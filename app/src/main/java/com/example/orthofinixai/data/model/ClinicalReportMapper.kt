package com.example.orthofinixai.data.model

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/** Maps full ClinicalReport to UI-facing AIReport DTO. */
object ClinicalReportMapper {

    fun toAIReport(clinical: ClinicalReport, caseId: String, reportId: String): AIReport {
        val violations = clinical.andrewsKeys.flatMap { key ->
            key.violations.map { v ->
                "Tooth ${v.toothFdi} ${v.measurementLabel}: ${String.format("%.1f", v.measured)}° (ideal ${String.format("%.1f", v.ideal)}°)."
            }
        }
        val recs = clinical.recommendations.toMutableList()
        clinical.rootDeviations.forEach { r ->
            if (r.severity != "Normal")
                recs.add("Tooth ${r.fdi} root angulation deviation: ${String.format("%.0f", r.angleDeg)}°.")
        }

        val abo = clinical.aboOgsResult
        val roling = clinical.rolingResult
        val rw = clinical.raleighWilliamsResult

        val overall = (
            clinical.aboScore + clinical.archSymmetryScore +
                clinical.rootAngulationScore + clinical.andrewsScore +
                (roling?.overallScore ?: 0f) + (rw?.overallScore ?: 0f)
            ) / 6f

        val toothLandmarks = clinical.toothLandmarks.mapValues { (_, v) ->
            ToothLandmarkDto(
                fdi = v.fdi,
                incisal_edge = PointDto(v.incisalEdge.x, v.incisalEdge.y),
                apex = PointDto(v.longAxisApex.x, v.longAxisApex.y),
                long_axis_incisal = PointDto(v.longAxisIncisal.x, v.longAxisIncisal.y),
                contact_mesial = PointDto(v.contactMesial.x, v.contactMesial.y),
                contact_distal = PointDto(v.contactDistal.x, v.contactDistal.y),
                center = PointDto(v.center.x, v.center.y),
                occlusal_surface = v.occlusalSurface?.let { PointDto(it.x, it.y) }
            )
        }

        return AIReport(
            id = reportId,
            case_id = caseId,
            abo_score = clinical.aboScore,
            arch_symmetry_score = clinical.archSymmetryScore,
            root_angulation_score = clinical.rootAngulationScore,
            andrews_score = clinical.andrewsScore,
            recommendations = recs.distinct(),
            created_at = isoNow(),
            confidence_score = clinical.confidenceScore,
            overjet_mm = clinical.overjetMm,
            overbite_percent = clinical.overbitePercent,
            overjet_status = clinical.overjetStatus,
            overbite_status = clinical.overbiteStatus,
            andrews_violations = violations,
            low_confidence_warning = if (clinical.confidenceScore < 0.65f)
                "Detection confidence low. Please verify landmarks manually." else null,
            detected_teeth_count = clinical.detectedTeethCount,
            view_type = clinical.viewType,
            tooth_landmarks = toothLandmarks,
            molar_right_class = clinical.molarRightClass,
            molar_left_class = clinical.molarLeftClass,
            midline_discrepancy_mm = clinical.midlineDiscrepancyMm,
            curve_of_spee_mm = clinical.curveOfSpeeMm,
            clinical_findings = clinical.supplementalFindings.map {
                ClinicalFindingDto(it.category, it.toothFdi, it.measurement, it.value, it.ideal, it.severity, it.explanation)
            },
            abo_total_deductions = abo?.totalDeductions ?: 0,
            abo_finishing_grade = abo?.finishingGrade ?: "",
            abo_categories = abo?.categories?.map {
                AboCategoryDto(it.category, it.deduction, it.affectedTeeth, it.measurementSummary, it.explanation)
            } ?: emptyList(),
            andrews_keys = clinical.andrewsKeyEvaluations.map {
                AndrewsKeyDto(it.keyNumber, it.keyName, it.passed, it.scorePercent, it.status, it.explanation, it.violations)
            },
            roling_score = roling?.overallScore ?: 0f,
            roling_parameters = roling?.parameters?.map {
                RolingParameterDto(it.name, it.status, it.score, it.measurement, it.explanation, it.suggestion)
            } ?: emptyList(),
            raleigh_williams_score = rw?.overallScore ?: 0f,
            raleigh_williams_keys = rw?.keys?.map {
                RaleighWilliamsKeyDto(it.keyNumber, it.keyName, it.status, it.score, it.measurement, it.explanation)
            } ?: emptyList(),
            structured_recommendations = clinical.structuredRecommendations.map {
                ClinicalRecommendationDto(
                    it.guidelineSource, it.discrepancyDetected, it.clinicalActionStep,
                    it.affectedTeeth, it.severity, it.priority, it.expectedOutcome
                )
            },
            overall_finishing_score = overall
        )
    }

    private fun isoNow(): String =
        SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("UTC")
        }.format(Date())
}
