package com.example.orthofinixai.data.model

data class Case(
    val id: String,
    val patient_id: String,
    val notes: String? = null,
    val status: String,
    val created_at: String
)

data class ClinicalFindingDto(
    val category: String,
    val toothFdi: Int? = null,
    val measurement: String,
    val value: String,
    val ideal: String,
    val severity: String,
    val explanation: String
)

data class PointDto(val x: Float, val y: Float)

data class ToothLandmarkDto(
    val fdi: Int,
    val incisal_edge: PointDto,
    val apex: PointDto,
    val long_axis_incisal: PointDto,
    val contact_mesial: PointDto,
    val contact_distal: PointDto,
    val center: PointDto,
    val occlusal_surface: PointDto?
)

data class AIReport(
    val id: String,
    val case_id: String,
    val abo_score: Float,
    val arch_symmetry_score: Float,
    val root_angulation_score: Float,
    val andrews_score: Float,
    val recommendations: List<String>,
    val created_at: String,
    val confidence_score: Float = 0.85f,
    val overjet_mm: Float = 2.5f,
    val overbite_percent: Float = 30f,
    val overjet_status: String = "Normal",
    val overbite_status: String = "Normal",
    val molar_right_class: String = "Class I",
    val molar_left_class: String = "Class I",
    val midline_discrepancy_mm: Float = 0f,
    val curve_of_spee_mm: Float = 0f,
    val clinical_findings: List<ClinicalFindingDto> = emptyList(),
    val andrews_violations: List<String> = emptyList(),
    val low_confidence_warning: String? = null,
    val detected_teeth_count: Int = 0,
    val view_type: String = "frontal",
    val tooth_landmarks: Map<Int, ToothLandmarkDto> = emptyMap(),
    val abo_total_deductions: Int = 0,
    val abo_finishing_grade: String = "",
    val abo_categories: List<AboCategoryDto> = emptyList(),
    val andrews_keys: List<AndrewsKeyDto> = emptyList(),
    val roling_score: Float = 0f,
    val roling_parameters: List<RolingParameterDto> = emptyList(),
    val raleigh_williams_score: Float = 0f,
    val raleigh_williams_keys: List<RaleighWilliamsKeyDto> = emptyList(),
    val structured_recommendations: List<ClinicalRecommendationDto> = emptyList(),
    val overall_finishing_score: Float = 0f,
    val overallScore: Float = 0f,
    val alignmentScore: Float = 0f,
    val confidence: Float = 0f,
    val teeth: List<ToothFindingDto> = emptyList(),
    val teeth_data: List<ToothFindingDto> = emptyList()
)

data class ToothFindingDto(
    val toothNumber: Int = 11,
    val fdi: Int = 11,
    val name: String = "",
    val score: Float = 88.5f,
    val confidence: Float = 0.94f,
    val status: String = "Aligned",
    val conditions: List<String> = emptyList(),
    val issues: List<String> = emptyList(),
    val recommendation: String = ""
)
