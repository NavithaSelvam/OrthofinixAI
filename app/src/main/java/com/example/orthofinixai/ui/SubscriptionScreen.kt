package com.example.orthofinixai.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SubscriptionScreen(onBack: () -> Unit) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Subscription Plans") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "Choose the right plan for your practice",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(24.dp))

            PlanCard(
                name = "Basic",
                price = "$49",
                period = "/month",
                features = listOf("5 AI Assessments", "ABO OGS Scoring", "PDF Export"),
                isSelected = false
            )

            Spacer(modifier = Modifier.height(16.dp))

            PlanCard(
                name = "Professional",
                price = "$129",
                period = "/month",
                features = listOf("Unlimited Assessments", "All Finishing Keys", "Visual Overlays", "Priority Support"),
                isSelected = true,
                isBestValue = true
            )

            Spacer(modifier = Modifier.height(16.dp))

            PlanCard(
                name = "Institutional",
                price = "Custom",
                period = "",
                features = listOf("Team Collaboration", "API Access", "SSO Integration", "Dedicated Account Manager"),
                isSelected = false
            )

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
fun PlanCard(
    name: String,
    price: String,
    period: String,
    features: List<String>,
    isSelected: Boolean,
    isBestValue: Boolean = false
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = if (isSelected) Color(0xFFF0FDF4) else Color.White),
        border = BorderStroke(2.dp, if (isSelected) PrimaryGreen else Color(0xFFE5E7EB)),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(24.dp)) {
            if (isBestValue) {
                Surface(
                    color = PrimaryGreen,
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.padding(bottom = 8.dp)
                ) {
                    Text(
                        "BEST VALUE",
                        color = Color.White,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
            
            Text(name, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Row(verticalAlignment = Alignment.Bottom) {
                Text(price, fontSize = 32.sp, fontWeight = FontWeight.ExtraBold)
                Text(period, color = TextGray, modifier = Modifier.padding(bottom = 6.dp, start = 4.dp))
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            features.forEach { feature ->
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 4.dp)) {
                    Icon(Icons.Default.Check, contentDescription = null, tint = PrimaryGreen, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(feature, fontSize = 14.sp)
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Button(
                onClick = { /* TODO */ },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isSelected) PrimaryGreen else Color(0xFFF3F4F6),
                    contentColor = if (isSelected) Color.White else Color.Black
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(if (isSelected) "Current Plan" else "Upgrade Now", fontWeight = FontWeight.Bold)
            }
        }
    }
}
