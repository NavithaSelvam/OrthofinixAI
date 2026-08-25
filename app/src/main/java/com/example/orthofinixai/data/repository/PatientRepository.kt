package com.example.orthofinixai.data.repository

import android.content.Context
import android.util.Log
import com.example.orthofinixai.data.api.OrthofinixApi
import com.example.orthofinixai.data.api.PatientCreateRequest
import com.example.orthofinixai.data.local.OrthofinixDatabase
import com.example.orthofinixai.data.local.entity.PatientEntity
import com.example.orthofinixai.data.model.Patient
import com.example.orthofinixai.data.model.PatientCreate
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

class PatientRepository(private val context: Context) {

    private val patientDao by lazy { OrthofinixDatabase.getInstance(context).patientDao() }
    private val caseDao by lazy { OrthofinixDatabase.getInstance(context).caseDao() }
    private val firestore by lazy { FirebaseFirestore.getInstance() }
    private val authRepository by lazy { AuthRepository(context) }

    fun getPatients(): Flow<Result<List<Patient>>> = channelFlow {
        val userId = AuthRepository.getCurrentUserId()
        
        // 1. Observe local Room DB
        val localJob = launch(Dispatchers.IO) {
            try {
                patientDao.getPatientsForUser(userId).collect { entities ->
                    val sourceEntities = if (entities.isEmpty()) patientDao.getAllPatientsList() else entities
                    val mapped = sourceEntities.map { it.toPatient() }
                    send(Result.success(mapped))
                }
            } catch (e: kotlinx.coroutines.CancellationException) {
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "Error collecting local patients", e)
            }
        }

        // 2. Fetch remote patients from Backend API & Firestore
        launch(Dispatchers.IO) {
            try {
                // A. Try Backend API
                try {
                    val token = authRepository.getUserIdToken()
                    if (!token.isNullOrEmpty()) {
                        val api = OrthofinixApi.create()
                        val apiPatients = api.getPatients("Bearer $token")
                        apiPatients.forEach { bp ->
                            val entity = PatientEntity(
                                id = bp.id,
                                userId = bp.doctorId ?: userId,
                                name = bp.name,
                                age = estimateAge(bp.dateOfBirth ?: ""),
                                gender = bp.gender ?: "Unknown",
                                phone = bp.contactInfo ?: "",
                                notes = "",
                                createdAt = System.currentTimeMillis()
                            )
                            patientDao.insertPatient(entity)
                        }
                    }
                } catch (e: Exception) {
                    Log.w(TAG, "Notice fetching patients from API: ${e.message}")
                }

                // B. Fetch Firestore 'patients' collection for current user
                try {
                    if (userId.isNotEmpty() && userId != "anonymous") {
                        val fetchedDocs = mutableMapOf<String, com.google.firebase.firestore.DocumentSnapshot>()
                        for (field in listOf("doctor_id", "doctorId")) {
                            try {
                                val snap = firestore.collection("patients").whereEqualTo(field, userId).get().await()
                                snap.documents.forEach { doc ->
                                    if (!fetchedDocs.containsKey(doc.id)) {
                                        fetchedDocs[doc.id] = doc
                                    }
                                }
                            } catch (_: Exception) {}
                        }
                        fetchedDocs.values.forEach { doc ->
                            val pId = doc.id
                            val name = doc.getString("name") 
                                ?: doc.getString("patient_name") 
                                ?: doc.getString("patientName") 
                                ?: "Unknown Patient"
                            val dob = doc.getString("date_of_birth") 
                                ?: doc.getString("dateOfBirth") 
                                ?: doc.getString("dob") 
                                ?: ""
                            val gender = doc.getString("gender") ?: "Unknown"
                            val phone = doc.getString("phone") ?: doc.getString("contact_info") ?: ""
                            val notes = doc.getString("notes") ?: ""
                            val docUid = doc.getString("doctor_id") ?: doc.getString("doctorId") ?: userId

                            val entity = PatientEntity(
                                id = pId,
                                userId = docUid,
                                name = name,
                                age = estimateAge(dob),
                                gender = gender,
                                phone = phone,
                                notes = notes,
                                createdAt = doc.getLong("createdAt") ?: System.currentTimeMillis()
                            )
                            patientDao.insertPatient(entity)
                        }
                    }
                } catch (e: Exception) {
                    Log.w(TAG, "Notice fetching Firestore patients: ${e.message}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error in remote patients fetch", e)
            }
        }

        // 3. Real-time Firestore direct snapshot listener on root 'patients' collection
        val listeners = mutableListOf<ListenerRegistration>()
        try {
            val userEmail = authRepository.getCurrentUserEmail()
            val handlePatientSnapshot = com.google.firebase.firestore.EventListener<com.google.firebase.firestore.QuerySnapshot> { snapshot, error ->
                if (error != null) {
                    Log.e("FIRESTORE_ERROR", "Patients listen failed with code: ${error.code}", error)
                } else if (snapshot != null) {
                    Log.d("FIRESTORE_DEBUG", "Received ${snapshot.size()} patients from Firestore root")
                    launch(Dispatchers.IO) {
                        try {
                            for (change in snapshot.documentChanges) {
                                val doc = change.document
                                if (change.type == com.google.firebase.firestore.DocumentChange.Type.REMOVED) {
                                    patientDao.deletePatientById(doc.id)
                                } else {
                                    val pId = doc.id
                                    val name = doc.getString("name") ?: doc.getString("patient_name") ?: doc.getString("patientName") ?: "Patient"
                                    val dob = doc.getString("date_of_birth") ?: doc.getString("dateOfBirth") ?: doc.getString("dob") ?: ""
                                    val gender = doc.getString("gender") ?: "Unknown"
                                    val phone = doc.getString("phone") ?: ""
                                    val notes = doc.getString("notes") ?: ""
                                    val docUid = doc.getString("doctor_id") ?: doc.getString("doctorId") ?: doc.getString("user_id") ?: ""
                                    val docEmail = doc.getString("email") ?: doc.getString("doctor_email") ?: ""

                                    val matches = userId.isEmpty() || userId == "anonymous" || docUid == userId || 
                                                  (userEmail.isNotEmpty() && docEmail == userEmail) || docUid.isEmpty()

                                    if (matches) {
                                        val entity = PatientEntity(
                                            id = pId,
                                            userId = if (docUid.isNotEmpty()) docUid else userId,
                                            name = name,
                                            age = estimateAge(dob),
                                            gender = gender,
                                            phone = phone,
                                            notes = notes,
                                            createdAt = doc.getLong("createdAt") ?: System.currentTimeMillis()
                                        )
                                        patientDao.insertPatient(entity)
                                    }
                                }
                            }
                        } catch (ex: Exception) {
                            Log.w(TAG, "Error in patient snapshot sync: ${ex.message}")
                        }
                    }
                }
            }

            val rootPatListener = firestore.collection("patients").addSnapshotListener(handlePatientSnapshot)
            listeners.add(rootPatListener)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to register patients listener", e)
        }

        awaitClose {
            localJob.cancel()
            listeners.forEach { it.remove() }
        }
    }.flowOn(Dispatchers.IO)

    fun createPatient(patient: PatientCreate): Flow<Result<Patient>> = flow {
        val result = try {
            val userId = AuthRepository.getCurrentUserId()
            val cleanSlug = patient.name.lowercase(Locale.ROOT).replace(Regex("[^a-z0-9]"), "_")
            val id = "pat_${cleanSlug}_${System.currentTimeMillis()}"
            val nowIso = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US).apply {
                timeZone = TimeZone.getTimeZone("UTC")
            }.format(Date())
            val nowMs = System.currentTimeMillis()

            // 1. Insert into local SQLite Room DB
            val entity = PatientEntity(
                id = id,
                userId = userId,
                name = patient.name,
                age = estimateAge(patient.dateOfBirth),
                gender = patient.gender,
                phone = patient.phone,
                notes = patient.notes,
                createdAt = nowMs
            )
            patientDao.insertPatient(entity)

            // 2. Save to Firestore 'patients' collection
            try {
                val firestoreMap = hashMapOf<String, Any>(
                    "id" to id,
                    "name" to patient.name,
                    "patient_name" to patient.name,
                    "patientName" to patient.name,
                    "date_of_birth" to patient.dateOfBirth,
                    "dateOfBirth" to patient.dateOfBirth,
                    "dob" to patient.dateOfBirth,
                    "gender" to patient.gender,
                    "phone" to patient.phone,
                    "email" to patient.email,
                    "doctor_id" to userId,
                    "doctorId" to userId,
                    "doctor_name" to patient.doctorName,
                    "doctorName" to patient.doctorName,
                    "hospital" to patient.hospital,
                    "diagnosis" to patient.diagnosis,
                    "treatment_date" to patient.treatmentDate,
                    "treatmentDate" to patient.treatmentDate,
                    "notes" to patient.notes,
                    "created_at" to nowIso,
                    "createdAt" to nowMs,
                    "updated_at" to nowIso,
                    "updatedAt" to nowMs
                )
                firestore.collection("patients").document(id).set(firestoreMap).await()
            } catch (fsErr: Exception) {
                Log.w(TAG, "Notice saving patient to Firestore: ${fsErr.message}")
            }

            // 3. Post to Backend API
            try {
                val token = authRepository.getUserIdToken()
                if (!token.isNullOrEmpty()) {
                    OrthofinixApi.create().createPatient(
                        "Bearer $token",
                        PatientCreateRequest(
                            name = patient.name,
                            dateOfBirth = patient.dateOfBirth,
                            gender = patient.gender,
                            contactInfo = patient.phone
                        )
                    )
                }
            } catch (apiErr: Exception) {
                Log.w(TAG, "Notice calling API createPatient: ${apiErr.message}")
            }

            val createdPatient = Patient(
                id = id,
                name = patient.name,
                dateOfBirth = patient.dateOfBirth,
                gender = patient.gender,
                phone = patient.phone,
                email = patient.email,
                doctorName = patient.doctorName,
                hospital = patient.hospital,
                diagnosis = patient.diagnosis,
                treatmentDate = patient.treatmentDate,
                notes = patient.notes,
                doctorId = userId,
                createdAt = entity.createdAt
            )
            Result.success(createdPatient)
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create patient", e)
            Result.failure(e)
        }
        emit(result)
    }.flowOn(Dispatchers.IO)

    private fun PatientEntity.toPatient() = Patient(
        id = id,
        name = name,
        age = age,
        gender = gender,
        phone = phone,
        notes = notes,
        createdAt = createdAt
    )

    private fun estimateAge(dob: String): Int {
        return try {
            val year = dob.split("/").lastOrNull()?.toIntOrNull() 
                ?: dob.split("-").firstOrNull()?.toIntOrNull() 
                ?: 2010
            (2026 - year).coerceIn(5, 80)
        } catch (e: Exception) { 25 }
    }

    suspend fun deletePatient(patientId: String) {
        val userId = AuthRepository.getCurrentUserId()
        try {
            patientDao.deletePatientById(patientId)
            patientDao.deletePatientByName(patientId)
            caseDao.deleteCaseById(patientId)
            caseDao.deleteCaseByName(patientId)

            // 1. Call Backend API
            try {
                val token = authRepository.getUserIdToken()
                if (!token.isNullOrEmpty()) {
                    OrthofinixApi.create().deletePatient("Bearer $token", patientId)
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice on API deletePatient: ${e.message}")
            }

            // 2. Delete from Firestore
            if (userId.isNotEmpty() && userId != "anonymous") {
                try {
                    firestore.collection("patients").document(patientId).delete().await()
                } catch (_: Exception) {}
            }
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to delete patient", e)
        }
    }

    companion object {
        private const val TAG = "PatientRepository"
    }
}
