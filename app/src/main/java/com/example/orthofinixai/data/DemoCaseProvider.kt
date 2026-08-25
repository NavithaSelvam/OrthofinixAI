package com.example.orthofinixai.data

import androidx.annotation.VisibleForTesting
import com.example.orthofinixai.data.model.AIReport
import com.example.orthofinixai.data.model.ClinicalFindingDto

/**
 * DEBUG / TEST ONLY: Static mock report used exclusively for UI preview testing when disconnected.
 * Production clinical workflows MUST receive model-derived reports from the FastAPI backend.
 */
@VisibleForTesting(otherwise = VisibleForTesting.NONE)
object DemoCaseProvider {
    const val DEMO_CASE_ID = "demo-summit-case"

    fun buildDemoReport(): AIReport = AIReport(
        id = "demo-report-001",
        case_id = DEMO_CASE_ID,
        abo_score = 8f,
        arch_symmetry_score = 88.5f,
        root_angulation_score = 86f,
        andrews_score = 89f,
        recommendations = listOf(
            "Tooth 11 torque inclination deviates by +4°.",
            "Overjet measured at 2.1 mm.",
            "Left molar relationship classified as Class I.",
            "Root uprighting required for tooth 23 (9° deviation).",
            "Curve of Spee depth: 1.4 mm — favorable flat plane."
        ),
        created_at = java.time.Instant.now().toString(),
        confidence_score = 0.94f,
        overjet_mm = 2.1f,
        overbite_percent = 28f,
        overjet_status = "Normal",
        overbite_status = "Normal",
        molar_right_class = "Class I (0.8 mm)",
        molar_left_class = "Class I (1.1 mm)",
        midline_discrepancy_mm = 0.6f,
        curve_of_spee_mm = 1.4f,
        low_confidence_warning = null,
        detected_teeth_count = 28,
        view_type = "frontal",
        clinical_findings = listOf(
            ClinicalFindingDto("Overjet", null, "Overjet", "2.1 mm", "2.0–4.0 mm", "Normal", "Overjet within normal range."),
            ClinicalFindingDto("Midline", null, "Midline Discrepancy", "0.6 mm", "< 1.0 mm", "Normal", "Dental midline acceptable."),
            ClinicalFindingDto("Molar Relationship", null, "Left Molar", "Class I", "Class I", "Normal", "Left molar relationship classified as Class I.")
        )
    )
}
