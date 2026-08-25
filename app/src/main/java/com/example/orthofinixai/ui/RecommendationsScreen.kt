package com.example.orthofinixai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Lightbulb
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
import com.example.orthofinixai.data.model.ClinicalRecommendationDto
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray
import com.example.orthofinixai.ui.viewmodel.AnalysisViewModel
import com.example.orthofinixai.ui.viewmodel.AnalysisState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecommendationsScreen(
    viewModel: AnalysisViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Clinical Recommendations") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(Color(0xFFF9FAFB))
        ) {
            when (uiState) {
                is AnalysisState.Processing -> RecsLoadingState()
                is AnalysisState.Error -> RecsErrorState((uiState as AnalysisState.Error).message, onBack)
                else -> {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val structured = report?.structured_recommendations.orEmpty()

                    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                        Text("Personalized Correction Steps", fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text(
                            "${structured.size} recommendations from measured clinical findings",
                            color = TextGray, fontSize = 14.sp
                        )
                        Spacer(modifier = Modifier.height(16.dp))

                        if (structured.isEmpty()) {
                            Text("No structured recommendations — run a new analysis.", color = TextGray)
                        } else {
                            LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                                items(structured, key = { it.discrepancyDetected }) { rec ->
                                    StructuredRecommendationCard(rec)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StructuredRecommendationCard(rec: ClinicalRecommendationDto) {
    val severityColor = when (rec.severity) {
        "Severe" -> Color(0xFFDC2626)
        "Moderate" -> Color(0xFFF59E0B)
        else -> PrimaryGreen
    }
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Lightbulb, contentDescription = null, tint = severityColor)
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text("Priority ${rec.priority}", fontSize = 11.sp, color = TextGray)
                    Text(rec.discrepancyDetected, fontWeight = FontWeight.Bold, fontSize = 15.sp)
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text(rec.clinicalActionStep, fontSize = 14.sp, color = Color.Black)
            if (rec.affectedTeeth.isNotEmpty()) {
                Text(
                    "Teeth (FDI): ${rec.affectedTeeth.joinToString(", ")}",
                    fontSize = 12.sp, color = TextGray, modifier = Modifier.padding(top = 6.dp)
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            HorizontalDivider(color = Color(0xFFF3F4F6))
            Spacer(modifier = Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.Top) {
                Icon(Icons.Default.Build, contentDescription = null, tint = TextGray, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text("Expected outcome:", fontWeight = FontWeight.Bold, fontSize = 12.sp, color = PrimaryGreen)
                    Text(rec.expectedOutcome, fontSize = 12.sp, color = TextGray)
                }
            }
            Text(
                "${rec.guidelineSource} • ${rec.severity}",
                fontSize = 11.sp, color = PrimaryGreen.copy(alpha = 0.8f),
                modifier = Modifier.align(Alignment.End).padding(top = 8.dp)
            )
        }
    }
}

@Composable
private fun RecsLoadingState() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator(color = PrimaryGreen)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Compiling clinical recommendations from measured findings...", color = TextGray)
    }
}

@Composable
private fun RecsErrorState(message: String, onBack: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(Icons.Default.Warning, contentDescription = null, tint = Color.Red, modifier = Modifier.size(48.dp))
        Text(message, color = TextGray)
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onBack) { Text("Go Back") }
    }
}
