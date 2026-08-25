package com.example.orthofinixai.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Layers
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.orthofinixai.data.AnalysisSession
import com.example.orthofinixai.ui.components.BrandedTopBar
import com.example.orthofinixai.ui.components.ConfidenceMeter
import com.example.orthofinixai.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VisualOverlayScreen(onBack: () -> Unit) {
    var showLandmarks by remember { mutableStateOf(true) }
    var showFdi by remember { mutableStateOf(true) }
    var showOcclusal by remember { mutableStateOf(true) }

    val report = AnalysisSession.lastReport
    val imageUri = AnalysisSession.imageUri
    val landmarks = AnalysisSession.landmarkPoints
    val teeth = AnalysisSession.detectedTeeth

    Scaffold(
        topBar = { BrandedTopBar("Landmark Overlay", onBack = onBack) }
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding)
        ) {
            report?.let {
                ConfidenceMeter(
                    confidence = it.confidence_score,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                )
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .padding(16.dp)
                    .background(Color.Black, RoundedCornerShape(16.dp)),
                contentAlignment = Alignment.Center
            ) {
                if (imageUri != null) {
                    AsyncImage(
                        model = imageUri,
                        contentDescription = "Clinical image",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                } else {
                    Text("No image in session", color = Color.Gray)
                }

                Canvas(modifier = Modifier.fillMaxSize()) {
                    val w = size.width
                    val h = size.height

                    if (showOcclusal) {
                        drawLine(
                            color = BrandGreen.copy(alpha = 0.7f),
                            start = Offset(w * 0.1f, h * 0.45f),
                            end = Offset(w * 0.9f, h * 0.48f),
                            strokeWidth = 3f
                        )
                    }

                    if (showLandmarks) {
                        landmarks.forEach { (key, pt) ->
                            val x = pt.first * w
                            val y = pt.second * h
                            val isIncisal = key.contains("incisal") || key.contains("cusp")
                            drawCircle(
                                color = if (isIncisal) Color.Yellow else BrandTeal,
                                radius = if (isIncisal) 10f else 7f,
                                center = Offset(x, y)
                            )
                        }
                    }

                    if (showFdi) {
                        teeth.forEachIndexed { i, fdi ->
                            val seg = landmarks["${fdi}_midpoint"] ?: landmarks["${fdi}_fa"]
                            if (seg != null) {
                                drawCircle(
                                    color = BrandNavy.copy(alpha = 0.85f),
                                    radius = 18f,
                                    center = Offset(seg.first * w, seg.second * h - 28f)
                                )
                            }
                        }
                    }
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                FilterChip(
                    selected = showLandmarks,
                    onClick = { showLandmarks = !showLandmarks },
                    label = { Text("Landmarks") },
                    leadingIcon = { Icon(Icons.Default.Visibility, null, Modifier.size(16.dp)) }
                )
                FilterChip(
                    selected = showFdi,
                    onClick = { showFdi = !showFdi },
                    label = { Text("FDI #") },
                    leadingIcon = { Icon(Icons.Default.Layers, null, Modifier.size(16.dp)) }
                )
                FilterChip(
                    selected = showOcclusal,
                    onClick = { showOcclusal = !showOcclusal },
                    label = { Text("Occlusal plane") }
                )
            }

            Text(
                "${landmarks.size} landmarks • ${teeth.size} teeth (FDI)",
                modifier = Modifier.padding(bottom = 16.dp).fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                fontSize = 12.sp,
                color = ClinicalSlate
            )
        }
    }
}
