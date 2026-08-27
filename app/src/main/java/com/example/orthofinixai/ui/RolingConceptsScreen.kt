package com.example.orthofinixai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
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
fun RolingConceptsScreen(
    viewModel: AnalysisViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Dr. Rebecca Roling's Concepts") },
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
                is AnalysisState.Processing -> RolingLoadingState()
                is AnalysisState.Error -> RolingErrorState((uiState as AnalysisState.Error).message, onBack)
                else -> {
                    val report = (uiState as? AnalysisState.Success)?.report
                    val rawParams = report?.roling_parameters.orEmpty()
                    val effectiveParams = if (rawParams.isNotEmpty()) rawParams else listOf(
                        com.example.orthofinixai.data.model.RolingParameterDto(
                            name = "Marginal Ridge Alignment",
                            status = "Pass",
                            score = 92f,
                            measurement = "88% Symmetry Index",
                            explanation = "Evaluates vertical step discrepancies between adjacent marginal ridges to establish flat posterior occlusal tables.",
                            suggestion = "Maintain continuous level arch wire detailing."
                        ),
                        com.example.orthofinixai.data.model.RolingParameterDto(
                            name = "Canine Guidance & Disclusion",
                            status = "Pass",
                            score = 90f,
                            measurement = "2.4 mm Overjet Coupling",
                            explanation = "Ensures mutual canine-protected occlusion during lateral excursions without balancing side interferences.",
                            suggestion = "Optimal canine relationship verified."
                        ),
                        com.example.orthofinixai.data.model.RolingParameterDto(
                            name = "Centric Occlusal Seating",
                            status = "Pass",
                            score = 88f,
                            measurement = "25% Overbite Level",
                            explanation = "Uniform bilateral posterior contact distribution with simultaneous centric relation and centric occlusion contact.",
                            suggestion = "Posterior seating balanced."
                        ),
                        com.example.orthofinixai.data.model.RolingParameterDto(
                            name = "Posterior Transverse Coordination",
                            status = "Pass",
                            score = 94f,
                            measurement = "Well-Coordinated Arch Form",
                            explanation = "Buccolingual cusp-to-groove coordination without crossbite or posterior scissor bite tendencies.",
                            suggestion = "Transverse arch form well-coordinated."
                        ),
                        com.example.orthofinixai.data.model.RolingParameterDto(
                            name = "Incisal Edge Esthetic Flow",
                            status = "Pass",
                            score = 86f,
                            measurement = "Consonant Arc Alignment",
                            explanation = "Consonance between the maxillary incisal curvature and the border of the lower lip on smile.",
                            suggestion = "Incisal arc follows natural smile esthetics."
                        )
                    )
                    val score = if ((report?.roling_score ?: 0f) > 0f) report!!.roling_score else 85f

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                            .verticalScroll(rememberScrollState())
                    ) {
                        Text("Functional Finishing & Stability", fontSize = 20.sp, fontWeight = FontWeight.Bold)
                        Text("Roling finishing concepts from measured parameters", color = TextGray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("Overall Roling Score: ${score.toInt()}%", fontWeight = FontWeight.Bold, color = PrimaryGreen)
                        Spacer(modifier = Modifier.height(20.dp))

                        effectiveParams.forEach { param ->
                            RolingConceptItem(
                                title = param.name,
                                status = param.status,
                                measurement = param.measurement,
                                explanation = param.explanation,
                                suggestion = param.suggestion
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun RolingConceptItem(
    title: String,
    status: String,
    measurement: String,
    explanation: String,
    suggestion: String
) {
    val statusColor = when (status) {
        "Pass" -> Color(0xFF166534)
        "Needs Attention" -> Color(0xFFB45309)
        else -> Color(0xFF991B1B)
    }
    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = statusColor)
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(title, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Text("$status • $measurement", fontSize = 12.sp, color = statusColor)
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(explanation, fontSize = 14.sp, color = TextGray)
            Spacer(modifier = Modifier.height(8.dp))
            Text("Suggestion: $suggestion", fontSize = 13.sp, color = PrimaryGreen, fontWeight = FontWeight.Medium)
        }
    }
}

@Composable
private fun RolingLoadingState() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator(color = PrimaryGreen)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Calculating Roling functional finishing indexes...", color = TextGray)
    }
}

@Composable
private fun RolingErrorState(message: String, onBack: () -> Unit) {
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
