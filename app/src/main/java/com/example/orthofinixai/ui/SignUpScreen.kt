package com.example.orthofinixai.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.orthofinixai.ui.theme.*
import com.example.orthofinixai.ui.viewmodel.AuthState
import com.example.orthofinixai.ui.viewmodel.AuthViewModel

@Composable
fun SignUpScreen(
    onSignUpClick: () -> Unit,
    onSignInClick: () -> Unit,
    viewModel: AuthViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(uiState) {
        if (uiState is AuthState.Authenticated) {
            onSignUpClick()
        }
    }

    var fullName by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var termsAccepted by remember { mutableStateOf(false) }
    
    // Validation Errors
    var nameError by remember { mutableStateOf<String?>(null) }
    var emailError by remember { mutableStateOf<String?>(null) }
    var passwordError by remember { mutableStateOf<String?>(null) }
    var confirmError by remember { mutableStateOf<String?>(null) }
    var termsError by remember { mutableStateOf<String?>(null) }

    fun validate(): Boolean {
        var isValid = true
        if (fullName.isBlank()) { nameError = "Full name is required"; isValid = false } else nameError = null
        
        val emailRegex = "^[A-Za-z](.*)([@]{1})(.{1,})(\\.)(.{1,})".toRegex()
        if (email.isBlank() || !emailRegex.matches(email)) { emailError = "Valid email is required"; isValid = false } else emailError = null
        
        if (password.length < 6) { 
            passwordError = "Password must be at least 6 characters"
            isValid = false 
        } else passwordError = null
        
        if (password != confirmPassword) { confirmError = "Passwords do not match"; isValid = false } else confirmError = null
        
        if (!termsAccepted) { termsError = "You must accept the terms & clinical privacy policy"; isValid = false } else termsError = null
        
        return isValid
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundClinical)
            .safeDrawingPadding()
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp, vertical = 12.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(16.dp))

            // Brand Header matching Web
            Text(
                text = "ORTHOFINIX.AI",
                color = BrandDarkNavy,
                fontWeight = FontWeight.Black,
                fontSize = 22.sp,
                letterSpacing = 2.sp
            )
            Text(
                text = "Clinical-Grade Orthodontic Intelligence",
                color = BrandGray,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Main Registration Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                shape = RoundedCornerShape(16.dp),
                border = BorderStroke(1.dp, BorderClinical)
            ) {
                Column(modifier = Modifier.padding(24.dp)) {

                    Text(
                        text = "Create Doctor Account",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandDarkNavy
                    )
                    Text(
                        text = "Join the OrthofinixAI orthodontic community.",
                        fontSize = 12.sp,
                        color = BrandGray,
                        modifier = Modifier.padding(top = 2.dp)
                    )

                    Spacer(modifier = Modifier.height(18.dp))

                    // Full Doctor Name
                    Text(
                        "Full Doctor Name",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandDarkNavy
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    OutlinedTextField(
                        value = fullName,
                        onValueChange = { fullName = it; nameError = null },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("Dr. Alexander Wright, DDS", color = BrandGray.copy(alpha = 0.5f), fontSize = 13.sp) },
                        leadingIcon = { Icon(Icons.Default.Person, contentDescription = null, tint = BrandSkyBlue) },
                        isError = nameError != null,
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = BrandDarkNavy,
                            unfocusedTextColor = BrandDarkNavy,
                            focusedBorderColor = BrandSkyBlue,
                            unfocusedBorderColor = BorderClinical,
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White
                        )
                    )
                    if (nameError != null) {
                        Text(nameError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(top = 2.dp))
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Work Email Address
                    Text(
                        "Work Email Address",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandDarkNavy
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    OutlinedTextField(
                        value = email,
                        onValueChange = { email = it; emailError = null },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("doctor@orthoclinic.com", color = BrandGray.copy(alpha = 0.5f), fontSize = 13.sp) },
                        leadingIcon = { Icon(Icons.Default.Email, contentDescription = null, tint = BrandSkyBlue) },
                        isError = emailError != null,
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = BrandDarkNavy,
                            unfocusedTextColor = BrandDarkNavy,
                            focusedBorderColor = BrandSkyBlue,
                            unfocusedBorderColor = BorderClinical,
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White
                        )
                    )
                    if (emailError != null) {
                        Text(emailError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(top = 2.dp))
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Password
                    Text(
                        "Password",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandDarkNavy
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it; passwordError = null },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("••••••••", color = BrandGray.copy(alpha = 0.5f), fontSize = 13.sp) },
                        leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null, tint = BrandSkyBlue) },
                        trailingIcon = {
                            val icon = if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff
                            IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                Icon(icon, contentDescription = null, tint = BrandGray)
                            }
                        },
                        visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                        isError = passwordError != null,
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = BrandDarkNavy,
                            unfocusedTextColor = BrandDarkNavy,
                            focusedBorderColor = BrandSkyBlue,
                            unfocusedBorderColor = BorderClinical,
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White
                        )
                    )
                    if (passwordError != null) {
                        Text(passwordError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(top = 2.dp))
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Confirm Password
                    Text(
                        "Confirm Password",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandDarkNavy
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    OutlinedTextField(
                        value = confirmPassword,
                        onValueChange = { confirmPassword = it; confirmError = null },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("••••••••", color = BrandGray.copy(alpha = 0.5f), fontSize = 13.sp) },
                        leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null, tint = BrandSkyBlue) },
                        visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                        isError = confirmError != null,
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = BrandDarkNavy,
                            unfocusedTextColor = BrandDarkNavy,
                            focusedBorderColor = BrandSkyBlue,
                            unfocusedBorderColor = BorderClinical,
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White
                        )
                    )
                    if (confirmError != null) {
                        Text(confirmError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(top = 2.dp))
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Terms Checkbox
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Checkbox(
                            checked = termsAccepted,
                            onCheckedChange = { termsAccepted = it; termsError = null },
                            colors = CheckboxDefaults.colors(checkedColor = BrandSkyBlue)
                        )
                        Text(
                            "I agree to the Terms of Service and Clinical Privacy Policy",
                            fontSize = 12.sp,
                            color = BrandGray,
                            lineHeight = 16.sp
                        )
                    }
                    if (termsError != null) {
                        Text(termsError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(start = 12.dp, top = 2.dp))
                    }

                    Spacer(modifier = Modifier.height(18.dp))

                    // Complete Registration Button
                    val isLoading = uiState is AuthState.Loading
                    Button(
                        onClick = {
                            if (validate()) {
                                viewModel.signUp(email, password, fullName)
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                        contentPadding = PaddingValues()
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(
                                    Brush.horizontalGradient(
                                        listOf(BrandNavy, BrandSkyBlue)
                                    ),
                                    shape = RoundedCornerShape(12.dp)
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            if (isLoading) {
                                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(20.dp))
                            } else {
                                Text(
                                    "Complete Registration",
                                    color = Color.White,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Already have account link
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Already have a clinic account? ", fontSize = 12.sp, color = BrandGray)
                        TextButton(onClick = onSignInClick, contentPadding = PaddingValues(0.dp)) {
                            Text("Sign In", color = BrandSkyBlue, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
