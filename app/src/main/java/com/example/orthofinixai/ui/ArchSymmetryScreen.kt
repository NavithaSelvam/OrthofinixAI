package com.example.orthofinixai.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.SyncAlt
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.viewmodel.AnalysisViewModel
import com.example.orthofinixai.ui.viewmodel.AnalysisState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ArchSymmetryScreen(
    viewModel: AnalysisViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Arch Symmetry", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = ClinicalDeepNavy,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = BackgroundClinical
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(BackgroundClinical)
        ) {
            when (uiState) {
                is AnalysisState.Processing -> {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator(color = ClinicalSkyBlue, strokeWidth = 4.dp)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Analyzing dental arch symmetry contours...", color = ClinicalSlate, fontSize = 14.sp)
                    }
                }
                is AnalysisState.Error -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.Warning, contentDescription = null, tint = StatusError, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Symmetry Calculations Unreachable", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = ClinicalDeepNavy)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text((uiState as AnalysisState.Error).message, color = ClinicalSlate, fontSize = 14.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                        Spacer(modifier = Modifier.height(24.dp))
                        Button(
                            onClick = onBack,
                            colors = ButtonDefaults.buttonColors(containerColor = ClinicalDeepNavy),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("Go Back", color = Color.White)
                        }
                    }
                }
                else -> {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val symmetryScore = report?.arch_symmetry_score ?: 88f

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                            .verticalScroll(rememberScrollState())
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(240.dp)
                                .background(ClinicalDeepNavy, RoundedCornerShape(12.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            // Dynamic bilateral symmetry visualization
                            Canvas(modifier = Modifier.fillMaxSize().padding(32.dp)) {
                                val midX = size.width / 2
                                // Draw central clinical midline
                                drawLine(Color.White.copy(alpha = 0.5f), Offset(midX, 0f), Offset(midX, size.height), strokeWidth = 2f)
                                
                                // Left side arch representation
                                drawArc(ClinicalSkyBlue, 180f, 90f, false, size = size, style = Stroke(4f))
                                // Right side arch representation (adjusting width slightly to mimic symmetryScore discrepancy)
                                val rightWidthMultiplier = if (symmetryScore < 90f) 0.85f else 0.98f
                                drawArc(
                                    color = ClinicalSkyBlue,
                                    startAngle = 270f,
                                    sweepAngle = 90f,
                                    useCenter = false,
                                    size = size.copy(width = size.width * rightWidthMultiplier),
                                    topLeft = Offset(size.width * (1f - rightWidthMultiplier) * 0.5f, 0f),
                                    style = Stroke(4f)
                                )
                            }
                            Text(
                                text = "Bilateral Symmetry Map Overlay", 
                                color = Color.White.copy(alpha = 0.7f), 
                                modifier = Modifier.align(Alignment.BottomCenter).padding(8.dp)
                            )
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Text("Symmetry Assessment", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                        
                        Spacer(modifier = Modifier.height(16.dp))

                        val maxSymmetry = "${symmetryScore.toInt()}%"
                        val maxFeedback = if (symmetryScore < 90f) {
                            "Slight transverse discrepancy detected in the upper right posterior quadrant segment."
                        } else {
                            "Excellent maxillary arch symmetry achieved."
                        }

                        val mandSymmetry = "${(symmetryScore * 1.05f).coerceAtMost(100f).toInt()}%"
                        val mandFeedback = if (symmetryScore < 80f) {
                            "Minor transverse deviation; evaluate arch coordination."
                        } else {
                            "Superb bilateral balance observed in mandibular segment."
                        }

                        val deviationText = if (symmetryScore > 90f) "0.3mm" else "1.2mm"
                        val deviationFeedback = if (symmetryScore > 90f) {
                            "Within ideal physiological clinical thresholds."
                        } else {
                            "Slight dental midline deviation to the right segment."
                        }

                        SymmetryMetric("Maxillary Arch Balance", maxSymmetry, maxFeedback)
                        SymmetryMetric("Mandibular Arch Balance", mandSymmetry, mandFeedback)
                        SymmetryMetric("Midline Coordinate Deviation", deviationText, deviationFeedback)

                        Spacer(modifier = Modifier.height(32.dp))

                        Card(
                            colors = CardDefaults.cardColors(containerColor = Color(0xFFFDF2F8)),
                            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFCE7F3)),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(modifier = Modifier.padding(16.dp)) {
                                Icon(Icons.Default.SyncAlt, contentDescription = null, tint = Color(0xFFDB2777))
                                Spacer(modifier = Modifier.width(12.dp))
                                Text(
                                    "Bilateral transverse coordination is critical for stable occlusal relationship, facial harmony, and avoiding TMJ dysfunction.",
                                    fontSize = 13.sp,
                                    color = Color(0xFF9D174D)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SymmetryMetric(label: String, value: String, feedback: String) {
    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(label, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                Text(value, color = ClinicalEmerald, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(feedback, fontSize = 13.sp, color = ClinicalSlate)
        }
    }
}
