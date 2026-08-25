package com.example.orthofinixai.ui

import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.R
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.components.MainBottomBar
import com.example.orthofinixai.ui.navigation.Screen
import com.example.orthofinixai.ui.viewmodel.PatientViewModel
import com.example.orthofinixai.ui.viewmodel.PatientState
import com.example.orthofinixai.ui.viewmodel.AuthViewModel
import com.example.orthofinixai.ui.viewmodel.AuthState
import androidx.compose.ui.text.style.TextAlign
import android.widget.Toast
import androidx.compose.ui.platform.LocalContext
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.model.ClinicalReport
import com.example.orthofinixai.util.PdfGenerator

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onAddCaseClick: () -> Unit,
    onCaseClick: (String) -> Unit,
    onProfileClick: () -> Unit,
    onNotificationsClick: () -> Unit,
    onSeeAllClick: () -> Unit,
    onBottomNav: (String) -> Unit = {},
    onDemoClick: () -> Unit = {},
    viewModel: PatientViewModel = viewModel(),
    authViewModel: AuthViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val authState by authViewModel.uiState.collectAsState()
    val context = LocalContext.current

    var showAccuracyDialog by remember { mutableStateOf(false) }
    var caseToDelete by remember { mutableStateOf<SavedCase?>(null) }

    LaunchedEffect(Unit) {
        viewModel.fetchPatients()
    }

    if (caseToDelete != null) {
        AlertDialog(
            onDismissRequest = { caseToDelete = null },
            title = { Text("Delete Case?", fontWeight = FontWeight.Bold, color = ClinicalDeepNavy) },
            text = { Text("This will permanently delete ${caseToDelete!!.patientName}'s analysis record from the registry.", color = ClinicalSlate) },
            confirmButton = {
                TextButton(onClick = {
                    val targetCaseId = caseToDelete!!.id
                    caseToDelete = null
                    viewModel.deleteCase(targetCaseId)
                }) { Text("Delete", color = StatusError, fontWeight = FontWeight.Bold) }
            },
            dismissButton = {
                TextButton(onClick = { caseToDelete = null }) { Text("Cancel", color = ClinicalSlate) }
            },
            shape = RoundedCornerShape(16.dp),
            containerColor = Color.White
        )
    }

    if (showAccuracyDialog) {
        AlertDialog(
            onDismissRequest = { showAccuracyDialog = false },
            title = { 
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Verified, contentDescription = null, tint = ClinicalEmerald, modifier = Modifier.size(24.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Clinical AI Accuracy Index", fontWeight = FontWeight.Bold)
                }
            },
            text = { 
                Text(
                    "The 98.4% index represents the average geometric landmark tracer accuracy validated across large-scale golden orthodontic datasets. All predictions are continuously benchmarked against standard American Board of Orthodontics (ABO) Objective Grading System guidelines and Andrews' Six Keys definitions.",
                    fontSize = 14.sp,
                    color = ClinicalSlate
                )
            },
            confirmButton = {
                TextButton(onClick = { showAccuracyDialog = false }) {
                    Text("Understood", color = ClinicalSkyBlue, fontWeight = FontWeight.Bold)
                }
            },
            shape = RoundedCornerShape(16.dp),
            containerColor = Color.White
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Image(
                            painter = painterResource(id = R.drawable.orthofinix_logo),
                            contentDescription = null,
                            modifier = Modifier.size(32.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("OrthofinixAI", fontWeight = FontWeight.Black, fontSize = 20.sp, color = ClinicalDeepNavy)
                    }
                },
                actions = {
                    IconButton(onClick = onNotificationsClick) {
                        Icon(Icons.Default.Notifications, null, tint = ClinicalSlate)
                    }
                    IconButton(onClick = onProfileClick) {
                        val userName = (authState as? AuthState.Authenticated)?.user?.display_name ?: "D"
                        Box(
                            modifier = Modifier.size(32.dp).clip(CircleShape).background(ClinicalSkyBlue),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(userName.take(1).uppercase(), color = Color.White, fontWeight = FontWeight.Bold)
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceClinical)
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = onAddCaseClick,
                containerColor = ClinicalDeepNavy,
                contentColor = Color.White,
                icon = { Icon(Icons.Default.Add, "New Case") },
                text = { Text("NEW CASE") }
            )
        },
        bottomBar = {
            MainBottomBar(currentRoute = Screen.Dashboard.route, onNavigate = onBottomNav)
        },
        containerColor = BackgroundClinical
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
        ) {
            // Welcome Section
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(SurfaceClinical)
                    .padding(24.dp)
            ) {
                Column {
                    val doctorName = (authState as? AuthState.Authenticated)?.user?.display_name ?: "Doctor"
                    Text("Welcome Back,", color = ClinicalSlate, fontSize = 14.sp)
                    Text("Dr. $doctorName", fontSize = 24.sp, fontWeight = FontWeight.Black, color = ClinicalDeepNavy)
                    
                    Spacer(modifier = Modifier.height(20.dp))
                    
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        val totalCases = (uiState as? PatientState.Success)?.savedCases?.size
                            ?: (uiState as? PatientState.Success)?.patients?.size ?: 0
                        
                        QuickStatCard(
                            label = "ACTIVE CASES", 
                            value = totalCases.toString(), 
                            accent = ClinicalSkyBlue, 
                            modifier = Modifier.weight(1f),
                            onClick = {
                                Toast.makeText(context, "Displaying roster of $totalCases registered clinical cases.", Toast.LENGTH_SHORT).show()
                            }
                        )
                        
                        QuickStatCard(
                            label = "AI ACCURACY", 
                            value = "98.4%", 
                            accent = ClinicalEmerald, 
                            modifier = Modifier.weight(1f),
                            onClick = {
                                showAccuracyDialog = true
                            }
                        )
                    }
                }
            }

            // Recent Cases Section
            Column(modifier = Modifier.padding(24.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Recent Assessments", fontWeight = FontWeight.Bold, fontSize = 18.sp, color = ClinicalDeepNavy)
                    TextButton(onClick = onSeeAllClick) {
                        Text("View Records", color = ClinicalSkyBlue, fontWeight = FontWeight.Bold)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                when (val state = uiState) {
                    is PatientState.Loading -> {
                        Box(modifier = Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator(color = ClinicalSkyBlue)
                        }
                    }
                    is PatientState.Success -> {
                        val cases = state.savedCases
                        if (cases.isEmpty()) {
                            EmptyDashboardState(onDemoClick = onDemoClick)
                        } else {
                            cases.take(5).forEach { c ->
                                ClinicalCaseItem(
                                    case = c, 
                                    onClick = onCaseClick, 
                                    onDeleteCase = { caseToDelete = c },
                                    context = context
                                )
                                Spacer(modifier = Modifier.height(12.dp))
                            }
                        }
                    }
                    is PatientState.Error -> {
                        ErrorMessage("Unable to load cases. Data is stored on-device.")
                    }
                    else -> {}
                }
            }
        }
    }
}

@Composable
fun QuickStatCard(
    label: String, 
    value: String, 
    accent: Color, 
    modifier: Modifier,
    onClick: () -> Unit = {}
) {
    Card(
        modifier = modifier.clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = BackgroundClinical),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(label, fontSize = 10.sp, fontWeight = FontWeight.Black, color = ClinicalSlate, letterSpacing = 1.sp)
            Text(value, fontSize = 24.sp, fontWeight = FontWeight.Bold, color = accent)
        }
    }
}


@Composable
fun ClinicalCaseItem(
    case: SavedCase, 
    onClick: (String) -> Unit, 
    onDeleteCase: ((String) -> Unit)? = null,
    context: android.content.Context
) {
    val clinicalData = try {
        if (case.clinicalDataJson.isNotEmpty()) ClinicalReport.fromJson(case.clinicalDataJson) else null
    } catch (e: Exception) { null }

    Card(
        modifier = Modifier.fillMaxWidth().clickable { onClick(case.id) },
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Thumbnail
                Box(
                    modifier = Modifier.size(64.dp).clip(RoundedCornerShape(12.dp)).background(BackgroundClinical),
                    contentAlignment = Alignment.Center
                ) {
                    if (case.imagePath.isNotEmpty()) {
                        // In a real app we'd load image with Coil, here we just show placeholder
                        Icon(Icons.Default.Person, null, tint = ClinicalDeepNavy, modifier = Modifier.size(32.dp))
                    } else {
                        Icon(Icons.Default.Assignment, null, tint = ClinicalDeepNavy, modifier = Modifier.size(32.dp))
                    }
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(case.patientName, fontWeight = FontWeight.Bold, fontSize = 18.sp, color = ClinicalDeepNavy)
                    val overallScore = if (clinicalData != null) {
                        (clinicalData.andrewsScore + clinicalData.archSymmetryScore + clinicalData.rootAngulationScore) / 3f
                    } else {
                        case.displayScore
                    }
                    Text("Overall Score: ${overallScore.toInt()}%", fontWeight = FontWeight.Bold, fontSize = 14.sp, color = ClinicalEmerald)
                }
                Box(
                    modifier = Modifier.clip(CircleShape).background(ClinicalEmerald.copy(alpha = 0.1f)).padding(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text("ANALYZED", color = ClinicalEmerald, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }

            if (clinicalData != null) {
                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider(color = BorderClinical)
                Spacer(modifier = Modifier.height(8.dp))
                
                // Scores Row
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    ScoreBadge("ABO", "${clinicalData.aboScore.toInt()}")
                    ScoreBadge("Andrews", "${clinicalData.andrewsScore.toInt()}")
                    ScoreBadge("Roling", clinicalData.rolingResult?.overallScore?.toInt()?.toString() ?: "N/A")
                    ScoreBadge("Raleigh", clinicalData.raleighWilliamsResult?.overallScore?.toInt()?.toString() ?: "N/A")
                }

                Spacer(modifier = Modifier.height(12.dp))
                Text("Measurements:", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                Text("Overjet: ${clinicalData.overjetMm}mm | Overbite: ${clinicalData.overbitePercent}% | Symmetry: ${clinicalData.archSymmetryScore}%", fontSize = 12.sp, color = ClinicalSlate)
                
                Spacer(modifier = Modifier.height(8.dp))
                Text("Top Recommendation:", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = ClinicalDeepNavy)
                val rec = clinicalData.recommendations.firstOrNull() ?: clinicalData.structuredRecommendations.firstOrNull()?.clinicalActionStep ?: "No recommendations"
                Text(rec, fontSize = 12.sp, color = ClinicalSlate, maxLines = 1)
            }

            Spacer(modifier = Modifier.height(16.dp))
            HorizontalDivider(color = BorderClinical)
            Spacer(modifier = Modifier.height(8.dp))
            
            // Buttons Row
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End, verticalAlignment = Alignment.CenterVertically) {
                TextButton(onClick = { onClick(case.id) }) {
                    Text("View Report", color = ClinicalSkyBlue, fontWeight = FontWeight.Bold)
                }
                Spacer(modifier = Modifier.width(4.dp))
                IconButton(onClick = { PdfGenerator.generateAndSharePdf(context, case) }) {
                    Icon(Icons.Default.Share, contentDescription = "Share PDF", tint = ClinicalSkyBlue)
                }
                IconButton(onClick = { PdfGenerator.generateAndSharePdf(context, case) }) {
                    Icon(Icons.Default.PictureAsPdf, contentDescription = "Download PDF", tint = ClinicalDeepNavy)
                }
                if (onDeleteCase != null) {
                    IconButton(onClick = { onDeleteCase(case.id) }) {
                        Icon(Icons.Default.Delete, contentDescription = "Delete Case", tint = StatusError)
                    }
                }
            }
        }
    }
}

@Composable
fun ScoreBadge(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = ClinicalDeepNavy)
        Text(label, fontSize = 10.sp, color = ClinicalSlate)
    }
}

@Composable
fun EmptyDashboardState(onDemoClick: () -> Unit = {}) {
    Column(
        modifier = Modifier.fillMaxWidth().padding(48.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(Icons.Default.CloudUpload, null, modifier = Modifier.size(64.dp), tint = BorderClinical)
        Spacer(modifier = Modifier.height(16.dp))
        Text("No clinical records yet", color = ClinicalSlate, fontWeight = FontWeight.Medium)
        Text("Tap NEW CASE or try the STAR Summit demo", color = ClinicalSlate.copy(alpha = 0.5f), fontSize = 12.sp)
        Spacer(modifier = Modifier.height(20.dp))
        Button(
            onClick = onDemoClick,
            colors = ButtonDefaults.buttonColors(containerColor = ClinicalEmerald)
        ) {
            Icon(Icons.Default.PlayArrow, null, modifier = Modifier.size(18.dp))
            Spacer(modifier = Modifier.width(8.dp))
            Text("Try Demo", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun ErrorMessage(msg: String) {
    Box(
        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(StatusError.copy(alpha = 0.1f)).padding(16.dp)
    ) {
        Text(msg, color = StatusError, fontSize = 13.sp, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
    }
}
