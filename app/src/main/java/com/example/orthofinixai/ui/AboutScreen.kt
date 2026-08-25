package com.example.orthofinixai.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.R
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AboutScreen(onBack: () -> Unit) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("About Orthofinix.ai") },
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
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Logo
            Image(
                painter = painterResource(id = R.drawable.logo),
                contentDescription = "Orthofinix Logo",
                modifier = Modifier.size(120.dp)
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Text("Orthofinix.ai", fontSize = 28.sp, fontWeight = FontWeight.Bold)
            Text("Version 1.0.0 (Build 102)", color = TextGray, fontSize = 14.sp)
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Text(
                "Our Mission",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Start
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                "Orthofinix.ai is dedicated to empowering orthodontists with cutting-edge artificial intelligence to achieve the highest standards of treatment finishing. Our platform bridges the gap between clinical expertise and data-driven precision, ensuring every patient receives a 'verified and perfected' smile.",
                color = Color.Black,
                fontSize = 15.sp,
                lineHeight = 22.sp,
                textAlign = TextAlign.Justify
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFF9FAFB))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Clinical Advisory Board", fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("• Dr. Emily Carter, Board Certified Orthodontist", fontSize = 14.sp)
                    Text("• Prof. Michael Zhao, AI & Computer Vision", fontSize = 14.sp)
                    Text("• Dr. Sarah Jenkins, Clinical Excellence Lead", fontSize = 14.sp)
                }
            }
            
            Spacer(modifier = Modifier.height(48.dp))
            
            Text("© 2024 Orthofinix Inc. All rights reserved.", fontSize = 12.sp, color = TextGray)
        }
    }
}
