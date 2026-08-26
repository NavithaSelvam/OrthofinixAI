package com.example.orthofinixai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.ui.components.BrandedTopBar
import com.example.orthofinixai.ui.components.MainBottomBar
import com.example.orthofinixai.ui.navigation.Screen
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.viewmodel.CaseListState
import com.example.orthofinixai.ui.viewmodel.CaseViewModel
import com.example.orthofinixai.ui.viewmodel.PatientState
import com.example.orthofinixai.ui.viewmodel.PatientViewModel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaseListScreen(
    onBack: (() -> Unit)? = null,
    onCaseClick: (String) -> Unit,
    onNewCaseClick: () -> Unit = {},
    onBottomNav: (String) -> Unit = {},
    caseViewModel: CaseViewModel = viewModel()
) {
    val caseState by caseViewModel.uiState.collectAsState()
    var searchQuery by remember { mutableStateOf("") }
    var caseToDelete by remember { mutableStateOf<SavedCase?>(null) }

    val lifecycleOwner = androidx.compose.ui.platform.LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = androidx.lifecycle.LifecycleEventObserver { _, event ->
            if (event == androidx.lifecycle.Lifecycle.Event.ON_RESUME) {
                caseViewModel.refresh()
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    LaunchedEffect(searchQuery) {
        caseViewModel.search(searchQuery)
    }

    val allCases = when (val s = caseState) {
        is CaseListState.Success -> s.cases
        else -> emptyList()
    }

    val isLoading = caseState is CaseListState.Loading && allCases.isEmpty()

    if (caseToDelete != null) {
        AlertDialog(
            onDismissRequest = { caseToDelete = null },
            title = { Text("Delete Case?", fontWeight = FontWeight.Bold, color = ClinicalDeepNavy) },
            text = { Text("This will permanently delete ${caseToDelete!!.patientName}'s analysis record from the registry.", color = ClinicalSlate) },
            confirmButton = {
                TextButton(onClick = {
                    val targetCaseId = caseToDelete!!.id
                    caseToDelete = null
                    caseViewModel.deleteCase(targetCaseId)
                }) { Text("Delete", color = StatusError, fontWeight = FontWeight.Bold) }
            },
            dismissButton = {
                TextButton(onClick = { caseToDelete = null }) { Text("Cancel", color = ClinicalSlate) }
            }
        )
    }

    Scaffold(
        topBar = { 
            BrandedTopBar(
                title = "Clinical Registry", 
                onBack = onBack,
                actions = {
                    IconButton(onClick = {
                        caseViewModel.refresh()
                    }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Sync", tint = ClinicalSkyBlue)
                    }
                }
            ) 
        },
        bottomBar = {
            MainBottomBar(currentRoute = Screen.CaseList.route, onNavigate = onBottomNav)
        },
        containerColor = BackgroundClinical
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(BackgroundClinical)
        ) {
            // Search Input
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                placeholder = { Text("Search by patient name or case ID...", color = ClinicalSlate.copy(alpha = 0.6f), fontSize = 13.sp) },
                leadingIcon = { Icon(Icons.Default.Search, null, tint = ClinicalSkyBlue) },
                shape = RoundedCornerShape(12.dp),
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = ClinicalSkyBlue,
                    unfocusedBorderColor = BorderClinical,
                    focusedContainerColor = Color.White,
                    unfocusedContainerColor = Color.White
                )
            )

            if (isLoading) {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        CircularProgressIndicator(color = ClinicalSkyBlue)
                        Text("Loading clinical cases...", color = ClinicalSlate, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    }
                }
            } else if (allCases.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 24.dp, vertical = 16.dp)
                        .verticalScroll(rememberScrollState()), 
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Box(
                            modifier = Modifier
                                .size(64.dp)
                                .clip(CircleShape)
                                .background(ClinicalSkyBlue.copy(alpha = 0.1f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.FolderOpen, contentDescription = null, tint = ClinicalSkyBlue, modifier = Modifier.size(32.dp))
                        }
                        
                        Spacer(modifier = Modifier.height(12.dp))
                        
                        Text(
                            "No Clinical Cases Found", 
                            fontWeight = FontWeight.Bold, 
                            fontSize = 17.sp,
                            color = ClinicalDeepNavy
                        )
                        
                        Spacer(modifier = Modifier.height(4.dp))
                        
                        Text(
                            "Start a new orthodontic scan analysis or tap Sync to refresh from the cloud.", 
                            color = ClinicalSlate, 
                            fontSize = 13.sp,
                            modifier = Modifier.padding(horizontal = 16.dp),
                            textAlign = androidx.compose.ui.text.style.TextAlign.Center
                        )
                        
                        Spacer(modifier = Modifier.height(20.dp))
                        
                        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            OutlinedButton(
                                onClick = {
                                    caseViewModel.refresh()
                                },
                                shape = RoundedCornerShape(12.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
                            ) {
                                Icon(Icons.Default.Refresh, contentDescription = null, modifier = Modifier.size(16.dp), tint = ClinicalSkyBlue)
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("Sync Cloud", color = ClinicalDeepNavy, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                            }
                            
                            Button(
                                onClick = onNewCaseClick,
                                shape = RoundedCornerShape(12.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = ClinicalSkyBlue)
                            ) {
                                Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("New Scan", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                            }
                        }
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    item {
                        Text(
                            text = "Total Cases: ${allCases.size}",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = ClinicalSlate,
                            modifier = Modifier.padding(bottom = 4.dp)
                        )
                    }
                    items(allCases, key = { it.id }) { case ->
                        SavedCaseCard(
                            case = case,
                            onOpen = { onCaseClick(case.id) },
                            onDelete = { caseToDelete = case }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SavedCaseCard(case: SavedCase, onOpen: () -> Unit, onDelete: () -> Unit) {
    val dateStr = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault()).format(Date(case.createdAt))
    val initial = case.patientName.take(1).uppercase()
    val overallScore = if (case.finishingScore > 0) case.finishingScore.toInt() else case.displayScore.toInt()
    val aboScore = case.aboScore.toInt()
    val andrewsScore = case.andrewsScore.toInt()

    Card(
        onClick = onOpen,
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
        elevation = CardDefaults.cardElevation(2.dp),
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, BorderClinical)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Patient Avatar
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(ClinicalSkyBlue.copy(alpha = 0.12f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = initial,
                        color = ClinicalSkyBlue,
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp
                    )
                }

                Spacer(modifier = Modifier.width(14.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = case.patientName,
                            fontWeight = FontWeight.Bold,
                            fontSize = 16.sp,
                            color = ClinicalDeepNavy,
                            maxLines = 1
                        )
                        
                        Box(
                            modifier = Modifier
                                .clip(CircleShape)
                                .background(ClinicalEmerald.copy(alpha = 0.12f))
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = "$overallScore%",
                                color = ClinicalEmerald,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Text(
                        text = "Case #${case.id.takeLast(8)} • ${case.viewType.uppercase()}", 
                        fontSize = 12.sp, 
                        color = ClinicalSlate
                    )
                }

                Spacer(modifier = Modifier.width(8.dp))

                IconButton(onClick = onDelete) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete", tint = StatusError.copy(alpha = 0.7f), modifier = Modifier.size(20.dp))
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(color = BorderClinical.copy(alpha = 0.5f))
            Spacer(modifier = Modifier.height(8.dp))

            // Score Metrics Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Overall: $overallScore%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = ClinicalEmerald)
                Text("ABO: $aboScore%", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = ClinicalDeepNavy)
                Text("Andrews: $andrewsScore%", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = ClinicalDeepNavy)
                Text(dateStr, fontSize = 11.sp, color = ClinicalSlate.copy(alpha = 0.7f))
            }

            // OPG View Button (Dynamic - Show ONLY if image_url or imagePath is present)
            if (case.imagePath.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    TextButton(
                        onClick = onOpen,
                        contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Icon(Icons.Default.Visibility, contentDescription = null, modifier = Modifier.size(14.dp), tint = ClinicalSkyBlue)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("View OPG Scan", color = ClinicalSkyBlue, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

