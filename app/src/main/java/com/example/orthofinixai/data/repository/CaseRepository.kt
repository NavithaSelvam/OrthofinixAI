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
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.Flow
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
        SessionManager.currentUserId ?: AuthRepository.getCurrentUserId()

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
            set.contains(caseId) || set.contains(caseId.lowercase().trim())
        } catch (_: Exception) {
            false
        }
    }

    fun observeCases(): Flow<List<SavedCase>> = kotlinx.coroutines.flow.channelFlow {
        val uid = userId()
        
        // 1. Observe local Room DB cases and emit reactively
        val localJob = this@channelFlow.launch(Dispatchers.IO) {
            try {
                caseDao.getCasesForUser(uid).collect { entities ->
                    val sourceEntities = if (entities.isEmpty()) {
                        caseDao.getAllCasesList()
                    } else {
                        entities
                    }
                    val mapped = sourceEntities
                        .filter { 
                            !isCaseDeletedLocally(it.id) && 
                            !isCaseDeletedLocally(it.patientId) && 
                            !isCaseDeletedLocally(it.patientName)
                        }
                        .map { entity ->
                            val patientEntity = patientDao.getPatient(uid, entity.patientId) 
                                ?: patientDao.getPatientById(entity.patientId)
                            entity.toSavedCase(patientEntity)
                        }
                    send(mapped)
                }
            } catch (e: kotlinx.coroutines.CancellationException) {
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "Error collecting local cases", e)
            }
        }
        
        // 2. Fetch remote cases from Backend API & Firestore, sync to Room
        this@channelFlow.launch(Dispatchers.IO) {
            try {
                Log.d("AUTH_DEBUG", "Mobile UID: " + com.google.firebase.auth.FirebaseAuth.getInstance().currentUser?.uid)
                val validRemoteIds = mutableSetOf<String>()
                var apiSuccess = false

                // A. Authoritative Backend API History first
                try {
                    val token = authRepository.getUserIdToken()
                    if (!token.isNullOrEmpty()) {
                        val api = OrthofinixApi.create()
                        val apiCases = api.getHistory("Bearer $token")
                        apiSuccess = true
                        apiCases.forEach { item ->
                            if (!isCaseDeletedLocally(item.id) && !isCaseDeletedLocally(item.patientName ?: "")) {
                                val score = item.finishingScore ?: 0f
                                validRemoteIds.add(item.id)

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

                                val caseEntity = CaseEntity(
                                    id = item.id,
                                    userId = uid,
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
                                caseDao.insertCase(caseEntity)
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.w(TAG, "Notice on API history sync: ${e.message}")
                }

                // B. Query user's Firestore records across all UID variants
                val caseDocsMap = mutableMapOf<String, com.google.firebase.firestore.DocumentSnapshot>()

                if (uid.isNotEmpty() && uid != "anonymous") {
                    // Query user subcollection
                    try {
                        val userSnap = firestore.collection("users").document(uid).collection("cases").get().await()
                        userSnap.documents.forEach { doc ->
                            caseDocsMap[doc.id] = doc
                            validRemoteIds.add(doc.id)
                        }
                    } catch (_: Exception) {}

                    // Query root 'cases' where doctor_id == uid
                    try {
                        val docSnap = firestore.collection("cases").whereEqualTo("doctor_id", uid).get().await()
                        docSnap.documents.forEach { doc ->
                            if (!caseDocsMap.containsKey(doc.id)) {
                                caseDocsMap[doc.id] = doc
                                validRemoteIds.add(doc.id)
                            }
                        }
                    } catch (_: Exception) {}

                    // Query root 'cases' where doctorId == uid
                    try {
                        val docIdSnap = firestore.collection("cases").whereEqualTo("doctorId", uid).get().await()
                        docIdSnap.documents.forEach { doc ->
                            if (!caseDocsMap.containsKey(doc.id)) {
                                caseDocsMap[doc.id] = doc
                                validRemoteIds.add(doc.id)
                            }
                        }
                    } catch (_: Exception) {}

                    // Query root 'cases' where user_id == uid
                    try {
                        val userColSnap = firestore.collection("cases").whereEqualTo("user_id", uid).get().await()
                        userColSnap.documents.forEach { doc ->
                            if (!caseDocsMap.containsKey(doc.id)) {
                                caseDocsMap[doc.id] = doc
                                validRemoteIds.add(doc.id)
                            }
                        }
                    } catch (_: Exception) {}

                    val userEmail = authRepository.getCurrentUserEmail()
                    if (userEmail.isNotEmpty()) {
                        try {
                            val emailSnap = firestore.collection("cases").whereEqualTo("doctor_email", userEmail).get().await()
                            emailSnap.documents.forEach { doc ->
                                if (!caseDocsMap.containsKey(doc.id)) {
                                    caseDocsMap[doc.id] = doc
                                    validRemoteIds.add(doc.id)
                                }
                            }
                        } catch (_: Exception) {}
                    }

                    // Query root 'analysis_reports' and 'analyses'
                    for (collName in listOf("analysis_reports", "analyses")) {
                        try {
                            val colSnap = firestore.collection(collName).whereEqualTo("doctor_id", uid).get().await()
                            colSnap.documents.forEach { doc ->
                                if (!caseDocsMap.containsKey(doc.id)) {
                                    caseDocsMap[doc.id] = doc
                                    validRemoteIds.add(doc.id)
                                }
                            }
                        } catch (_: Exception) {}
                        try {
                            val colSnap = firestore.collection(collName).whereEqualTo("user_id", uid).get().await()
                            colSnap.documents.forEach { doc ->
                                if (!caseDocsMap.containsKey(doc.id)) {
                                    caseDocsMap[doc.id] = doc
                                    validRemoteIds.add(doc.id)
                                }
                            }
                        } catch (_: Exception) {}
                    }
                }

                // Parse and persist remote cases to Room DB
                caseDocsMap.values.forEach { doc ->
                    val rc = SavedCase.fromFirestoreDoc(doc)
                    if (!isCaseDeletedLocally(rc.id) && !isCaseDeletedLocally(rc.patientName)) {
                        val caseEntity = CaseEntity(
                            id = rc.id,
                            userId = uid,
                            patientId = rc.patientId,
                            patientName = rc.patientName,
                            title = "Assessment Finishing: ${rc.viewType.uppercase()}",
                            viewType = rc.viewType,
                            imagePath = rc.imagePath,
                            reportJson = rc.clinicalDataJson,
                            reportId = rc.id,
                            confidenceScore = rc.confidenceScore,
                            aboScore = rc.aboScore,
                            andrewsScore = rc.andrewsScore,
                            status = "Analyzed",
                            createdAt = rc.createdAt,
                            updatedAt = rc.createdAt
                        )
                        caseDao.insertCase(caseEntity)
                        
                        val patientEntity = PatientEntity(
                            id = rc.patientId,
                            userId = uid,
                            name = rc.patientName,
                            age = 25,
                            gender = "Unknown",
                            phone = "",
                            notes = "",
                            createdAt = rc.createdAt
                        )
                        patientDao.insertPatient(patientEntity)
                    }
                }

                // Reconcile local Room DB: Clean table sync removing stale cases deleted remotely
                if (uid.isNotEmpty() && uid != "anonymous") {
                    val localList = caseDao.getAllCasesList()
                    for (localCase in localList) {
                        if (!validRemoteIds.contains(localCase.id) || isCaseDeletedLocally(localCase.id) || isCaseDeletedLocally(localCase.patientName)) {
                            caseDao.deleteCase(uid, localCase.id)
                            caseDao.deleteCaseById(localCase.id)
                        }
                    }
                }
            } catch (e: kotlinx.coroutines.CancellationException) {
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "Error fetching from remote sources", e)
            }
        }
        
        // 3. Listen to remote updates reactively for real-time synchronization
        val listeners = mutableListOf<ListenerRegistration>()
        try {
            val userEmail = authRepository.getCurrentUserEmail()

            // A. Primary direct listener on root 'cases' collection (No complex composite index required)
            val rootListener = firestore.collection("cases").addSnapshotListener { snapshot, error ->
                if (error != null) {
                    Log.e("FIRESTORE_ERROR", "Cases listen failed with code: ${error.code}", error)
                    android.os.Handler(android.os.Looper.getMainLooper()).post {
                        android.widget.Toast.makeText(context, "Sync Notice: ${error.message}", android.widget.Toast.LENGTH_SHORT).show()
                    }
                    return@addSnapshotListener
                }

                if (snapshot != null) {
                    Log.d("FIRESTORE_DEBUG", "Received ${snapshot.size()} cases from Firestore root")
                    this@channelFlow.launch(Dispatchers.IO) {
                        try {
                            for (change in snapshot.documentChanges) {
                                val doc = change.document
                                if (change.type == com.google.firebase.firestore.DocumentChange.Type.REMOVED) {
                                    caseDao.deleteCaseById(doc.id)
                                    caseDao.deleteCase(uid, doc.id)
                                } else {
                                    val rc = SavedCase.fromFirestoreDoc(doc)
                                    val docUid = doc.getString("user_id") ?: doc.getString("doctor_id") ?: doc.getString("doctorId") ?: rc.doctorId
                                    val docEmail = doc.getString("email") ?: doc.getString("doctor_email") ?: ""
                                    
                                    // Client-side isolation filter
                                    val matchesUser = uid.isEmpty() || uid == "anonymous" || docUid == uid || 
                                                      (userEmail.isNotEmpty() && docEmail == userEmail) || docUid.isEmpty()
                                    
                                    if (matchesUser && !isCaseDeletedLocally(rc.id) && !isCaseDeletedLocally(rc.patientName)) {
                                        val caseEntity = CaseEntity(
                                            id = rc.id,
                                            userId = if (docUid.isNotEmpty()) docUid else uid,
                                            patientId = rc.patientId,
                                            patientName = rc.patientName,
                                            title = "Assessment Finishing: ${rc.viewType.uppercase()}",
                                            viewType = rc.viewType,
                                            imagePath = rc.imagePath,
                                            reportJson = rc.clinicalDataJson,
                                            reportId = rc.id,
                                            confidenceScore = rc.confidenceScore,
                                            aboScore = rc.aboScore,
                                            andrewsScore = rc.andrewsScore,
                                            status = "Analyzed",
                                            createdAt = rc.createdAt,
                                            updatedAt = rc.createdAt
                                        )
                                        caseDao.insertCase(caseEntity)
                                    }
                                }
                            }
                        } catch (ex: Exception) {
                            Log.w(TAG, "Sync error in root cases listener: ${ex.message}")
                        }
                    }
                }
            }
            listeners.add(rootListener)

            // B. User private subcollection listener
            if (uid.isNotEmpty() && uid != "anonymous") {
                val userListener = firestore.collection("users").document(uid).collection("cases").addSnapshotListener { snapshot, error ->
                    if (error != null) {
                        Log.e("FIRESTORE_ERROR", "User subcollection listen failed: ${error.code}", error)
                        return@addSnapshotListener
                    }
                    if (snapshot != null) {
                        Log.d("FIRESTORE_DEBUG", "Received ${snapshot.size()} cases from user subcollection")
                        this@channelFlow.launch(Dispatchers.IO) {
                            try {
                                for (change in snapshot.documentChanges) {
                                    val doc = change.document
                                    if (change.type == com.google.firebase.firestore.DocumentChange.Type.REMOVED) {
                                        caseDao.deleteCaseById(doc.id)
                                        caseDao.deleteCase(uid, doc.id)
                                    } else {
                                        val rc = SavedCase.fromFirestoreDoc(doc)
                                        if (!isCaseDeletedLocally(rc.id) && !isCaseDeletedLocally(rc.patientName)) {
                                            val caseEntity = CaseEntity(
                                                id = rc.id,
                                                userId = uid,
                                                patientId = rc.patientId,
                                                patientName = rc.patientName,
                                                title = "Assessment Finishing: ${rc.viewType.uppercase()}",
                                                viewType = rc.viewType,
                                                imagePath = rc.imagePath,
                                                reportJson = rc.clinicalDataJson,
                                                reportId = rc.id,
                                                confidenceScore = rc.confidenceScore,
                                                aboScore = rc.aboScore,
                                                andrewsScore = rc.andrewsScore,
                                                status = "Analyzed",
                                                createdAt = rc.createdAt,
                                                updatedAt = rc.createdAt
                                            )
                                            caseDao.insertCase(caseEntity)
                                        }
                                    }
                                }
                            } catch (ex: Exception) {
                                Log.w(TAG, "Sync error in user subcollection listener: ${ex.message}")
                            }
                        }
                    }
                }
                listeners.add(userListener)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start firestore snapshot listener", e)
        }
        
        awaitClose {
            localJob.cancel()
            listeners.forEach { it.remove() }
        }
    }.flowOn(Dispatchers.IO)

    suspend fun saveFullCase(
        patient: Patient,
        imageUri: Uri?,
        imageBytes: ByteArray?,
        clinical: ClinicalReport,
        aiReport: AIReport
    ) {
        val uid = userId()
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

        val overallFinishingScore = (clinical.andrewsScore + clinical.archSymmetryScore + clinical.rootAngulationScore) / 3f

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
                aboScore = clinical.aboScore,
                andrewsScore = clinical.andrewsScore,
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
                "doctor_name" to patient.doctorName,
                "doctorName" to patient.doctorName,
                "image_url" to effectiveImageUrl,
                "imagePath" to effectiveImageUrl,
                "storage_url" to effectiveImageUrl,
                "view_type" to clinical.viewType,
                "viewType" to clinical.viewType,
                "status" to "completed",
                "finishing_score" to overallFinishingScore,
                "overall_finishing_score" to overallFinishingScore,
                "alignment_score" to clinical.archSymmetryScore,
                "arch_symmetry_score" to clinical.archSymmetryScore,
                "archSymmetryScore" to clinical.archSymmetryScore,
                "confidence_score" to clinical.confidenceScore,
                "confidenceScore" to clinical.confidenceScore,
                "midline_deviation_mm" to clinical.midlineDiscrepancyMm,
                "midlineDiscrepancyMm" to clinical.midlineDiscrepancyMm,
                "overjet_mm" to clinical.overjetMm,
                "overjetMm" to clinical.overjetMm,
                "overbite_percent" to clinical.overbitePercent,
                "overbitePercent" to clinical.overbitePercent,
                "abo_score" to clinical.aboScore,
                "aboScore" to clinical.aboScore,
                "andrews_score" to clinical.andrewsScore,
                "andrewsScore" to clinical.andrewsScore,
                "root_angulation_score" to clinical.rootAngulationScore,
                "rootAngulationScore" to clinical.rootAngulationScore,
                "prediction" to "Orthodontic finishing analysis completed. Alignment: ${clinical.archSymmetryScore.toInt()}%, Andrews: ${clinical.andrewsScore.toInt()}%, Root Angulation: ${clinical.rootAngulationScore.toInt()}%.",
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
                return ClinicalReport(
                    viewType = sc.viewType,
                    confidenceScore = sc.confidenceScore,
                    aboScore = sc.aboScore,
                    archSymmetryScore = sc.alignmentScore,
                    rootAngulationScore = sc.rootAngulationScore,
                    andrewsScore = sc.andrewsScore,
                    overjetMm = (doc.getDouble("overjet_mm") ?: 2.4).toFloat(),
                    overbitePercent = (doc.getDouble("overbite_percent") ?: 25.0).toFloat(),
                    midlineDiscrepancyMm = (doc.getDouble("midline_deviation_mm") ?: 0.0).toFloat(),
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
        val score = if (aboScore > 0f) aboScore else (if (andrewsScore > 0f) andrewsScore else 0f)
        return SavedCase(
            id = id,
            patientId = patientId,
            patientName = patientName,
            doctorName = "",
            imagePath = imagePath,
            viewType = viewType,
            confidenceScore = confidenceScore,
            aboScore = aboScore,
            andrewsScore = andrewsScore,
            finishingScore = score,
            overallFinishingScore = score,
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
