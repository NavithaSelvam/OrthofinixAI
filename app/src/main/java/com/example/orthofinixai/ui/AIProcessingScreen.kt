package com.example.orthofinixai.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.R
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.viewmodel.AnalysisState
import com.example.orthofinixai.ui.viewmodel.AnalysisViewModel
import com.example.orthofinixai.ui.viewmodel.SharedCaseViewModel

@Composable
fun AIProcessingScreen(
    sharedViewModel: SharedCaseViewModel,
    analysisViewModel: AnalysisViewModel,
    patientViewModel: com.example.orthofinixai.ui.viewmodel.PatientViewModel,
    onProcessingComplete: () -> Unit
) {
    val context = LocalContext.current
    val uiState by analysisViewModel.uiState.collectAsState()
    var analysisStarted by remember { mutableStateOf(false) }
    // Bumped whenever the user taps "Retry Analysis" so the LaunchedEffect below
    // re-runs and actually re-sends the request instead of doing nothing.
    var retryTrigger by remember { mutableStateOf(0) }

    val progressValue = when (val state = uiState) {
        is AnalysisState.Processing -> state.progress
        is AnalysisState.Success -> 1f
        else -> 0.05f
    }

    val progressText = when (val state = uiState) {
        is AnalysisState.Processing -> state.message
        is AnalysisState.Success -> "Clinical report generated"
        is AnalysisState.Error -> "Error: ${state.message}"
        else -> "Preparing clinical data..."
    }

    LaunchedEffect(sharedViewModel.opgPhoto, sharedViewModel.patientName, retryTrigger) {
        analysisViewModel.reset()
        analysisStarted = false

        val patientName = sharedViewModel.patientName ?: "Patient"
        val dob = sharedViewModel.dob ?: "01/01/2010"
        val gender = sharedViewModel.gender ?: "Male"
        val imageUri = sharedViewModel.opgPhoto

        val imageBytes = try {
            imageUri?.let { context.contentResolver.openInputStream(it)?.readBytes() }
        } catch (_: Exception) {
            null
        }

        // Guard: Do not proceed if image is null or empty
        if (imageBytes == null || imageBytes.isEmpty()) {
            analysisViewModel.reset()
            return@LaunchedEffect
        }

        val viewType = "opg"

        val caseId = "case_${System.currentTimeMillis()}"

        analysisViewModel.startAnalysis(
            caseId = caseId,
            patientName = patientName,
            dob = dob,
            gender = gender,
            imageUri = imageUri,
            imageBytes = imageBytes,
            viewType = viewType
        )
        analysisStarted = true
    }

    LaunchedEffect(uiState, analysisStarted) {
        if (!analysisStarted) return@LaunchedEffect
        when (uiState) {
            is AnalysisState.Success -> {
                kotlinx.coroutines.delay(400)
                onProcessingComplete()
            }
            else -> Unit
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.verticalGradient(listOf(Color.White, Color(0xFFF0F7FF)))),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Orthofinix Logo Box (Matching Web exactly)
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(androidx.compose.foundation.shape.RoundedCornerShape(16.dp))
                    .background(BrandNavy),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    "O",
                    color = Color.White,
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Black
                )
            }

            Spacer(modifier = Modifier.height(32.dp))

            // Circular Progress Ring with centered percentage
            if (uiState is AnalysisState.Error) {
                Box(
                    modifier = Modifier
                        .size(128.dp)
                        .clip(CircleShape)
                        .background(Color(0xFFFEF2F2))
                        .border(2.dp, Color(0xFFEF4444), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = "Error",
                        tint = Color(0xFFEF4444),
                        modifier = Modifier.size(56.dp)
                    )
                }
            } else {
                Box(
                    modifier = Modifier.size(128.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(
                        progress = { progressValue },
                        modifier = Modifier.size(128.dp),
                        color = BrandGreen,
                        strokeWidth = 6.dp,
                        trackColor = Color(0xFFE5E7EB),
                        strokeCap = StrokeCap.Round
                    )
                    Text(
                        "${(progressValue * 100).toInt()}%",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandNavy
                    )
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            Text(
                "AI Clinical Analysis",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = BrandNavy
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                progressText,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = ClinicalSlate,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = 16.dp)
            )

            Spacer(modifier = Modifier.height(32.dp))

            // Linear Progress Bar (Matching Web)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp))
                    .background(Color(0xFFE2E8F0))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(fraction = progressValue.coerceIn(0f, 1f))
                        .fillMaxHeight()
                        .clip(RoundedCornerShape(3.dp))
                        .background(BrandGreen)
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                "SECURE CLOUD AI PIPELINE • ACCURATE CLINICAL METRICS",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF808080),
                textAlign = TextAlign.Center,
                letterSpacing = 0.8.sp
            )

            if (uiState is AnalysisState.Error) {
                Spacer(modifier = Modifier.height(24.dp))
                OutlinedButton(
                    onClick = {
                        analysisViewModel.reset()
                        retryTrigger++
                    },
                    shape = RoundedCornerShape(12.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, BrandGreen),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = BrandGreen
                    )
                ) {
                    Icon(
                        Icons.Default.Refresh,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Retry Analysis", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                }
            }
        }
    }
}
