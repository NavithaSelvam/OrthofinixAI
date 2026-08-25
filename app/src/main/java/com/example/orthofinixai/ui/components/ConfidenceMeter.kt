package com.example.orthofinixai.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*

@Composable
fun ConfidenceMeter(
    confidence: Float,
    modifier: Modifier = Modifier,
    label: String = "AI Detection Confidence"
) {
    val pct = (confidence * 100).toInt().coerceIn(0, 100)
    val color = when {
        confidence >= 0.8f -> BrandGreen
        confidence >= 0.65f -> StatusWarning
        else -> StatusError
    }
    val status = when {
        confidence >= 0.8f -> "High — clinically reliable"
        confidence >= 0.65f -> "Moderate — review recommended"
        else -> "Low — verify landmarks manually"
    }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp)
    ) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(label, fontWeight = FontWeight.SemiBold, fontSize = 14.sp, color = BrandNavy)
            Text("$pct%", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = color)
        }
        Spacer(modifier = Modifier.height(8.dp))
        LinearProgressIndicator(
            progress = { confidence },
            modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
            color = color,
            trackColor = Color(0xFFE2E8F0)
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(status, fontSize = 12.sp, color = ClinicalSlate)
    }
}
