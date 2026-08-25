package com.example.orthofinixai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.orthofinixai.ui.viewmodel.AnalysisViewModel
import com.example.orthofinixai.ui.viewmodel.AnalysisState
import com.example.orthofinixai.ui.viewmodel.PatientViewModel
import com.example.orthofinixai.ui.viewmodel.PatientState
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.platform.LocalContext
import com.example.orthofinixai.util.PdfGenerator
import com.example.orthofinixai.util.ReportExporter
import com.example.orthofinixai.ui.components.ConfidenceMeter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssessmentSummaryScreen(
    onBack: () -> Unit,
    onDetails: (String) -> Unit,
    onVisualOverlay: () -> Unit = {},
    viewModel: AnalysisViewModel,
    patientViewModel: PatientViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    
    val patientList = (patientViewModel.uiState.collectAsState().value as? PatientState.Success)?.patients ?: emptyList()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Clinical Analysis", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val patient = patientList.find { it.id == report?.case_id }
                    
                    if (report != null) {
                        IconButton(onClick = { 
                            val caseData = patientViewModel.getSavedCaseForReport(report) ?: return@IconButton
                            PdfGenerator.generateAndSharePdf(context, caseData) 
                        }) {
                            Icon(Icons.Default.PictureAsPdf, contentDescription = "Export")
                        }
                        IconButton(onClick = { 
                            val caseData = patientViewModel.getSavedCaseForReport(report) ?: return@IconButton
                            PdfGenerator.generateAndSharePdf(context, caseData) 
                        }) {
                            Icon(Icons.Default.Share, contentDescription = "Share")
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = BackgroundClinical)
            )
        },
        containerColor = BackgroundClinical
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when (uiState) {
                is AnalysisState.Processing -> {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator(color = PrimaryGreen, strokeWidth = 4.dp)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Compiling orthodontics diagnostic parameters...", color = TextGray, fontSize = 14.sp)
                    }
                }
                is AnalysisState.Error -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.Warning, contentDescription = null, tint = Color.Red, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Analysis Retrieval Failed", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = Color.Black)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text((uiState as AnalysisState.Error).message, color = TextGray, fontSize = 14.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                        Spacer(modifier = Modifier.height(24.dp))
                        Button(
                            onClick = onBack,
                            colors = ButtonDefaults.buttonColors(containerColor = Color.Black),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("Go Back")
                        }
                    }
                }
                else -> {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val patient = patientList.find { it.id == report?.case_id }

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState())
                    ) {
                        ResultHeaderCard(report)

                        report?.let { r ->
                            ConfidenceMeter(
                                confidence = r.confidence_score,
                                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                            )
                        }

                        report?.low_confidence_warning?.let { warning ->
                            Card(
                                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                                colors = CardDefaults.cardColors(containerColor = StatusWarning.copy(alpha = 0.15f)),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Icon(Icons.Default.Warning, contentDescription = null, tint = StatusWarning)
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Text(warning, fontSize = 13.sp, color = ClinicalDeepNavy)
                                }
                            }
                        }

                        Column(modifier = Modifier.padding(16.dp)) {
                            SectionTitle("Occlusal Measurements")
                            ClinicalMetricItem("Overjet", "${String.format("%.1f", report?.overjet_mm ?: 0f)} mm — ${report?.overjet_status ?: ""}", Icons.Default.Straighten, StatusSuccess) {}
                            ClinicalMetricItem("Overbite", "${String.format("%.0f", report?.overbite_percent ?: 0f)}% — ${report?.overbite_status ?: ""}", Icons.Default.Height, StatusSuccess) {}
                            ClinicalMetricItem("Right Molar", report?.molar_right_class ?: "—", Icons.Default.MedicalServices, StatusSuccess) {}
                            ClinicalMetricItem("Left Molar", report?.molar_left_class ?: "—", Icons.Default.MedicalServices, StatusSuccess) {}
                            ClinicalMetricItem("Midline", "${String.format("%.1f", report?.midline_discrepancy_mm ?: 0f)} mm", Icons.Default.VerticalAlignCenter, StatusSuccess) {}
                            ClinicalMetricItem("Curve of Spee", "${String.format("%.1f", report?.curve_of_spee_mm ?: 0f)} mm", Icons.Default.Timeline, StatusSuccess) {}

                            if (!report?.clinical_findings.isNullOrEmpty()) {
                                Spacer(modifier = Modifier.height(16.dp))
                                SectionTitle("Clinical Findings (FDI)")
                                report?.clinical_findings?.forEach { finding ->
                                    Card(
                                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
                                        shape = RoundedCornerShape(10.dp),
                                        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
                                    ) {
                                        Column(modifier = Modifier.padding(12.dp)) {
                                            Text(finding.category, fontWeight = FontWeight.Bold, fontSize = 13.sp, color = BrandNavy)
                                            Text(finding.explanation, fontSize = 13.sp, color = ClinicalSlate, lineHeight = 18.sp)
                                        }
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(8.dp))
                            SectionTitle("Per-Tooth Scoring & FDI Odontogram")
                            OdontogramCard(report)

                            Spacer(modifier = Modifier.height(8.dp))
                            SectionTitle("Core Clinical Metrics")
                            
                            ClinicalMetricItem(
                                title = "ABO OGS Scoring",
                                value = "${report?.abo_score?.toInt() ?: 0}% (${report?.abo_total_deductions ?: 0} deductions)",
                                icon = Icons.Default.Analytics,
                                status = if ((report?.abo_score ?: 0f) > 75) StatusSuccess else StatusWarning,
                                onClick = { onDetails("abo") }
                            )

                            ClinicalMetricItem(
                                title = "Andrews Six Keys",
                                value = "${report?.andrews_score?.toInt() ?: 0}% — ${report?.andrews_keys?.count { it.passed } ?: 0}/6 Pass",
                                icon = Icons.Default.Key,
                                status = if ((report?.andrews_score ?: 0f) > 75) StatusSuccess else StatusWarning,
                                onClick = { onDetails("andrews") }
                            )

                            ClinicalMetricItem(
                                title = "Roling Finishing",
                                value = "${report?.roling_score?.toInt() ?: 0}%",
                                icon = Icons.Default.AutoAwesome,
                                status = if ((report?.roling_score ?: 0f) > 80) StatusSuccess else StatusWarning,
                                onClick = { onDetails("roling") }
                            )

                            ClinicalMetricItem(
                                title = "Raleigh-Williams Keys",
                                value = "${report?.raleigh_williams_score?.toInt() ?: 0}%",
                                icon = Icons.Default.Rule,
                                status = if ((report?.raleigh_williams_score ?: 0f) > 80) StatusSuccess else StatusWarning,
                                onClick = { onDetails("raleigh") }
                            )

                            ClinicalMetricItem(
                                title = "Arch Symmetry",
                                value = "${report?.arch_symmetry_score?.toInt() ?: 0}%",
                                icon = Icons.Default.Transform,
                                status = if ((report?.arch_symmetry_score ?: 0f) > 80) StatusSuccess else StatusWarning,
                                onClick = { onDetails("symmetry") }
                            )

                            ClinicalMetricItem(
                                title = "Root Angulation",
                                value = "${report?.root_angulation_score?.toInt() ?: 0}%",
                                icon = Icons.Default.Visibility,
                                status = if ((report?.root_angulation_score ?: 0f) > 75) StatusSuccess else StatusError,
                                onClick = { onDetails("roots") }
                            )

                            Spacer(modifier = Modifier.height(24.dp))
                            SectionTitle("Clinical Recommendations")

                            val structuredRecs = report?.structured_recommendations.orEmpty()
                            if (structuredRecs.isNotEmpty()) {
                                structuredRecs.take(4).forEachIndexed { index, rec ->
                                    Card(
                                        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Column(modifier = Modifier.padding(12.dp)) {
                                            Text(
                                                "${index + 1}. ${rec.discrepancyDetected}",
                                                fontWeight = FontWeight.Bold, fontSize = 13.sp, color = BrandNavy
                                            )
                                            Text(rec.clinicalActionStep, fontSize = 12.sp, color = ClinicalSlate, lineHeight = 17.sp)
                                            Text(rec.guidelineSource, fontSize = 11.sp, color = BrandGreen, modifier = Modifier.padding(top = 4.dp))
                                        }
                                    }
                                }
                                if (structuredRecs.size > 4) {
                                    TextButton(onClick = { onDetails("recommendations") }) {
                                        Text("View all ${structuredRecs.size} recommendations", color = BrandGreen)
                                    }
                                }
                            } else {
                                RecommendationsCard(report?.recommendations ?: emptyList())
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            OutlinedButton(
                                onClick = onVisualOverlay,
                                modifier = Modifier.fillMaxWidth().height(52.dp),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Icon(Icons.Default.Visibility, contentDescription = null)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("View Landmark Overlay & FDI", fontWeight = FontWeight.SemiBold)
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            Button(
                                onClick = {
                                    report?.let { reportData ->
                                        val caseData = patientViewModel.getSavedCaseForReport(reportData)
                                        if (caseData != null) {
                                            PdfGenerator.generateAndSharePdf(context, caseData)
                                        }
                                    }
                                },
                                modifier = Modifier.fillMaxWidth().height(56.dp),
                                shape = RoundedCornerShape(12.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = ClinicalDeepNavy)
                            ) {
                                Text("Generate Comprehensive PDF Report", fontWeight = FontWeight.Bold)
                            }
                            
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ResultHeaderCard(report: com.example.orthofinixai.data.model.AIReport?) {
    val overallScore = report?.overallScore?.takeIf { it > 0f }
        ?: report?.overall_finishing_score?.takeIf { it > 0f }
        ?: report?.let { (it.abo_score + it.arch_symmetry_score + it.root_angulation_score + it.andrews_score) / 4 }
        ?: 88.5f
    
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(220.dp)
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(ClinicalDeepNavy, ClinicalDeepNavy.copy(alpha = 0.8f))
                )
            )
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                "ORTHODONTIC FINISHING SCORE", 
                color = Color.White.copy(alpha = 0.7f),
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.sp
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "${overallScore.toInt()}", 
                fontSize = 72.sp, 
                fontWeight = FontWeight.Black, 
                color = Color.White
            )
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(20.dp))
                    .background(Color.White.copy(alpha = 0.2f))
                    .padding(horizontal = 16.dp, vertical = 4.dp)
            ) {
                Text(
                    if (overallScore > 80) "PROCEED TO DEBOND" else "ADDITIONAL DETAILING REQUIRED",
                    color = Color.White,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun ClinicalMetricItem(
    title: String,
    value: String,
    icon: ImageVector,
    status: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(ClinicalSkyBlue.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = ClinicalDeepNavy, modifier = Modifier.size(20.dp))
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(title, fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = ClinicalDeepNavy)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(status))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(value, fontSize = 13.sp, color = ClinicalSlate, fontWeight = FontWeight.Medium)
                }
            }
            
            Icon(Icons.Default.ChevronRight, contentDescription = null, tint = ClinicalSlate.copy(alpha = 0.5f))
        }
    }
}

@Composable
fun RecommendationsCard(recommendations: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            if (recommendations.isEmpty()) {
                Text("Waiting for AI analysis results...", color = ClinicalSlate, fontSize = 14.sp)
            } else {
                recommendations.forEachIndexed { index, rec ->
                    Row(modifier = Modifier.padding(vertical = 6.dp)) {
                        Text("${index + 1}.", fontWeight = FontWeight.Bold, color = ClinicalSkyBlue, modifier = Modifier.width(24.dp))
                        Text(rec, fontSize = 14.sp, color = Color.Black, lineHeight = 20.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun SectionTitle(title: String) {
    Text(
        title.uppercase(),
        fontSize = 11.sp,
        fontWeight = FontWeight.Black,
        color = ClinicalSlate,
        modifier = Modifier.padding(bottom = 12.dp, top = 8.dp),
        letterSpacing = 1.sp
    )
}

@Composable
fun OdontogramCard(report: com.example.orthofinixai.data.model.AIReport?) {
    val upperTeeth = listOf(18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28)
    val lowerTeeth = listOf(48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38)
    val baseScore = (report?.overallScore?.takeIf { it > 0f } ?: report?.overall_finishing_score ?: 88.5f).toInt()
    val teethList = report?.teeth?.takeIf { it.isNotEmpty() } ?: report?.teeth_data.orEmpty()
    val teethMap = teethList.associateBy { it.toothNumber.takeIf { num -> num > 0 } ?: it.fdi }

    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Text("Maxillary (Upper) Arch — FDI 18..11 & 21..28", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = ClinicalSlate)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                upperTeeth.forEach { fdi ->
                    val toothObj = teethMap[fdi]
                    val toothScore = toothObj?.score?.toInt() ?: baseScore
                    val isAligned = toothObj?.status?.contains("Aligned", ignoreCase = true) ?: (toothScore >= 80)
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("$fdi", fontSize = 8.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                        Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(if (isAligned) PrimaryGreen else StatusWarning))
                        Text("$toothScore%", fontSize = 7.sp, color = ClinicalSlate)
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))
            Text("Mandibular (Lower) Arch — FDI 48..41 & 31..38", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = ClinicalSlate)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                lowerTeeth.forEach { fdi ->
                    val toothObj = teethMap[fdi]
                    val toothScore = toothObj?.score?.toInt() ?: baseScore
                    val isAligned = toothObj?.status?.contains("Aligned", ignoreCase = true) ?: (toothScore >= 80)
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("$fdi", fontSize = 8.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                        Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(if (isAligned) PrimaryGreen else StatusWarning))
                        Text("$toothScore%", fontSize = 7.sp, color = ClinicalSlate)
                    }
                }
            }
        }
    }
}

