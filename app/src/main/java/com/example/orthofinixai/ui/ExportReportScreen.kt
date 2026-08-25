package com.example.orthofinixai.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.PictureAsPdf
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray
import com.example.orthofinixai.data.repository.CaseRepository
import com.example.orthofinixai.util.PdfGenerator
import com.example.orthofinixai.util.ReportExporter
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportReportScreen(caseId: String, onBack: () -> Unit) {
    var includePhotos by remember { mutableStateOf(true) }
    var includeGuidelines by remember { mutableStateOf(true) }
    var isGenerating by remember { mutableStateOf(false) }

    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val caseRepository = remember { CaseRepository(context) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Export Report") },
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
            Icon(
                Icons.Default.PictureAsPdf,
                contentDescription = null,
                tint = PrimaryGreen,
                modifier = Modifier.size(80.dp)
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Text("Generate Clinical Report", fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Text(
                "Create a professional PDF summary containing full patient details, clinical measurements, ABO scores, and dynamic recommendations pulled directly from Firestore.",
                color = TextGray,
                fontSize = 14.sp,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 8.dp)
            )

            Spacer(modifier = Modifier.height(40.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Export Options", fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Include Clinical Photos")
                        Switch(checked = includePhotos, onCheckedChange = { includePhotos = it })
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            if (isGenerating) {
                CircularProgressIndicator(color = PrimaryGreen)
                Spacer(modifier = Modifier.height(16.dp))
                Text("Retrieving Firestore Data & Generating PDF...", color = TextGray)
            } else {
                Button(
                    onClick = { 
                        isGenerating = true 
                        scope.launch {
                            try {
                                val targetCase = caseRepository.getSavedCaseSync(caseId) 
                                    ?: caseRepository.observeCases().first().find { it.id == caseId }
                                if (targetCase != null) {
                                    PdfGenerator.generateAndSharePdf(context, targetCase)
                                }
                            } catch (e: CancellationException) {
                                throw e
                            } catch (e: Exception) {
                                android.util.Log.e("ExportReportScreen", "Error generating PDF", e)
                            } finally {
                                isGenerating = false
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
                ) {
                    Icon(Icons.Default.Share, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Generate & Share", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}
