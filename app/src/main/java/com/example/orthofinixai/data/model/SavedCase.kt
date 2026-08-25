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
    @get:PropertyName("patientId") @set:PropertyName("patientId") var patientId: String = "",
    @get:PropertyName("patientName") @set:PropertyName("patientName") var patientName: String = "",
    @get:PropertyName("doctorName") @set:PropertyName("doctorName") var doctorName: String = "",
    @get:PropertyName("doctorId") @set:PropertyName("doctorId") var doctorId: String = "",
    @get:PropertyName("imagePath") @set:PropertyName("imagePath") var imagePath: String = "",
    @get:PropertyName("viewType") @set:PropertyName("viewType") var viewType: String = "",
    @get:PropertyName("confidenceScore") @set:PropertyName("confidenceScore") var confidenceScore: Float = 0f,
    @get:PropertyName("aboScore") @set:PropertyName("aboScore") var aboScore: Float = 0f,
    @get:PropertyName("andrewsScore") @set:PropertyName("andrewsScore") var andrewsScore: Float = 0f,
    @get:PropertyName("finishingScore") @set:PropertyName("finishingScore") var finishingScore: Float = 0f,
    @get:PropertyName("overallFinishingScore") @set:PropertyName("overallFinishingScore") var overallFinishingScore: Float = 0f,
    @get:PropertyName("alignmentScore") @set:PropertyName("alignmentScore") var alignmentScore: Float = 0f,
    @get:PropertyName("rootAngulationScore") @set:PropertyName("rootAngulationScore") var rootAngulationScore: Float = 0f,
    @get:PropertyName("createdAt") @set:PropertyName("createdAt") var createdAt: Long = 0L,
    @get:PropertyName("hasReport") @set:PropertyName("hasReport") var hasReport: Boolean = false,
    @get:PropertyName("clinicalDataJson") @set:PropertyName("clinicalDataJson") var clinicalDataJson: String = "",
    @get:PropertyName("patientProfile") @set:PropertyName("patientProfile") var patientProfile: Patient? = null
) {
    val displayScore: Float
        get() {
            if (overallFinishingScore > 0f) return overallFinishingScore
            if (finishingScore > 0f) return finishingScore
            if (andrewsScore > 0f) return andrewsScore
            return if (aboScore > 0f) aboScore else 88.5f
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
                
            val fScore = (doc.getDouble("overallScore")
                ?: doc.getDouble("overall_finishing_score") 
                ?: doc.getDouble("finishing_score") 
                ?: doc.getDouble("overallFinishingScore")
                ?: doc.getDouble("finishingScore")
                ?: 88.5).toFloat()
                
            val aScore = (doc.getDouble("abo_score") 
                ?: doc.getDouble("aboScore") 
                ?: fScore).toFloat()
                
            val andScore = (doc.getDouble("andrews_score") 
                ?: doc.getDouble("andrewsScore") 
                ?: fScore).toFloat()
                
            val alignScore = (doc.getDouble("alignmentScore")
                ?: doc.getDouble("alignment_score") 
                ?: doc.getDouble("arch_symmetry_score") 
                ?: doc.getDouble("alignmentScore") 
                ?: fScore).toFloat()
                
            val rootScore = (doc.getDouble("root_angulation_score") 
                ?: doc.getDouble("rootAngulationScore") 
                ?: fScore).toFloat()
                
            val confScore = (doc.getDouble("confidence")
                ?: doc.getDouble("confidence_score") 
                ?: doc.getDouble("confidenceScore") 
                ?: 0.96).toFloat()

            // Parse timestamp safely from Long, Double, String, or Firestore Timestamp
            var timeMs = doc.getLong("createdAt") ?: 0L
            if (timeMs == 0L) {
                val timestampObj = doc.getTimestamp("timestamp")
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
                patientId = pId,
                patientName = pName,
                doctorName = dName,
                doctorId = dId,
                imagePath = img,
                viewType = vType,
                confidenceScore = confScore,
                aboScore = if (aScore > 0f) aScore else fScore,
                andrewsScore = if (andScore > 0f) andScore else fScore,
                finishingScore = fScore,
                overallFinishingScore = fScore,
                alignmentScore = alignScore,
                rootAngulationScore = rootScore,
                createdAt = timeMs,
                hasReport = true,
                clinicalDataJson = cJson
            )
        }
    }
}
