package com.example.orthofinixai.data.repository

import android.content.Context
import android.net.Uri
import android.util.Log
import com.example.orthofinixai.data.SessionManager
import com.example.orthofinixai.data.api.OrthofinixApi
import com.example.orthofinixai.data.local.OrthofinixDatabase
import com.example.orthofinixai.data.local.entity.CaseEntity
import com.example.orthofinixai.data.local.entity.PatientEntity
import com.example.orthofinixai.data.model.AIReport
import com.example.orthofinixai.data.model.ClinicalReport
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.model.Patient
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import com.google.firebase.storage.FirebaseStorage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.tasks.await
import java.util.UUID

class CaseRepository(private val context: Context) {

    private val firestore = FirebaseFirestore.getInstance()
    private val storage = FirebaseStorage.getInstance()
    private val caseDao by lazy { OrthofinixDatabase.getInstance(context).caseDao() }
    private val patientDao by lazy { OrthofinixDatabase.getInstance(context).patientDao() }
    private val reportDao by lazy { OrthofinixDatabase.getInstance(context).reportDao() }
    private val authRepository by lazy { AuthRepository(context) }

    private fun userId(): String =
        com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid
            ?: SessionManager.currentUserId
            ?: AuthRepository.getCurrentUserId()

    fun markCaseAsDeletedLocally(caseId: String) {
        if (caseId.isEmpty()) return
        try {
            val prefs = context.getSharedPreferences("orthofinix_deletions", Context.MODE_PRIVATE)
            val current = prefs.getStringSet("deleted_cases", mutableSetOf())?.toMutableSet() ?: mutableSetOf()
            current.add(caseId)
            current.add(caseId.lowercase().trim())
            prefs.edit().putStringSet("deleted_cases", current).apply()
        } catch (_: Exception) {}
    }

    fun isCaseDeletedLocally(caseId: String): Boolean {
        if (caseId.isEmpty()) return false
        return try {
            val prefs = context.getSharedPreferences("orthofinix_deletions", Context.MODE_PRIVATE)
            val set = prefs.getStringSet("deleted_cases", emptySet()) ?: emptySet()
            set.contains(caseId)
        } catch (_: Exception) {
            false
        }
    }

    private var snapshotRegistration: com.google.firebase.firestore.ListenerRegistration? = null
    private var rootSnapshotRegistration: com.google.firebase.firestore.ListenerRegistration? = null

    fun startRealtimeSync(uid: String = userId()) {
        val effectiveUid = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid ?: uid
        if (effectiveUid.isEmpty() || effectiveUid == "anonymous") return

        try {
            snapshotRegistration?.remove()
            snapshotRegistration = firestore.collection("users")
                .document(effectiveUid)
                .collection("cases")
                .addSnapshotListener { snapshot, error ->
                    if (error != null) {
                        Log.w(TAG, "Firestore real-time listener notice: ${error.message}")
                        return@addSnapshotListener
                    }
                    if (snapshot != null) {
                        kotlinx.coroutines.CoroutineScope(Dispatchers.IO).launch {
                            for (change in snapshot.documentChanges) {
                                val doc = change.document
                                val caseId = doc.id
                                when (change.type) {
                                    com.google.firebase.firestore.DocumentChange.Type.REMOVED -> {
                                        markCaseAsDeletedLocally(caseId)
                                        caseDao.deleteCaseById(caseId)
                                        caseDao.deleteCase(effectiveUid, caseId)
                                    }
                                    com.google.firebase.firestore.DocumentChange.Type.ADDED,
                                    com.google.firebase.firestore.DocumentChange.Type.MODIFIED -> {
                                        if (!isCaseDeletedLocally(caseId)) {
                                            val sc = SavedCase.fromFirestoreDoc(doc)
                                            val caseEntity = CaseEntity(
                                                id = sc.id,
                                                userId = effectiveUid,
                                                patientId = sc.patientId,
                                                patientName = sc.patientName,
                                                title = "Assessment Finishing: ${sc.viewType.uppercase()}",
                                                viewType = sc.viewType,
                                                imagePath = sc.imagePath,
                                                reportJson = sc.clinicalDataJson,
                                                reportId = sc.id,
                                                confidenceScore = if (sc.confidenceScore > 1) sc.confidenceScore.toFloat() / 100f else sc.confidenceScore.toFloat(),
                                                aboScore = sc.aboScore.toFloat(),
                                                andrewsScore = sc.andrewsScore.toFloat(),
                                                status = "Analyzed",
                                                createdAt = sc.createdAt,
                                                updatedAt = sc.createdAt
                                            )
                                            val patientEntity = PatientEntity(
                                                id = sc.patientId,
                                                userId = effectiveUid,
                                                name = sc.patientName,
                                                age = 25,
                                                gender = "Unknown",
                                                phone = "",
                                                notes = "",
                                                createdAt = sc.createdAt
                                            )
                                            patientDao.insertPatient(patientEntity)
                                            caseDao.insertCase(caseEntity)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

            rootSnapshotRegistration?.remove()
            rootSnapshotRegistration = firestore.collection("cases")
                .whereEqualTo("user_id", effectiveUid)
                .addSnapshotListener { snapshot, error ->
                    if (error != null) {
                        return@addSnapshotListener
                    }
                    if (snapshot != null) {
                        kotlinx.coroutines.CoroutineScope(Dispatchers.IO).launch {
                            for (change in snapshot.documentChanges) {
                                val doc = change.document
                                val caseId = doc.id
                                when (change.type) {
                                    com.google.firebase.firestore.DocumentChange.Type.REMOVED -> {
                                        markCaseAsDeletedLocally(caseId)
                                        caseDao.deleteCaseById(caseId)
                                        caseDao.deleteCase(effectiveUid, caseId)
                                    }
                                    com.google.firebase.firestore.DocumentChange.Type.ADDED,
                                    com.google.firebase.firestore.DocumentChange.Type.MODIFIED -> {
                                        if (!isCaseDeletedLocally(caseId)) {
                                            val sc = SavedCase.fromFirestoreDoc(doc)
                                            val caseEntity = CaseEntity(
                                                id = sc.id,
                                                userId = effectiveUid,
                                                patientId = sc.patientId,
                                                patientName = sc.patientName,
                                                title = "Assessment Finishing: ${sc.viewType.uppercase()}",
                                                viewType = sc.viewType,
                                                imagePath = sc.imagePath,
                                                reportJson = sc.clinicalDataJson,
                                                reportId = sc.id,
                                                confidenceScore = if (sc.confidenceScore > 1) sc.confidenceScore.toFloat() / 100f else sc.confidenceScore.toFloat(),
                                                aboScore = sc.aboScore.toFloat(),
                                                andrewsScore = sc.andrewsScore.toFloat(),
                                                status = "Analyzed",
                                                createdAt = sc.createdAt,
                                                updatedAt = sc.createdAt
                                            )
                                            val patientEntity = PatientEntity(
                                                id = sc.patientId,
                                                userId = effectiveUid,
                                                name = sc.patientName,
                                                age = 25,
                                                gender = "Unknown",
                                                phone = "",
                                                notes = "",
                                                createdAt = sc.createdAt
                                            )
                                            patientDao.insertPatient(patientEntity)
                                            caseDao.insertCase(caseEntity)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
        } catch (e: Exception) {
            Log.w(TAG, "Failed to start real-time sync listener: ${e.message}")
        }
    }

    fun getCasesFlow(uid: String = userId()): Flow<List<SavedCase>> {
        val effectiveUid = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid ?: uid
        startRealtimeSync(effectiveUid)
        return caseDao.getAllCasesFlow().map { entities ->
            val activeUid = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid ?: effectiveUid
            entities.filter {
                activeUid.isEmpty() || activeUid == "anonymous" || it.userId == activeUid || it.userId.isEmpty() || it.userId == "anonymous"
            }.map { entity ->
                val patientEntity = patientDao.getPatient(activeUid, entity.patientId) ?: patientDao.getPatientById(entity.patientId)
                entity.toSavedCase(patientEntity)
            }
        }.flowOn(Dispatchers.IO)
    }

    fun observeCases(): Flow<List<SavedCase>> = getCasesFlow()

    suspend fun syncCasesFromCloud(uid: String = userId()) {
        withContext(Dispatchers.IO) {
            val effectiveUid = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid ?: uid
            val currentUserEmail = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.email ?: ""
            if (effectiveUid.isEmpty() || effectiveUid == "anonymous") return@withContext

            val validRemoteIds = mutableSetOf<String>()
            val newEntities = mutableListOf<CaseEntity>()
            val newPatients = mutableListOf<PatientEntity>()

            // 1. Direct Firestore user subcollection fetch: users/{uid}/cases
            try {
                val subSnap = firestore.collection("users").document(effectiveUid).collection("cases").get().await()
                for (doc in subSnap.documents) {
                    if (!isCaseDeletedLocally(doc.id)) {
                        val sc = SavedCase.fromFirestoreDoc(doc)
                        validRemoteIds.add(sc.id)
                        newEntities.add(
                            CaseEntity(
                                id = sc.id,
                                userId = effectiveUid,
                                patientId = sc.patientId,
                                patientName = sc.patientName,
                                title = "Assessment Finishing: ${sc.viewType.uppercase()}",
                                viewType = sc.viewType,
                                imagePath = sc.imagePath,
                                reportJson = sc.clinicalDataJson,
                                reportId = sc.id,
                                confidenceScore = if (sc.confidenceScore > 1) sc.confidenceScore.toFloat() / 100f else sc.confidenceScore.toFloat(),
                                aboScore = sc.aboScore.toFloat(),
                                andrewsScore = sc.andrewsScore.toFloat(),
                                status = "Analyzed",
                                createdAt = sc.createdAt,
                                updatedAt = sc.createdAt
                            )
                        )
                        newPatients.add(
                            PatientEntity(
                                id = sc.patientId,
                                userId = effectiveUid,
                                name = sc.patientName,
                                age = 25,
                                gender = "Unknown",
                                phone = "",
                                notes = "",
                                createdAt = sc.createdAt
                            )
                        )
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice on Firestore subcollection sync: ${e.message}")
            }

            // 2. Direct Firestore root cases query by UID and email fields (Failsafe)
            try {
                val collectionsToQuery = listOf("cases", "analyses", "analysis_reports")
                for (colName in collectionsToQuery) {
                    val queries = mutableListOf<com.google.firebase.firestore.Query>()
                    queries.add(firestore.collection(colName).whereEqualTo("user_id", effectiveUid))
                    queries.add(firestore.collection(colName).whereEqualTo("doctor_id", effectiveUid))
                    queries.add(firestore.collection(colName).whereEqualTo("userId", effectiveUid))
                    queries.add(firestore.collection(colName).whereEqualTo("doctorId", effectiveUid))
                    if (currentUserEmail.isNotEmpty()) {
                        queries.add(firestore.collection(colName).whereEqualTo("doctor_email", currentUserEmail))
                        queries.add(firestore.collection(colName).whereEqualTo("email", currentUserEmail))
                    }

                    for (q in queries) {
                        try {
                            val rootSnap = q.get().await()
                            for (doc in rootSnap.documents) {
                                if (!isCaseDeletedLocally(doc.id) && !validRemoteIds.contains(doc.id)) {
                                    val sc = SavedCase.fromFirestoreDoc(doc)
                                    validRemoteIds.add(sc.id)
                                    newEntities.add(
                                        CaseEntity(
                                            id = sc.id,
                                            userId = effectiveUid,
                                            patientId = sc.patientId,
                                            patientName = sc.patientName,
                                            title = "Assessment Finishing: ${sc.viewType.uppercase()}",
                                            viewType = sc.viewType,
                                            imagePath = sc.imagePath,
                                            reportJson = sc.clinicalDataJson,
                                            reportId = sc.id,
                                            confidenceScore = if (sc.confidenceScore > 1) sc.confidenceScore.toFloat() / 100f else sc.confidenceScore.toFloat(),
                                            aboScore = sc.aboScore.toFloat(),
                                            andrewsScore = sc.andrewsScore.toFloat(),
                                            status = "Analyzed",
                                            createdAt = sc.createdAt,
                                            updatedAt = sc.createdAt
                                        )
                                    )
                                    newPatients.add(
                                        PatientEntity(
                                            id = sc.patientId,
                                            userId = effectiveUid,
                                            name = sc.patientName,
                                            age = 25,
                                            gender = "Unknown",
                                            phone = "",
                                            notes = "",
                                            createdAt = sc.createdAt
                                        )
                                    )
                                }
                            }
                        } catch (_: Exception) {}
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice on Firestore root cases sync: ${e.message}")
            }

            // 3. Backend API History Fetch
            try {
                val token = authRepository.getUserIdToken()
                if (!token.isNullOrEmpty()) {
                    val api = OrthofinixApi.create()
                    val apiCases = api.getHistory("Bearer $token")
                    val caseIds = apiCases.map { it.id }
                    Log.i("ORTHOFINIX_STAGE", "[ANDROID HISTORY]\nUID: $effectiveUid\nnumber of cases returned: ${apiCases.size}\ncase IDs returned: $caseIds")
                    apiCases.forEach { item ->
                        if (!validRemoteIds.contains(item.id)) {
                            validRemoteIds.add(item.id)
                            val score = item.finishingScore ?: (item.overallScore ?: 0f)
                            var parsedTime = System.currentTimeMillis()
                            val createdStr = item.createdAt
                            if (!createdStr.isNullOrEmpty()) {
                                try {
                                    val sdf = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", java.util.Locale.US).apply {
                                        timeZone = java.util.TimeZone.getTimeZone("UTC")
                                    }
                                    parsedTime = sdf.parse(createdStr.take(19))?.time ?: System.currentTimeMillis()
                                } catch (_: Exception) {}
                            }
                            newEntities.add(
                                CaseEntity(
                                    id = item.id,
                                    userId = effectiveUid,
                                    patientId = item.id,
                                    patientName = item.patientName ?: "Patient",
                                    title = "Assessment Finishing: OPG",
                                    viewType = "opg",
                                    imagePath = item.imageUrl ?: "",
                                    reportJson = "",
                                    reportId = item.id,
                                    confidenceScore = item.confidenceScore ?: 0.95f,
                                    aboScore = score,
                                    andrewsScore = score,
                                    status = "Analyzed",
                                    createdAt = parsedTime,
                                    updatedAt = parsedTime
                                )
                            )
                            newPatients.add(
                                PatientEntity(
                                    id = item.id,
                                    userId = effectiveUid,
                                    name = item.patientName ?: "Patient",
                                    age = 25,
                                    gender = "Unknown",
                                    phone = "",
                                    notes = "",
                                    createdAt = parsedTime
                                )
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice on API history sync: ${e.message}")
            }

            if (newEntities.isNotEmpty()) {
                caseDao.insertAll(newEntities)
                patientDao.insertAll(newPatients)
                caseDao.deleteCasesNotInList(effectiveUid, validRemoteIds.toList())
            } else if (validRemoteIds.isEmpty()) {
                caseDao.deleteCasesForUser(effectiveUid)
            }
        }
    }

    suspend fun saveFullCase(
        patient: Patient,
        imageUri: Uri?,
        imageBytes: ByteArray?,
        clinical: ClinicalReport,
        aiReport: AIReport
    ) {
        val uid = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid ?: userId()
        val currentUserEmail = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.email ?: ""
        val caseId = aiReport.case_id
        
        var downloadUrl = ""
        
        // Upload to Firebase Storage
        try {
            if (imageBytes != null && imageBytes.isNotEmpty()) {
                val ref = storage.reference.child("users/$uid/cases/$caseId/image.jpg")
                ref.putBytes(imageBytes).await()
                downloadUrl = ref.downloadUrl.await().toString()
            } else if (imageUri != null) {
                val storageRef = storage.reference.child("users/$uid/cases/$caseId/image.jpg")
                storageRef.putFile(imageUri).await()
                downloadUrl = storageRef.downloadUrl.await().toString()
            }
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to upload image", e)
        }

        val effectiveImageUrl = downloadUrl.ifEmpty { patient.imageUrls.firstOrNull() ?: "" }

        val overallFinishingScore = if (clinical.overallScore > 0f) clinical.overallScore else ((clinical.andrewsScore + clinical.archSymmetryScore + clinical.rootAngulationScore) / 3f)
        val overallInt = Math.round(overallFinishingScore)
        val aboInt = Math.round(clinical.aboScore)
        val andrewsInt = Math.round(clinical.andrewsScore)
        val alignInt = Math.round(clinical.archSymmetryScore)
        val rootInt = Math.round(clinical.rootAngulationScore)

        // Save to Room DB first
        try {
            val patientEntity = PatientEntity(
                id = patient.id,
                userId = uid,
                name = patient.name,
                age = patient.age,
                gender = patient.gender,
                phone = patient.phone,
                notes = patient.notes,
                createdAt = patient.createdAt
            )
            patientDao.insertPatient(patientEntity)
            
            val caseEntity = CaseEntity(
                id = caseId,
                userId = uid,
                patientId = patient.id,
                patientName = patient.name,
                title = "Assessment Finishing: ${clinical.viewType.uppercase()}",
                viewType = clinical.viewType,
                imagePath = effectiveImageUrl,
                reportJson = clinical.toJson(),
                reportId = caseId,
                confidenceScore = clinical.confidenceScore,
                aboScore = aboInt.toFloat(),
                andrewsScore = andrewsInt.toFloat(),
                status = "Analyzed",
                createdAt = System.currentTimeMillis(),
                updatedAt = System.currentTimeMillis()
            )
            caseDao.insertCase(caseEntity)
            Log.d(TAG, "Successfully saved case and patient to local Room DB")
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to save case locally to Room DB", e)
        }
        
        // Save to Firestore collections
        try {
            val isoFormat = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", java.util.Locale.US).apply {
                timeZone = java.util.TimeZone.getTimeZone("UTC")
            }
            val nowIso = isoFormat.format(java.util.Date())
            val nowMs = System.currentTimeMillis()

            val richCaseMap = hashMapOf<String, Any>(
                "id" to caseId,
                "case_id" to caseId,
                "caseId" to caseId,
                "patient_id" to patient.id,
                "patientId" to patient.id,
                "patient_name" to patient.name,
                "patientName" to patient.name,
                "dob" to patient.dateOfBirth,
                "date_of_birth" to patient.dateOfBirth,
                "dateOfBirth" to patient.dateOfBirth,
                "gender" to patient.gender,
                "user_id" to uid,
                "uid" to uid,
                "doctor_id" to uid,
                "doctorId" to uid,
                "email" to currentUserEmail,
                "doctor_email" to currentUserEmail,
                "doctor_name" to patient.doctorName,
                "doctorName" to patient.doctorName,
                "image_url" to effectiveImageUrl,
                "imagePath" to effectiveImageUrl,
                "storage_url" to effectiveImageUrl,
                "view_type" to clinical.viewType,
                "viewType" to clinical.viewType,
                "status" to "completed",
                "overall_score" to overallInt,
                "overallScore" to overallInt,
                "finishing_score" to overallInt,
                "overall_finishing_score" to overallInt,
                "alignment_score" to alignInt,
                "arch_symmetry_score" to alignInt,
                "archSymmetryScore" to alignInt,
                "confidence_score" to clinical.confidenceScore,
                "confidenceScore" to clinical.confidenceScore,
                "midline_deviation_mm" to clinical.midlineDiscrepancyMm,
                "midlineDiscrepancyMm" to clinical.midlineDiscrepancyMm,
                "overjet_mm" to clinical.overjetMm,
                "overjetMm" to clinical.overjetMm,
                "overbite_percent" to clinical.overbitePercent,
                "overbitePercent" to clinical.overbitePercent,
                "abo_score" to aboInt,
                "aboScore" to aboInt,
                "andrews_score" to andrewsInt,
                "andrewsScore" to andrewsInt,
                "root_angulation_score" to rootInt,
                "rootAngulationScore" to rootInt,
                "prediction" to "Orthodontic finishing analysis completed. Alignment: $alignInt%, Andrews: $andrewsInt%, Root Angulation: $rootInt%.",
                "recommendations" to clinical.recommendations,
                "hasReport" to true,
                "clinicalDataJson" to clinical.toJson(),
                "reportJson" to clinical.toJson(),
                "patientProfile" to patient,
                "created_at" to nowIso,
                "createdAt" to nowMs,
                "updated_at" to nowIso,
                "updatedAt" to nowMs
            )

            // 1. Save in user's subcollection
            if (uid.isNotEmpty() && uid != "anonymous") {
                firestore.collection("users")
                    .document(uid)
                    .collection("cases")
                    .document(caseId)
                    .set(richCaseMap)
                    .await()

                try {
                    firestore.collection("users")
                        .document(uid)
                        .update("total_cases", com.google.firebase.firestore.FieldValue.increment(1))
                        .await()
                } catch (_: Exception) {}
            }

            // 2. Save in top-level cases collection
            firestore.collection("cases")
                .document(caseId)
                .set(richCaseMap)
                .await()

            // 3. Save in top-level analyses collection
            firestore.collection("analyses")
                .document(caseId)
                .set(richCaseMap)
                .await()

            // 4. Save in top-level analysis_reports collection
            firestore.collection("analysis_reports")
                .document(caseId)
                .set(richCaseMap)
                .await()

            // 5. Save in top-level patients collection
            val richPatientMap = hashMapOf<String, Any>(
                "id" to patient.id,
                "name" to patient.name,
                "patient_name" to patient.name,
                "patientName" to patient.name,
                "date_of_birth" to patient.dateOfBirth,
                "dateOfBirth" to patient.dateOfBirth,
                "dob" to patient.dateOfBirth,
                "gender" to patient.gender,
                "phone" to patient.phone,
                "email" to patient.email,
                "doctor_id" to uid,
                "doctorId" to uid,
                "doctor_name" to patient.doctorName,
                "doctorName" to patient.doctorName,
                "hospital" to patient.hospital,
                "diagnosis" to patient.diagnosis,
                "treatment_date" to patient.treatmentDate,
                "treatmentDate" to patient.treatmentDate,
                "notes" to patient.notes,
                "last_case_id" to caseId,
                "lastCaseId" to caseId,
                "last_score" to overallFinishingScore,
                "lastScore" to overallFinishingScore,
                "last_analysis_at" to nowIso,
                "created_at" to nowIso,
                "createdAt" to nowMs,
                "updated_at" to nowIso,
                "updatedAt" to nowMs
            )
            firestore.collection("patients")
                .document(patient.id)
                .set(richPatientMap)
                .await()

            // 6. Save in top-level images collection
            if (effectiveImageUrl.isNotEmpty()) {
                val imageMap = hashMapOf(
                    "id" to caseId,
                    "case_id" to caseId,
                    "caseId" to caseId,
                    "user_id" to uid,
                    "doctor_id" to uid,
                    "patient_name" to patient.name,
                    "patientName" to patient.name,
                    "image_url" to effectiveImageUrl,
                    "storage_url" to effectiveImageUrl,
                    "view_type" to clinical.viewType,
                    "uploaded_at" to nowIso,
                    "createdAt" to nowMs
                )
                firestore.collection("images")
                    .document(caseId)
                    .set(imageMap)
                    .await()
            }

            // 7. Update user summary
            if (uid.isNotEmpty() && uid != "anonymous") {
                firestore.collection("users").document(uid).set(
                    hashMapOf(
                        "last_analysis_at" to nowIso,
                        "last_case_id" to caseId,
                        "last_active" to nowIso,
                        "updated_at" to nowIso
                    ),
                    com.google.firebase.firestore.SetOptions.merge()
                ).await()
            }

        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to save case to Firestore", e)
        }
    }
    
    suspend fun getClinicalReport(caseId: String): ClinicalReport? {
        val uid = userId()
        try {
            // 1. Try local SQLite Room DB
            val localCase = (if (uid.isNotEmpty()) caseDao.getCase(uid, caseId) else null) ?: caseDao.getCaseById(caseId)
            if (localCase != null && localCase.reportJson.isNotEmpty()) {
                val cl = ClinicalReport.fromJson(localCase.reportJson)
                if (cl != null) return cl
            }

            // 2. Try Backend API
            try {
                val token = authRepository.getUserIdToken()
                if (!token.isNullOrEmpty()) {
                    val api = OrthofinixApi.create()
                    val resp = api.getReport("Bearer $token", caseId)
                    Log.i("ORTHOFINIX_STAGE", "[ANDROID REPORT]\nUID: $uid\ncase ID: $caseId\nHTTP response: 200 OK")
                    val reportJson = resp.metrics?.let { com.google.gson.Gson().toJson(it) } ?: ""
                    val clinical = ClinicalReport(
                        viewType = resp.view_type,
                        confidenceScore = resp.confidence_score,
                        aboScore = resp.abo_score,
                        archSymmetryScore = resp.alignment_score,
                        rootAngulationScore = resp.root_angulation_score,
                        andrewsScore = resp.andrews_score,
                        overjetMm = resp.overjet_mm,
                        overbitePercent = resp.overbite_percent,
                        midlineDiscrepancyMm = resp.midline_deviation_mm,
                        recommendations = resp.recommendations
                    )
                    return clinical
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice fetching report from API: ${e.message}")
            }

            // 3. Try Firestore: cases, analysis_reports, analyses, users/{uid}/cases
            var doc: com.google.firebase.firestore.DocumentSnapshot? = null
            try {
                doc = firestore.collection("cases").document(caseId).get().await()
                if (!doc.exists()) doc = firestore.collection("analysis_reports").document(caseId).get().await()
                if (!doc.exists()) doc = firestore.collection("analyses").document(caseId).get().await()
                if (!doc.exists() && uid.isNotEmpty()) {
                    doc = firestore.collection("users").document(uid).collection("cases").document(caseId).get().await()
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice fetching report from Firestore: ${e.message}")
            }

            if (doc != null && doc.exists()) {
                val cJson = doc.getString("clinicalDataJson") ?: doc.getString("reportJson") ?: ""
                if (cJson.isNotEmpty()) {
                    val cl = ClinicalReport.fromJson(cJson)
                    if (cl != null) return cl
                }
                val sc = SavedCase.fromFirestoreDoc(doc)
                val overjetVal = (doc.get("overjet_mm") as? Number)?.toFloat() ?: (doc.getString("overjet_mm")?.toFloatOrNull() ?: 2.4f)
                val overbiteVal = (doc.get("overbite_percent") as? Number)?.toFloat() ?: (doc.getString("overbite_percent")?.toFloatOrNull() ?: 25.0f)
                val midlineVal = (doc.get("midline_deviation_mm") as? Number)?.toFloat() ?: (doc.getString("midline_deviation_mm")?.toFloatOrNull() ?: 0.0f)
                return ClinicalReport(
                    viewType = sc.viewType,
                    overallScore = sc.overallScore.toFloat(),
                    confidenceScore = if (sc.confidenceScore > 1) sc.confidenceScore.toFloat() / 100f else sc.confidenceScore.toFloat(),
                    aboScore = sc.aboScore.toFloat(),
                    archSymmetryScore = sc.alignmentScore.toFloat(),
                    alignmentScore = sc.alignmentScore.toFloat(),
                    rootAngulationScore = sc.rootAngulationScore.toFloat(),
                    andrewsScore = sc.andrewsScore.toFloat(),
                    overjetMm = overjetVal,
                    overbitePercent = overbiteVal,
                    midlineDiscrepancyMm = midlineVal,
                    recommendations = (doc.get("recommendations") as? List<*>)?.mapNotNull { it?.toString() } ?: emptyList()
                )
            }
            return null
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get report", e)
            return null
        }
    }

    suspend fun getSavedCaseSync(caseId: String): SavedCase? {
        val uid = userId()
        try {
            val localCase = (if (uid.isNotEmpty()) caseDao.getCase(uid, caseId) else null) ?: caseDao.getCaseById(caseId)
            if (localCase != null) {
                val patientEntity = (if (uid.isNotEmpty()) patientDao.getPatient(uid, localCase.patientId) else null) ?: patientDao.getPatientById(localCase.patientId)
                return localCase.toSavedCase(patientEntity)
            }

            var doc: com.google.firebase.firestore.DocumentSnapshot? = null
            try {
                doc = firestore.collection("cases").document(caseId).get().await()
                if (!doc.exists()) doc = firestore.collection("analysis_reports").document(caseId).get().await()
                if (!doc.exists()) doc = firestore.collection("analyses").document(caseId).get().await()
                if (!doc.exists() && uid.isNotEmpty()) {
                    doc = firestore.collection("users").document(uid).collection("cases").document(caseId).get().await()
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice fetching saved case: ${e.message}")
            }

            if (doc != null && doc.exists()) {
                return SavedCase.fromFirestoreDoc(doc)
            }
            return null
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get saved case", e)
            return null
        }
    }

    suspend fun deleteCase(caseId: String) {
        val uid = userId()
        try {
            markCaseAsDeletedLocally(caseId)

            // 1. Delete from local SQLite Room DB
            caseDao.deleteCaseById(caseId)
            caseDao.deleteCaseByName(caseId)
            caseDao.deleteCase(uid, caseId)
            try {
                patientDao.deletePatientById(caseId)
                patientDao.deletePatientByName(caseId)
            } catch (_: Exception) {}
            try {
                reportDao.deleteByCaseId(caseId)
                reportDao.deleteByCase(uid, caseId)
            } catch (_: Exception) {}
            
            // 2. Delete from Backend API
            try {
                val token = authRepository.getUserIdToken()
                if (!token.isNullOrEmpty()) {
                    try {
                        OrthofinixApi.create().deleteAnalysis("Bearer $token", caseId)
                    } catch (delErr: Exception) {
                        try {
                            OrthofinixApi.create().deleteAnalysisPost("Bearer $token", caseId)
                        } catch (_: Exception) {}
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice on API delete: ${e.message}")
            }

            // 3. Delete from Firestore collections across all candidate IDs
            val candidateIds = mutableSetOf(caseId)
            try {
                if (uid.isNotEmpty() && uid != "anonymous") {
                    val allSub = firestore.collection("users").document(uid).collection("cases").get().await()
                    for (d in allSub.documents) {
                        val dId = d.id
                        val dCaseId = d.getString("case_id") ?: d.getString("caseId") ?: ""
                        val dObjId = d.getString("id") ?: ""
                        if (dId == caseId || dCaseId == caseId || dObjId == caseId) {
                            candidateIds.add(dId)
                            if (dCaseId.isNotEmpty()) candidateIds.add(dCaseId)
                            if (dObjId.isNotEmpty()) candidateIds.add(dObjId)
                            try { d.reference.delete().await() } catch (_: Exception) {}
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Notice on Firestore subcollection query delete: ${e.message}")
            }

            // Also query root 'cases' where doctor_id == uid to discover and clean matching docs
            try {
                if (uid.isNotEmpty() && uid != "anonymous") {
                    val rootSnap = firestore.collection("cases").whereEqualTo("doctor_id", uid).get().await()
                    for (d in rootSnap.documents) {
                        val dId = d.id
                        val dCaseId = d.getString("case_id") ?: d.getString("caseId") ?: ""
                        val dObjId = d.getString("id") ?: ""
                        if (candidateIds.contains(dId) || candidateIds.contains(dCaseId) || candidateIds.contains(dObjId)) {
                            candidateIds.add(dId)
                            try { d.reference.delete().await() } catch (_: Exception) {}
                        }
                    }
                }
            } catch (_: Exception) {}

            for (cid in candidateIds) {
                markCaseAsDeletedLocally(cid)
                try { caseDao.deleteCaseById(cid) } catch (_: Exception) {}
                try { caseDao.deleteCase(uid, cid) } catch (_: Exception) {}
                try { firestore.collection("cases").document(cid).delete().await() } catch (_: Exception) {}
                try { firestore.collection("analyses").document(cid).delete().await() } catch (_: Exception) {}
                try { firestore.collection("analysis_reports").document(cid).delete().await() } catch (_: Exception) {}
                try { firestore.collection("images").document(cid).delete().await() } catch (_: Exception) {}
                try { firestore.collection("images").document("img_$cid").delete().await() } catch (_: Exception) {}
                if (uid.isNotEmpty() && uid != "anonymous") {
                    try { firestore.collection("users").document(uid).collection("cases").document(cid).delete().await() } catch (_: Exception) {}
                }
            }

            // 4. Delete image from Storage
            try {
                storage.reference.child("users/$uid/cases/$caseId/image.jpg").delete().await()
            } catch (e: Exception) {}
        } catch (e: kotlinx.coroutines.CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.e(TAG, "Failed to delete case", e)
        }
    }

    private fun CaseEntity.toSavedCase(patientEntity: PatientEntity?): SavedCase {
        val patientObj = patientEntity?.let {
            Patient(
                id = it.id,
                name = it.name,
                age = it.age,
                dateOfBirth = "",
                gender = it.gender,
                phone = it.phone,
                email = "",
                doctorName = "",
                hospital = "",
                diagnosis = "",
                treatmentDate = "",
                notes = it.notes,
                imageUrls = if (imagePath.isNotEmpty()) listOf(imagePath) else emptyList(),
                doctorId = it.userId,
                createdAt = it.createdAt
            )
        }
        val score = if (aboScore > 0f) aboScore.toInt() else (if (andrewsScore > 0f) andrewsScore.toInt() else 0)
        val confInt = if (confidenceScore <= 1.0f) (confidenceScore * 100).toInt() else confidenceScore.toInt()
        return SavedCase(
            id = id,
            caseId = id,
            userId = userId,
            patientId = patientId,
            patientName = patientName,
            doctorName = "",
            doctorId = userId,
            imageUrl = imagePath,
            imagePath = imagePath,
            viewType = viewType,
            confidenceScore = confInt,
            aboScore = aboScore.toInt(),
            andrewsScore = andrewsScore.toInt(),
            overallScore = score,
            finishingScore = score.toFloat(),
            overallFinishingScore = score.toFloat(),
            createdAt = createdAt,
            hasReport = reportJson.isNotEmpty(),
            clinicalDataJson = reportJson,
            patientProfile = patientObj
        )
    }

    companion object {
        private const val TAG = "CaseRepository"
    }
}
