package com.example.orthofinixai.ui

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.data.model.PatientCreate
import com.example.orthofinixai.data.repository.PatientRepository
import com.example.orthofinixai.ui.theme.BrandGreen
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddPatientScreen(onBack: () -> Unit) {
    var name by remember { mutableStateOf("") }
    var age by remember { mutableStateOf("") }
    var gender by remember { mutableStateOf("Male") }
    var phone by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var doctorName by remember { mutableStateOf("") }
    var hospital by remember { mutableStateOf("") }
    var diagnosis by remember { mutableStateOf("") }
    var treatmentDate by remember { mutableStateOf("") }
    var notes by remember { mutableStateOf("") }
    
    var isSaving by remember { mutableStateOf(false) }

    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val repository = remember { PatientRepository(context) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Add New Patient", fontWeight = FontWeight.Bold) },
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
            Text("Enter full clinical details", fontSize = 16.sp, color = Color.Gray)
            Spacer(modifier = Modifier.height(32.dp))

            OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Patient Name") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = age, onValueChange = { age = it }, label = { Text("Age") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            Column(modifier = Modifier.fillMaxWidth()) {
                Text("Gender", fontWeight = FontWeight.Medium)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(selected = gender == "Male", onClick = { gender = "Male" })
                    Text("Male")
                    Spacer(modifier = Modifier.width(16.dp))
                    RadioButton(selected = gender == "Female", onClick = { gender = "Female" })
                    Text("Female")
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = phone, onValueChange = { phone = it }, label = { Text("Phone Number") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = email, onValueChange = { email = it }, label = { Text("Email") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = doctorName, onValueChange = { doctorName = it }, label = { Text("Doctor Name") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = hospital, onValueChange = { hospital = it }, label = { Text("Hospital") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = diagnosis, onValueChange = { diagnosis = it }, label = { Text("Diagnosis") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = treatmentDate, onValueChange = { treatmentDate = it }, label = { Text("Treatment Date (dd/mm/yyyy)") }, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = notes, onValueChange = { notes = it }, label = { Text("Notes") }, modifier = Modifier.fillMaxWidth().height(120.dp), maxLines = 5)
            
            Spacer(modifier = Modifier.height(32.dp))

            if (isSaving) {
                CircularProgressIndicator(color = BrandGreen)
            } else {
                Button(
                    onClick = {
                        if (name.isBlank() || age.isBlank()) {
                            Toast.makeText(context, "Please fill required fields", Toast.LENGTH_SHORT).show()
                        } else {
                            isSaving = true
                            scope.launch {
                                val dob = "01/01/${2026 - age.toIntOrNull()!!}"
                                repository.createPatient(
                                    PatientCreate(
                                        name = name,
                                        dateOfBirth = dob,
                                        gender = gender,
                                        phone = phone,
                                        email = email,
                                        doctorName = doctorName,
                                        hospital = hospital,
                                        diagnosis = diagnosis,
                                        treatmentDate = treatmentDate,
                                        notes = notes
                                    )
                                ).collect { result ->
                                    isSaving = false
                                    result.onSuccess {
                                        Toast.makeText(context, "Patient saved to Firebase", Toast.LENGTH_SHORT).show()
                                        onBack()
                                    }.onFailure {
                                        Toast.makeText(context, "Failed to save patient", Toast.LENGTH_SHORT).show()
                                    }
                                }
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = BrandGreen)
                ) {
                    Text("Save Patient", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}
