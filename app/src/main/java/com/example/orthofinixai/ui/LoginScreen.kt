package com.example.orthofinixai.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.R
import com.example.orthofinixai.ui.theme.BorderColor
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.orthofinixai.ui.viewmodel.AuthViewModel
import com.example.orthofinixai.ui.viewmodel.AuthState
import com.example.orthofinixai.ui.theme.PrimaryGreen
import com.example.orthofinixai.ui.theme.TextGray
import com.example.orthofinixai.ui.theme.BorderColor
import com.example.orthofinixai.ui.theme.BackgroundClinical
import com.example.orthofinixai.ui.theme.ClinicalDeepNavy
import com.example.orthofinixai.ui.theme.ClinicalSlate
import com.example.orthofinixai.ui.theme.SurfaceClinical
import com.example.orthofinixai.ui.theme.BorderClinical
import com.example.orthofinixai.ui.theme.ClinicalSkyBlue
@Composable
fun LoginScreen(
    onSignInClick: () -> Unit,
    onSignUpClick: () -> Unit,
    onForgotPasswordClick: () -> Unit,
    onGoogleSignInClick: () -> Unit = {},
    viewModel: AuthViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(uiState) {
        if (uiState is AuthState.Authenticated) {
            onSignInClick()
        }
    }

    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var rememberMe by remember { mutableStateOf(true) }
    
    // Validation Errors
    var emailError by remember { mutableStateOf<String?>(null) }
    var passwordError by remember { mutableStateOf<String?>(null) }

    fun validate(): Boolean {
        var isValid = true
        if (email.isBlank()) {
            emailError = "Email is required"
            isValid = false
        } else if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            emailError = "Please enter a valid email address"
            isValid = false
        } else {
            emailError = null
        }

        if (password.length < 6) {
            passwordError = "Password must be at least 6 characters"
            isValid = false
        } else {
            passwordError = null
        }
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

        Image(
            painter = painterResource(id = R.drawable.orthofinix_logo),
            contentDescription = "Orthofinix Logo",
            modifier = Modifier.fillMaxWidth(0.75f).aspectRatio(3.2f)
        )

        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "ORTHOFINIX.AI",
            color = ClinicalDeepNavy,
            fontWeight = FontWeight.Black,
            fontSize = 22.sp,
            letterSpacing = 2.sp
        )
        Text(
            text = "Clinical-Grade Orthodontic Intelligence",
            color = ClinicalSlate,
            fontSize = 13.sp,
            fontWeight = FontWeight.Medium
        )

        Spacer(modifier = Modifier.height(24.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceClinical),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
            shape = RoundedCornerShape(16.dp),
            border = BorderStroke(1.dp, BorderClinical)
        ) {
            Column(modifier = Modifier.padding(24.dp)) {

                Text(
                    text = "Welcome Back",
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    color = ClinicalDeepNavy
                )

                Spacer(modifier = Modifier.height(20.dp))

                Text(
                    "Email Address",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                    color = ClinicalDeepNavy
                )
                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = email,
                    onValueChange = { email = it; emailError = null },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("dr.smith@orthofinix.ai", color = ClinicalSlate.copy(alpha = 0.5f)) },
                    leadingIcon = { Icon(Icons.Default.Email, contentDescription = null, tint = ClinicalSkyBlue) },
                    isError = emailError != null,
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = ClinicalDeepNavy,
                        unfocusedTextColor = ClinicalDeepNavy,
                        focusedBorderColor = ClinicalSkyBlue,
                        unfocusedBorderColor = BorderClinical,
                        focusedContainerColor = Color.White,
                        unfocusedContainerColor = Color.White
                    )
                )
                if (emailError != null) {
                    Text(emailError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "Password",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = ClinicalDeepNavy
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Checkbox(
                            checked = rememberMe,
                            onCheckedChange = { rememberMe = it },
                            colors = CheckboxDefaults.colors(checkedColor = ClinicalSkyBlue)
                        )
                        Text("Remember Me", fontSize = 13.sp, color = ClinicalSlate)
                    }
                    TextButton(onClick = onForgotPasswordClick, contentPadding = PaddingValues(0.dp)) {
                        Text("Forgot Password?", color = ClinicalSkyBlue, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                    }
                }

                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it; passwordError = null },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("••••••••", color = ClinicalSlate.copy(alpha = 0.5f)) },
                    leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null, tint = ClinicalSkyBlue) },
                    trailingIcon = {
                        val icon = if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff
                        IconButton(onClick = { passwordVisible = !passwordVisible }) {
                            Icon(icon, contentDescription = null, tint = ClinicalSlate)
                        }
                    },
                    visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    isError = passwordError != null,
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = ClinicalDeepNavy,
                        unfocusedTextColor = ClinicalDeepNavy,
                        focusedBorderColor = ClinicalSkyBlue,
                        unfocusedBorderColor = BorderClinical,
                        focusedContainerColor = Color.White,
                        unfocusedContainerColor = Color.White
                    )
                )
                if (passwordError != null) {
                    Text(passwordError!!, color = Color.Red, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(24.dp))

                if (uiState is AuthState.Error) {
                    Text(
                        (uiState as AuthState.Error).message,
                        color = Color.Red,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }

                Button(
                    onClick = { if (validate()) viewModel.login(email, password) },
                    enabled = uiState !is AuthState.Loading,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = ClinicalDeepNavy)
                ) {
                    if (uiState is AuthState.Loading) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                    } else {
                        Text("Sign In", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    HorizontalDivider(modifier = Modifier.weight(1f), color = BorderClinical)
                    Text(" Or continue with ", modifier = Modifier.padding(horizontal = 8.dp), color = ClinicalSlate, fontSize = 12.sp)
                    HorizontalDivider(modifier = Modifier.weight(1f), color = BorderClinical)
                }

                Spacer(modifier = Modifier.height(20.dp))

                SocialButton(
                    icon = Icons.Default.Person,
                    text = "Continue with Google",
                    onClick = onGoogleSignInClick,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("Don't have an account? ", color = ClinicalSlate)
            TextButton(onClick = onSignUpClick) {
                Text("Sign up", color = ClinicalSkyBlue, fontWeight = FontWeight.Bold)
            }
        }
    }
}
}

@Composable
fun SocialButton(
    icon: ImageVector,
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier.height(50.dp),
        colors = ButtonDefaults.outlinedButtonColors(contentColor = ClinicalDeepNavy),
        border = BorderStroke(1.dp, BorderClinical)
    ) {
        Icon(icon, contentDescription = null, tint = ClinicalSkyBlue)
        Spacer(modifier = Modifier.width(8.dp))
        Text(text, fontWeight = FontWeight.Bold)
    }
}