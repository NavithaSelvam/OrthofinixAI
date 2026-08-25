package com.example.orthofinixai.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.FileUpload
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.orthofinixai.ui.theme.BorderColor
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OPGUploadScreen(onNext: (Uri) -> Unit, onBack: () -> Unit) {
    var opgUri by remember { mutableStateOf<Uri?>(null) }
    
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        opgUri = uri
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Upload OPG / Radiograph", fontWeight = FontWeight.Bold) },
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
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            LinearProgressIndicator(
                progress = { 1.0f },
                modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(4.dp)),
                color = PrimaryGreen,
                trackColor = Color(0xFFE5E7EB)
            )
            
            Spacer(modifier = Modifier.height(16.dp))

            Text(
                "Step 4 of 4",
                color = PrimaryGreen,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp
            )
            Text(
                "Upload Post-treatment OPG for root analysis",
                color = TextGray,
                fontSize = 16.sp,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(48.dp))

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(280.dp)
                    .clip(RoundedCornerShape(24.dp))
                    .background(Color(0xFFF9FAFB))
                    .border(2.dp, if (opgUri != null) PrimaryGreen else BorderColor, RoundedCornerShape(24.dp))
                    .clickable { launcher.launch("image/*") },
                contentAlignment = Alignment.Center
            ) {
                if (opgUri != null) {
                    AsyncImage(
                        model = opgUri,
                        contentDescription = "OPG Radiograph",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                } else {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            Icons.Default.FileUpload, 
                            contentDescription = null, 
                            tint = PrimaryGreen, 
                            modifier = Modifier.size(64.dp)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Select OPG Radiograph", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                        Text("Supports JPG, PNG, DICOM", fontSize = 14.sp, color = TextGray)
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))
            
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFEFF6FF)),
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp)
            ) {
                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Image, contentDescription = null, tint = Color(0xFF3B82F6))
                    Spacer(modifier = Modifier.width(16.dp))
                    Text(
                        "Ensure the OPG is high resolution and all roots are clearly visible from molar to molar.",
                        fontSize = 14.sp,
                        color = Color(0xFF1E40AF),
                        lineHeight = 20.sp
                    )
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            Button(
                onClick = { opgUri?.let { onNext(it) } },
                enabled = opgUri != null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryGreen,
                    disabledContainerColor = Color.LightGray
                )
            ) {
                Text("Start AI Assessment", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}
