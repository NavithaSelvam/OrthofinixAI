package com.example.orthofinixai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.viewmodel.AnalysisViewModel
import com.example.orthofinixai.ui.viewmodel.AnalysisState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ABOScoringScreen(
    viewModel: AnalysisViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("ABO OGS Scoring", fontWeight = FontWeight.Bold) },
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
                is AnalysisState.Processing -> LoadingState("Retrieving ABO objective grading parameters...")
                is AnalysisState.Error -> ErrorState((uiState as AnalysisState.Error).message, onBack)
                else -> {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val categories = report?.abo_categories.orEmpty()
                    val totalDeductions = report?.abo_total_deductions ?: 0
                    val netScore = report?.abo_score ?: 0f

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                            .verticalScroll(rememberScrollState())
                    ) {
                        Text("Objective Grading System", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                        Text("American Board of Orthodontics — measured deductions", color = ClinicalSlate, fontSize = 14.sp)

                        Spacer(modifier = Modifier.height(20.dp))

                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = ClinicalDeepNavy),
                            shape = RoundedCornerShape(16.dp)
                        ) {
                            Column(modifier = Modifier.padding(20.dp)) {
                                Text("Net ABO Score", color = Color.White.copy(alpha = 0.7f), fontSize = 12.sp)
                                Text("${netScore.toInt()}%", fontSize = 42.sp, fontWeight = FontWeight.Black, color = Color.White)
                                Text("Total deductions: $totalDeductions pts", color = ClinicalSkyBlue, fontSize = 14.sp)
                                Text(report?.abo_finishing_grade ?: "", color = Color.White.copy(alpha = 0.8f), fontSize = 13.sp)
                            }
                        }

                        Spacer(modifier = Modifier.height(20.dp))

                        if (categories.isEmpty()) {
                            Text("No ABO category data available.", color = ClinicalSlate)
                        } else {
                            categories.forEach { cat ->
                                AboCategoryCard(
                                    name = cat.category,
                                    deduction = cat.deduction,
                                    summary = cat.measurementSummary,
                                    explanation = cat.explanation,
                                    teeth = cat.affectedTeeth
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
private fun AboCategoryCard(
    name: String,
    deduction: Int,
    summary: String,
    explanation: String,
    teeth: List<Int>
) {
    val color = when (deduction) {
        0 -> StatusSuccess
        -1 -> StatusWarning
        else -> StatusError
    }
    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(name, fontWeight = FontWeight.Bold, fontSize = 15.sp, color = ClinicalDeepNavy)
                Text(
                    if (deduction == 0) "0" else deduction.toString(),
                    fontWeight = FontWeight.Black,
                    fontSize = 18.sp,
                    color = color
                )
            }
            Text(summary, fontSize = 13.sp, color = ClinicalSlate, modifier = Modifier.padding(top = 4.dp))
            Text(explanation, fontSize = 13.sp, color = Color.Black, modifier = Modifier.padding(top = 6.dp))
            if (teeth.isNotEmpty()) {
                Text(
                    "Affected teeth (FDI): ${teeth.joinToString(", ")}",
                    fontSize = 12.sp,
                    color = ClinicalSkyBlue,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
private fun LoadingState(message: String) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator(color = ClinicalSkyBlue, strokeWidth = 4.dp)
        Spacer(modifier = Modifier.height(16.dp))
        Text(message, color = ClinicalSlate, fontSize = 14.sp)
    }
}

@Composable
private fun ErrorState(message: String, onBack: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(Icons.Default.Warning, contentDescription = null, tint = StatusError, modifier = Modifier.size(48.dp))
        Spacer(modifier = Modifier.height(16.dp))
        Text("Clinical Report Unavailable", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = ClinicalDeepNavy)
        Spacer(modifier = Modifier.height(8.dp))
        Text(message, color = ClinicalSlate, fontSize = 14.sp)
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = onBack, colors = ButtonDefaults.buttonColors(containerColor = ClinicalDeepNavy)) {
            Text("Go Back", color = Color.White)
        }
    }
}
