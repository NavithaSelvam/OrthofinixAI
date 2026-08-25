package com.example.orthofinixai.ui

import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.QuestionAnswer
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HelpSupportScreen(onBack: () -> Unit) {
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Help & Support", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.White
                )
            )
        },
        containerColor = BackgroundClinical
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(20.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text(
                "How can we help you?",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = BrandDarkNavy
            )
            Spacer(modifier = Modifier.height(20.dp))

            SupportActionCard(
                title = "Chat with Support", 
                description = "Real-time chat assistance.", 
                icon = Icons.Default.Chat,
                onClick = {
                    Toast.makeText(context, "Opening real-time chat support console...", Toast.LENGTH_SHORT).show()
                }
            )
            
            Spacer(modifier = Modifier.height(12.dp))

            SupportActionCard(
                title = "Email Us", 
                description = "Send us a message at support@orthofinix.ai", 
                icon = Icons.Default.Email,
                onClick = {
                    val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
                        data = Uri.parse("mailto:support@orthofinix.ai")
                        putExtra(Intent.EXTRA_SUBJECT, "Orthofinix.AI Support Request")
                    }
                    try {
                        context.startActivity(emailIntent)
                    } catch (e: Exception) {
                        Toast.makeText(context, "No email client app found on your device.", Toast.LENGTH_LONG).show()
                    }
                }
            )
            
            Spacer(modifier = Modifier.height(12.dp))

            SupportActionCard(
                title = "FAQs", 
                description = "Find answers to commonly asked questions below.", 
                icon = Icons.Default.QuestionAnswer,
                onClick = {
                    Toast.makeText(context, "Scroll down to browse standard clinical FAQs.", Toast.LENGTH_SHORT).show()
                }
            )

            Spacer(modifier = Modifier.height(32.dp))

            Text(
                "Frequently Asked Questions",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = BrandDarkNavy
            )
            Spacer(modifier = Modifier.height(16.dp))

            FAQItem("How accurate is the AI assessment?", "Our AI is trained on thousands of board-certified cases and achieves over 95% consistency with expert human graders.")
            FAQItem("Can I use this for final diagnosis?", "Orthofinix.ai is a decision support tool. Final clinical decisions should always be made by a qualified orthodontist.")
            FAQItem("What image formats are supported?", "We support high-resolution JPG, PNG, and DICOM formats for radiographs.")
        }
    }
}

@Composable
fun SupportActionCard(
    title: String, 
    description: String, 
    icon: ImageVector,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(Color(0xFFE0F2FE), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = Color(0xFF0284C7), modifier = Modifier.size(22.dp))
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(title, fontWeight = FontWeight.Bold, fontSize = 15.sp, color = BrandDarkNavy)
                Text(description, fontSize = 12.sp, color = BrandGray)
            }
        }
    }
}

@Composable
fun FAQItem(question: String, answer: String) {
    Column(modifier = Modifier.padding(vertical = 12.dp)) {
        Text(question, fontWeight = FontWeight.Bold, fontSize = 14.sp, color = BrandDarkNavy)
        Spacer(modifier = Modifier.height(4.dp))
        Text(answer, fontSize = 13.sp, color = BrandGray, lineHeight = 18.sp)
        Spacer(modifier = Modifier.height(12.dp))
        HorizontalDivider(color = Color(0xFFE2E8F0))
    }
}