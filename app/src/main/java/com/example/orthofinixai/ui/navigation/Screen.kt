package com.example.orthofinixai.ui.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object SignUp : Screen("signup")
    object ForgotPassword : Screen("forgot_password")
    object Dashboard : Screen("dashboard")
    object CaseList : Screen("case_list")
    object Notifications : Screen("notifications")
    
    // New Case Flow
    object AddCasePatientInfo : Screen("add_case_patient")
    object AddCaseUploadGuide : Screen("add_case_guide")
    object AddCasePhotoUpload : Screen("add_case_photos")
    object AddCaseOPGUpload : Screen("add_case_opg")
    object AIProcessing : Screen("ai_processing")
    
    // Assessment Results
    object AssessmentSummary : Screen("assessment_summary")
    object ABOScoring : Screen("abo_scoring")
    object AndrewsKeys : Screen("andrews_keys")
    object RolingConcepts : Screen("roling_concepts")
    object RaleighWilliams : Screen("raleigh_williams")
    object VisualOverlay : Screen("visual_overlay")
    object RootAngulation : Screen("root_angulation")
    object Recommendations : Screen("recommendations")
    object ArchSymmetry : Screen("arch_symmetry")
    
    // Tools & Profile
    object GuidelinesLibrary : Screen("guidelines_library")
    object GuidelineDetail : Screen("guideline_detail/{guidelineId}") {
        fun createRoute(guidelineId: String) = "guideline_detail/$guidelineId"
    }
    object Profile : Screen("profile")
    object Settings : Screen("settings")
    object Subscription : Screen("subscription")
    object ExportReport : Screen("export_report")
    object HelpSupport : Screen("help_support")
    object About : Screen("about")
}
