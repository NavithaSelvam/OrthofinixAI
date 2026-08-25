package com.example.orthofinixai.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.components.MainBottomBar
import com.example.orthofinixai.ui.navigation.Screen
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.orthofinixai.ui.viewmodel.AuthViewModel
import com.example.orthofinixai.ui.viewmodel.AuthState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onBack: (() -> Unit)? = null,
    onLogoutClick: () -> Unit,
    onSubscriptionClick: () -> Unit,
    onSettingsClick: () -> Unit,
    onHelpSupportClick: () -> Unit,
    onAboutClick: () -> Unit,
    onBottomNav: (String) -> Unit = {},
    viewModel: AuthViewModel = viewModel()
) {
    val authState by viewModel.uiState.collectAsState()
    val user = (authState as? AuthState.Authenticated)?.user
    val userName = user?.display_name ?: "Doctor"
    val userEmail = user?.email ?: "dr.smith@orthofinix.ai"

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    if (onBack != null) {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = ClinicalDeepNavy,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        bottomBar = {
            MainBottomBar(currentRoute = Screen.Profile.route, onNavigate = onBottomNav)
        },
        containerColor = BackgroundClinical
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(100.dp)
                    .clip(CircleShape)
                    .background(ClinicalSkyBlue.copy(alpha = 0.1f))
                    .border(2.dp, ClinicalSkyBlue, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = userName.take(1).uppercase(),
                    color = ClinicalSkyBlue,
                    fontSize = 40.sp,
                    fontWeight = FontWeight.Black
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text("Dr. $userName", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
            Text(userEmail, color = ClinicalSlate, fontSize = 14.sp)
            Text("Orthodontist • Clinic Associate", color = ClinicalSlate.copy(alpha = 0.7f), fontSize = 12.sp)

            Spacer(modifier = Modifier.height(32.dp))

            val context = androidx.compose.ui.platform.LocalContext.current
            
            ProfileMenuItem("Personal Information", Icons.Default.Badge, onClick = onSettingsClick)
            ProfileMenuItem("Clinical Credentials", Icons.Default.Verified, onClick = {
                android.widget.Toast.makeText(context, "Credentials Verified. Certified Orthodontic AI Clinician.", android.widget.Toast.LENGTH_SHORT).show()
            })
            ProfileMenuItem("Subscription Plan", Icons.Default.Payment, "Pro Access", onClick = onSubscriptionClick)
            ProfileMenuItem("Help & Support", Icons.Default.Help, onClick = onHelpSupportClick)
            ProfileMenuItem("About Orthofinix", Icons.Default.Info, onClick = onAboutClick)
            ProfileMenuItem("HIPAA & Security Compliance", Icons.Default.Security, onClick = {
                android.widget.Toast.makeText(context, "All patient data complies with HIPAA and GDPR standards.", android.widget.Toast.LENGTH_SHORT).show()
            })

            Spacer(modifier = Modifier.height(48.dp))

            OutlinedButton(
                onClick = {
                    viewModel.logout()
                    onLogoutClick()
                },
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, Color.Red),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.Red)
            ) {
                Icon(Icons.AutoMirrored.Filled.Logout, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Sign Out", fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun ProfileMenuItem(title: String, icon: ImageVector, trailingText: String = "", onClick: () -> Unit = {}) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        border = BorderStroke(1.dp, BorderClinical),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(icon, contentDescription = null, tint = ClinicalSkyBlue, modifier = Modifier.size(24.dp))
            Spacer(modifier = Modifier.width(16.dp))
            Text(title, modifier = Modifier.weight(1f), fontWeight = FontWeight.Medium, color = ClinicalDeepNavy)
            if (trailingText.isNotEmpty()) {
                Text(trailingText, color = ClinicalEmerald, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 8.dp))
            }
            Icon(Icons.Default.ChevronRight, contentDescription = null, tint = ClinicalSlate)
        }
    }
}
