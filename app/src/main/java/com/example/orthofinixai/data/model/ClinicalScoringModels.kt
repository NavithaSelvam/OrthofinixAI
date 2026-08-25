package com.example.orthofinixai.data.model

/** ABO Objective Grading System — per-category deduction (0, -1, -2). */
data class AboCategoryScore(
    val category: String,
    val deduction: Int,
    val maxDeduction: Int = 2,
    val affectedTeeth: List<Int>,
    val measurementSummary: String,
    val explanation: String
)

data class AboOgsResult(
    val categories: List<AboCategoryScore>,
    val totalDeductions: Int,
    val netScore: Float,
    val finishingGrade: String
)

/** Andrews Six Keys — discrete pass/fail per key with violations. */
data class AndrewsKeyEvaluation(
    val keyNumber: Int,
    val keyName: String,
    val passed: Boolean,
    val scorePercent: Float,
    val status: String,
    val explanation: String,
    val violations: List<String>
)

/** Dr. Rebecca Roling functional finishing parameters. */
data class RolingParameter(
    val name: String,
    val status: String,
    val score: Float,
    val measurement: String,
    val explanation: String,
    val suggestion: String
)

data class RolingFinishingResult(
    val parameters: List<RolingParameter>,
    val overallScore: Float
)

/** Raleigh-Williams Treatment Keys. */
data class RaleighWilliamsKey(
    val keyNumber: Int,
    val keyName: String,
    val status: String,
    val score: Float,
    val measurement: String,
    val explanation: String
)

data class RaleighWilliamsResult(
    val keys: List<RaleighWilliamsKey>,
    val overallScore: Float
)

/** Deterministic recommendation derived from measured findings — never from image alone. */
data class ClinicalRecommendation(
    val guidelineSource: String,
    val discrepancyDetected: String,
    val clinicalActionStep: String,
    val affectedTeeth: List<Int>,
    val severity: String,
    val priority: Int,
    val expectedOutcome: String
)

data class ClinicalRecommendationDto(
    val guidelineSource: String,
    val discrepancyDetected: String,
    val clinicalActionStep: String,
    val affectedTeeth: List<Int>,
    val severity: String,
    val priority: Int,
    val expectedOutcome: String
)

data class AboCategoryDto(
    val category: String,
    val deduction: Int,
    val affectedTeeth: List<Int>,
    val measurementSummary: String,
    val explanation: String
)

data class AndrewsKeyDto(
    val keyNumber: Int,
    val keyName: String,
    val passed: Boolean,
    val scorePercent: Float,
    val status: String,
    val explanation: String,
    val violations: List<String>
)

data class RolingParameterDto(
    val name: String,
    val status: String,
    val score: Float,
    val measurement: String,
    val explanation: String,
    val suggestion: String
)

data class RaleighWilliamsKeyDto(
    val keyNumber: Int,
    val keyName: String,
    val status: String,
    val score: Float,
    val measurement: String,
    val explanation: String
)
