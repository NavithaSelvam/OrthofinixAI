package com.example.orthofinixai.data.model

import com.google.gson.Gson
import java.util.Date

/** Complete clinical analysis report — serializable to JSON and Room. */
data class ClinicalReport(
    val viewType: String = "opg",
    val overallScore: Float = 88.5f,
    val confidenceScore: Float = 0.96f,
    val aboScore: Float = 88f,
    val archSymmetryScore: Float = 88f,
    val alignmentScore: Float = 88f,
    val rootAngulationScore: Float = 88f,
    val andrewsScore: Float = 88f,
    val andrewsKeys: List<KeySummary> = emptyList(),
    val overjetMm: Float = 2.4f,
    val overbitePercent: Float = 25f,
    val overbiteAbsMm: Float = 0f,
    val overjetStatus: String = "Normal",
    val overbiteStatus: String = "Normal",
    val rootDeviations: List<RootDeviation> = emptyList(),
    val recommendations: List<String> = emptyList(),
    val detectedTeethCount: Int = 28,
    val scaleFactor: Float = 1.0f,
    val molarRightClass: String = "Class I",
    val molarLeftClass: String = "Class I",
    val midlineDiscrepancyMm: Float = 0f,
    val curveOfSpeeMm: Float = 0f,
    val supplementalFindings: List<SupplementalFinding> = emptyList(),
    val landmarkOverlay: Map<String, LandmarkPoint> = emptyMap(),
    val toothLandmarks: Map<Int, ToothLandmarks> = emptyMap(),
    val detectedTeethFdi: List<Int> = emptyList(),
    val generatedAt: Long = System.currentTimeMillis(),
    val aboOgsResult: AboOgsResult? = null,
    val andrewsKeyEvaluations: List<AndrewsKeyEvaluation> = emptyList(),
    val rolingResult: RolingFinishingResult? = null,
    val raleighWilliamsResult: RaleighWilliamsResult? = null,
    val structuredRecommendations: List<ClinicalRecommendation> = emptyList(),
    val teethData: List<ToothScore> = emptyList(),
    val teeth: List<ToothScore> = emptyList()
) {
    data class ToothScore(
        val toothNumber: Int = 11,
        val fdi: Int = 11,
        val name: String = "",
        val confidence: Float = 0.96f,
        val condition: String = "healthy",
        val score: Float = 88f,
        val status: String = "Aligned",
        val alert: String? = null,
        val issues: List<String> = emptyList(),
        val recommendation: String = ""
    )

    data class LandmarkPoint(val x: Float, val y: Float)

    data class ToothLandmarks(
        val fdi: Int,
        val incisalEdge: LandmarkPoint,
        val longAxisApex: LandmarkPoint,
        val longAxisIncisal: LandmarkPoint,
        val contactMesial: LandmarkPoint,
        val contactDistal: LandmarkPoint,
        val center: LandmarkPoint,
        val occlusalSurface: LandmarkPoint?
    )

    data class SupplementalFinding(
        val category: String,
        val toothFdi: Int? = null,
        val measurement: String,
        val value: String,
        val ideal: String,
        val severity: String,
        val explanation: String
    )
    data class KeySummary(
        val keyNumber: Int,
        val keyName: String,
        val status: String,
        val score: Float,
        val violations: List<Violation>,
        val explanation: String
    )

    data class Violation(
        val toothFdi: Int,
        val measurementLabel: String,
        val measured: Float,
        val ideal: Float,
        val deviation: Float,
        val severity: String,
        val clinicalExplanation: String
    )

    data class RootDeviation(
        val fdi: Int,
        val angleDeg: Float,
        val status: String,
        val severity: String,
        val recommendation: String
    )

    fun toJson(): String = Gson().toJson(this)

    companion object {
        fun fromJson(json: String): ClinicalReport = Gson().fromJson(json, ClinicalReport::class.java)
    }
}
