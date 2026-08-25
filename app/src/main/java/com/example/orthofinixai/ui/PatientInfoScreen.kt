package com.example.orthofinixai.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.LocalTextStyle
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PatientInfoScreen(
    onNext: (String, String, String) -> Unit,
    onBack: () -> Unit
) {

    var firstName by remember { mutableStateOf("") }
    var lastName by remember { mutableStateOf("") }
    var patientId by remember { mutableStateOf("") }
    var dob by remember { mutableStateOf("") }
    var gender by remember { mutableStateOf("Male") }

    // Validation Errors
    var firstNameError by remember { mutableStateOf<String?>(null) }
    var lastNameError by remember { mutableStateOf<String?>(null) }
    var patientIdError by remember { mutableStateOf<String?>(null) }
    var dobError by remember { mutableStateOf<String?>(null) }

    fun validate(): Boolean {
        var isValid = true

        if (firstName.isBlank()) {
            firstNameError = "First name is required"
            isValid = false
        } else {
            firstNameError = null
        }

        if (lastName.isBlank()) {
            lastNameError = "Last name is required"
            isValid = false
        } else {
            lastNameError = null
        }

        if (patientId.isBlank()) {
            patientIdError = "Case ID is required"
            isValid = false
        } else {
            patientIdError = null
        }

        if (dob.isBlank()) {
            dobError = "Date of Birth is required"
            isValid = false
        } else {
            dobError = null
        }

        return isValid
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "New Case Setup",
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        },
        containerColor = BackgroundClinical
    ) { padding ->

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp)
                .verticalScroll(rememberScrollState())
        ) {

            Text(
                text = "Clinical Record",
                color = ClinicalSkyBlue,
                fontWeight = FontWeight.Black,
                fontSize = 12.sp,
                letterSpacing = 1.sp
            )

            Text(
                text = "Create a new patient clinical file",
                color = ClinicalSlate,
                fontSize = 15.sp,
                modifier = Modifier.padding(top = 4.dp)
            )

            Spacer(modifier = Modifier.height(32.dp))

            ClinicalInputField(
                label = "First Name",
                value = firstName,
                onValueChange = {
                    firstName = it
                    firstNameError = null
                },
                placeholder = "e.g., John",
                icon = Icons.Default.Person,
                error = firstNameError
            )

            Spacer(modifier = Modifier.height(16.dp))

            ClinicalInputField(
                label = "Last Name",
                value = lastName,
                onValueChange = {
                    lastName = it
                    lastNameError = null
                },
                placeholder = "e.g., Doe",
                icon = Icons.Default.Person,
                error = lastNameError
            )

            Spacer(modifier = Modifier.height(16.dp))

            ClinicalInputField(
                label = "Patient Case ID",
                value = patientId,
                onValueChange = {
                    patientId = it
                    patientIdError = null
                },
                placeholder = "OF-2024-001",
                icon = Icons.Default.Assignment,
                error = patientIdError
            )

            Spacer(modifier = Modifier.height(16.dp))

            ClinicalInputField(
                label = "Date of Birth",
                value = dob,
                onValueChange = {
                    dob = it
                    dobError = null
                },
                placeholder = "DD/MM/YYYY",
                icon = Icons.Default.CalendarToday,
                error = dobError
            )

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "Gender",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = ClinicalDeepNavy
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth()
            ) {

                FilterChip(
                    selected = gender == "Male",
                    onClick = { gender = "Male" },
                    label = { Text("Male") },
                    leadingIcon = if (gender == "Male") {
                        {
                            Icon(
                                Icons.Default.Check,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    } else null,
                    modifier = Modifier.padding(end = 8.dp)
                )

                FilterChip(
                    selected = gender == "Female",
                    onClick = { gender = "Female" },
                    label = { Text("Female") },
                    leadingIcon = if (gender == "Female") {
                        {
                            Icon(
                                Icons.Default.Check,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    } else null
                )
            }

            Spacer(modifier = Modifier.height(48.dp))

            Button(
                onClick = {
                    if (validate()) {
                        onNext(
                            "$firstName $lastName",
                            dob,
                            gender
                        )
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = ClinicalDeepNavy
                )
            ) {

                Text(
                    text = "Initialize Case Profile",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Text(
                text = "Data is encrypted and HIPAA compliant",
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp),
                textAlign = TextAlign.Center,
                fontSize = 11.sp,
                color = ClinicalSlate
            )
        }
    }
}

@Composable
fun ClinicalInputField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    icon: ImageVector,
    error: String? = null
) {

    Column {

        Text(
            text = label,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            color = ClinicalDeepNavy,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,

            textStyle = LocalTextStyle.current.copy(
                color = Color.Black
            ),

            modifier = Modifier.fillMaxWidth(),

            placeholder = {
                Text(
                    placeholder,
                    color = ClinicalSlate.copy(alpha = 0.5f)
                )
            },

            leadingIcon = {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = ClinicalSkyBlue
                )
            },

            shape = RoundedCornerShape(12.dp),

            isError = error != null,

            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Color.Black,
                unfocusedTextColor = Color.Black,
                cursorColor = Color.Black,

                focusedBorderColor = ClinicalSkyBlue,
                unfocusedBorderColor = BorderClinical,

                focusedContainerColor = Color.White,
                unfocusedContainerColor = Color.White,

                focusedPlaceholderColor = ClinicalSlate,
                unfocusedPlaceholderColor = ClinicalSlate
            )
        )

        if (error != null) {
            Text(
                text = error,
                color = StatusError,
                fontSize = 11.sp,
                modifier = Modifier.padding(
                    top = 4.dp,
                    start = 4.dp
                )
            )
        }
    }
}