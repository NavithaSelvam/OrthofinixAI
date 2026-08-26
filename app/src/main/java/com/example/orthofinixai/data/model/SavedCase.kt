package com.example.orthofinixai.data.model

import com.google.firebase.firestore.DocumentSnapshot
import com.google.firebase.firestore.PropertyName
import com.google.firebase.firestore.IgnoreExtraProperties
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone

@IgnoreExtraProperties
data class SavedCase(
    @get:PropertyName("id") @set:PropertyName("id") var id: String = "",
    @get:PropertyName("case_id") @set:PropertyName("case_id") var caseId: String = "",
    @get:PropertyName("user_id") @set:PropertyName("user_id") var userId: String = "",
    @get:PropertyName("patientId") @set:PropertyName("patientId") var patientId: String = "",
    @get:PropertyName("patient_name") @set:PropertyName("patient_name") var patientName: String = "",
    @get:PropertyName("doctorName") @set:PropertyName("doctorName") var doctorName: String = "",
    @get:PropertyName("doctorId") @set:PropertyName("doctorId") var doctorId: String = "",
    @get:PropertyName("image_url") @set:PropertyName("image_url") var imageUrl: String = "",
    @get:PropertyName("imagePath") @set:PropertyName("imagePath") var imagePath: String = "",
    @get:PropertyName("view_type") @set:PropertyName("view_type") var viewType: String = "opg",
    @get:PropertyName("confidence_score") @set:PropertyName("confidence_score") var confidenceScore: Int = 95,
    @get:PropertyName("abo_score") @set:PropertyName("abo_score") var aboScore: Int = 0,
    @get:PropertyName("andrews_score") @set:PropertyName("andrews_score") var andrewsScore: Int = 0,
    @get:PropertyName("overall_score") @set:PropertyName("overall_score") var overallScore: Int = 0,
    @get:PropertyName("finishingScore") @set:PropertyName("finishingScore") var finishingScore: Float = 0f,
    @get:PropertyName("overallFinishingScore") @set:PropertyName("overallFinishingScore") var overallFinishingScore: Float = 0f,
    @get:PropertyName("alignment_score") @set:PropertyName("alignment_score") var alignmentScore: Int = 0,
    @get:PropertyName("root_angulation_score") @set:PropertyName("root_angulation_score") var rootAngulationScore: Int = 0,
    @get:PropertyName("status") @set:PropertyName("status") var status: String = "ANALYZED",
    @get:PropertyName("createdAt") @set:PropertyName("createdAt") var createdAt: Long = 0L,
    @get:PropertyName("hasReport") @set:PropertyName("hasReport") var hasReport: Boolean = true,
    @get:PropertyName("clinicalDataJson") @set:PropertyName("clinicalDataJson") var clinicalDataJson: String = "",
    @get:PropertyName("patientProfile") @set:PropertyName("patientProfile") var patientProfile: Patient? = null
) {
    val displayScore: Int
        get() {
            if (overallScore > 0) return overallScore
            if (finishingScore > 0f) return finishingScore.toInt()
            if (overallFinishingScore > 0f) return overallFinishingScore.toInt()
            if (andrewsScore > 0) return andrewsScore
            if (aboScore > 0) return aboScore
            return 0
        }

    companion object {
        fun fromFirestoreDoc(doc: DocumentSnapshot): SavedCase {
            val docId = doc.id
            val pName = doc.getString("patient_name") 
                ?: doc.getString("patientName") 
                ?: doc.getString("name") 
                ?: "Patient"
                
            val pId = doc.getString("patient_id") 
                ?: doc.getString("patientId") 
                ?: doc.getString("id") 
                ?: docId
                
            val dName = doc.getString("doctor_name") 
                ?: doc.getString("doctorName") 
                ?: "Doctor"

            val dId = doc.getString("doctor_id")
                ?: doc.getString("doctorId")
                ?: doc.getString("user_id")
                ?: ""
                
            val img = doc.getString("image_url") 
                ?: doc.getString("imagePath") 
                ?: doc.getString("storage_url") 
                ?: ""
                
            val vType = doc.getString("view_type") 
                ?: doc.getString("viewType") 
                ?: "opg"
                
            val cJson = doc.getString("reportJson") 
                ?: doc.getString("clinicalDataJson") 
                ?: run {
                    try {
                        val m = doc.data ?: emptyMap<String, Any>()
                        com.google.gson.Gson().toJson(m)
                    } catch (_: Exception) { "" }
                }
                
            val oScore = (doc.getDouble("overall_score")
                ?: doc.getDouble("overallScore")
                ?: doc.getDouble("overall_finishing_score") 
                ?: doc.getDouble("finishing_score") 
                ?: doc.getDouble("overallFinishingScore")
                ?: doc.getDouble("finishingScore")
                ?: 0.0).toInt()
                
            val aScore = (doc.getDouble("abo_score") 
                ?: doc.getDouble("aboScore") 
                ?: oScore.toDouble()).toInt()
                
            val andScore = (doc.getDouble("andrews_score") 
                ?: doc.getDouble("andrewsScore") 
                ?: oScore.toDouble()).toInt()
                
            val alignScore = (doc.getDouble("alignment_score")
                ?: doc.getDouble("alignmentScore") 
                ?: doc.getDouble("arch_symmetry_score") 
                ?: oScore.toDouble()).toInt()
                
            val rootScore = (doc.getDouble("root_angulation_score") 
                ?: doc.getDouble("rootAngulationScore") 
                ?: oScore.toDouble()).toInt()
                
            val rawConf = doc.getDouble("confidence_score") 
                ?: doc.getDouble("confidenceScore") 
                ?: 95.0
            val confScore = if (rawConf <= 1.0) (rawConf * 100).toInt() else rawConf.toInt()

            val stat = doc.getString("status") ?: "ANALYZED"

            var timeMs = doc.getLong("createdAt") ?: 0L
            if (timeMs == 0L) {
                val timestampObj = doc.getTimestamp("timestamp") ?: doc.getTimestamp("created_at")
                if (timestampObj != null) {
                    timeMs = timestampObj.toDate().time
                } else {
                    val dateStr = doc.getString("created_at") ?: doc.getString("createdAt")
                    if (!dateStr.isNullOrEmpty()) {
                        timeMs = try {
                            val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US).apply {
                                timeZone = TimeZone.getTimeZone("UTC")
                            }
                            sdf.parse(dateStr.take(19))?.time ?: System.currentTimeMillis()
                        } catch (e: Exception) {
                            System.currentTimeMillis()
                        }
                    } else {
                        timeMs = System.currentTimeMillis()
                    }
                }
            }

            return SavedCase(
                id = docId,
                caseId = docId,
                userId = dId,
                patientId = pId,
                patientName = pName,
                doctorName = dName,
                doctorId = dId,
                imageUrl = img,
                imagePath = img,
                viewType = vType,
                confidenceScore = confScore,
                aboScore = aScore,
                andrewsScore = andScore,
                overallScore = oScore,
                finishingScore = oScore.toFloat(),
                overallFinishingScore = oScore.toFloat(),
                alignmentScore = alignScore,
                rootAngulationScore = rootScore,
                status = stat,
                createdAt = timeMs,
                hasReport = true,
                clinicalDataJson = cJson
            )
        }
    }
}
