package com.example.orthofinixai.data.model

data class GuidelineInfo(
    val id: String,
    val name: String,
    val category: String,
    val description: String,
    val keyPoints: List<String>,
    val clinicalSignificance: String
)

val guidelinesData = listOf(
    GuidelineInfo(
        id = "abo-ogs",
        name = "ABO Objective Grading System (OGS)",
        category = "Finishing Index",
        description = "The global gold standard for board-level orthodontic finishing assessment and case examination.",
        keyPoints = listOf(
            "Alignment and Leveling (anterior incisal & posterior marginal ridges)",
            "Marginal Ridge Heights (adjacent premolars and molars within 0.5mm)",
            "Buccolingual Inclination (avoiding excessive lingual cusp hanging)",
            "Occlusal Contacts (functional contact across all premolar/molar cusps)",
            "Occlusal Relationships (Class I canine and molar intercuspation)",
            "Overjet & Anterior Crossbite (proper 1-3mm contact with guidance)",
            "Interproximal Contacts (tight, closed contacts without food traps)",
            "Root Angulation (parallel roots on panoramic radiograph)"
        ),
        clinicalSignificance = "ABO OGS scoring ensures board-certified finishing quality, post-treatment stability, and balanced periodontal health."
    ),
    GuidelineInfo(
        id = "andrews-keys",
        name = "Andrews' Six Keys to Normal Occlusion",
        category = "Occlusal Fundamentals",
        description = "The six fundamental morphological characteristics observed in naturally optimal non-orthodontic occlusions.",
        keyPoints = listOf(
            "Key 1: Molar Relationship (mesiobuccal cusp into mesiobuccal groove & distal cusp contacts)",
            "Key 2: Crown Angulation / Tip (gingival portion located distal to incisal portion)",
            "Key 3: Crown Inclination / Torque (anterior labial/lingual torque & posterior lingual crown inclination)",
            "Key 4: Absence of Rotations (teeth free of undesirable rotations)",
            "Key 5: Tight Contacts (no interdental spaces present)",
            "Key 6: Flat Curve of Spee (depth ≤ 1.5mm for optimal mandibular excursion)"
        ),
        clinicalSignificance = "Forms the foundational biomechanical blueprint for straight-wire bracket prescriptions and functional occlusion."
    ),
    GuidelineInfo(
        id = "roling-concepts",
        name = "Dr. Rebecca Roling's Finishing Concepts",
        category = "Functional Stability",
        description = "Practical clinical guidelines focusing on arch form symmetry, canine seating, and long-term functional stability.",
        keyPoints = listOf(
            "Maxillary Intercanine Width Stability",
            "Solid Canine Guidance without Balance Interferences",
            "Torque Expression in Maxillary Lateral Incisors",
            "Marginal Ridge Alignment between Upper 4s and 5s",
            "Second Molar Control and Alignment"
        ),
        clinicalSignificance = "Prevents relapse and ensures aesthetic smile arc curvature consonant with the lower lip."
    ),
    GuidelineInfo(
        id = "raleigh-williams",
        name = "Raleigh-Williams Keys to Excellence",
        category = "Clinical Finishing",
        description = "Detailed criteria for finishing orthodontic cases with aesthetic and gnathological precision.",
        keyPoints = listOf(
            "Parallel roots verified on panoramic radiograph",
            "Flat or gentle curve of Spee (< 1.0mm)",
            "Correct anterior torque for solid incisal stops",
            "Centric relation coinciding with centric occlusion",
            "Smooth canine protected excursion"
        ),
        clinicalSignificance = "Ensures functional masticatory comfort and protects against temporomandibular joint dysfunction."
    ),
    GuidelineInfo(
        id = "ricketts-analysis",
        name = "Ricketts / Merrifield Analysis",
        category = "Cephalometric & Skeletal",
        description = "Cephalometric, profile, and skeletal finishing criteria for facial balance and profile harmony.",
        keyPoints = listOf(
            "Esthetic Plane (E-line) lip positions",
            "Lower Incisor to A-Pog line (1-3mm ideal)",
            "Facial Axis & Mandibular Plane stability",
            "Total Space Analysis for arch length discrepancy"
        ),
        clinicalSignificance = "Maintains soft tissue profile harmony and avoids excessive lip protrusion or retrusion."
    ),
    GuidelineInfo(
        id = "roth-williams",
        name = "Roth / Williams Philosophy",
        category = "Gnathological Philosophy",
        description = "Functional occlusion, seated condylar position (CR-CO harmony), and mutually protected occlusion.",
        keyPoints = listOf(
            "Condyles seated in anterior-superior position (Centric Relation)",
            "Mutually protected occlusion with anterior guidance",
            "No balancing / non-working side interferences",
            "Optimized posterior disclusion during lateral & protrusive excursions"
        ),
        clinicalSignificance = "Eliminates occlusal trauma and protects restorative dentistry longevity."
    )
)
