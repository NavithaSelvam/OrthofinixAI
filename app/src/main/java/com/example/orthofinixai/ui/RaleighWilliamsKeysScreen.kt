package com.example.orthofinixai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Rule
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
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray
import com.example.orthofinixai.ui.viewmodel.AnalysisViewModel
import com.example.orthofinixai.ui.viewmodel.AnalysisState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RaleighWilliamsKeysScreen(
    viewModel: AnalysisViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Raleigh-Williams Keys") },
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
                is AnalysisState.Processing -> RwLoadingState()
                is AnalysisState.Error -> RwErrorState((uiState as AnalysisState.Error).message, onBack)
                else -> {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val keys = report?.raleigh_williams_keys.orEmpty()
                    val score = report?.raleigh_williams_score ?: 0f

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                            .verticalScroll(rememberScrollState())
                    ) {
                        Text("Treatment Keys Review", fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text("Raleigh-Williams principles from measured findings", color = TextGray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("Overall RW Score: ${score.toInt()}%", fontWeight = FontWeight.Bold, color = PrimaryGreen)
                        Spacer(modifier = Modifier.height(20.dp))

                        keys.forEach { key ->
                            RWKeyItem(
                                title = "${key.keyNumber}. ${key.keyName}",
                                score = "${key.score.toInt()}%",
                                status = key.status,
                                measurement = key.measurement,
                                explanation = key.explanation
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RWKeyItem(
    title: String,
    score: String,
    status: String,
    measurement: String,
    explanation: String
) {
    val statusColor = when (status) {
        "Pass" -> PrimaryGreen
        "Review" -> Color(0xFFF59E0B)
        else -> Color(0xFFEF4444)
    }
    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Rule, contentDescription = null, tint = statusColor)
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(title, fontWeight = FontWeight.Bold, fontSize = 15.sp)
                }
                Text(score, fontWeight = FontWeight.Black, color = statusColor)
            }
            Text("$status • $measurement", fontSize = 12.sp, color = TextGray, modifier = Modifier.padding(top = 6.dp))
            Text(explanation, fontSize = 14.sp, color = Color.Black, modifier = Modifier.padding(top = 8.dp))
        }
    }
}

@Composable
private fun RwLoadingState() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator(color = PrimaryGreen)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Retrieving Raleigh-Williams diagnostic indexes...", color = TextGray)
    }
}

@Composable
private fun RwErrorState(message: String, onBack: () -> Unit) {
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
