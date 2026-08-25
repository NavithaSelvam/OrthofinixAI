package com.example.orthofinixai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.rememberNavController
import com.example.orthofinixai.data.repository.AuthRepository
import com.example.orthofinixai.ui.navigation.OrthofinixNavGraph
import com.example.orthofinixai.ui.navigation.Screen
import com.example.orthofinixai.ui.theme.OrthofinixAiTheme
import com.example.orthofinixai.ui.theme.ThemePreferences
import com.example.orthofinixai.ui.viewmodel.AuthState
import com.example.orthofinixai.ui.viewmodel.AuthViewModel
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.common.api.ApiException

class MainActivity : ComponentActivity() {

    private val googleSignInLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
        try {
            val account = task.getResult(ApiException::class.java)
            authViewModel?.signInWithGoogle(account)
        } catch (_: ApiException) { }
    }

    private var authViewModel: AuthViewModel? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        ThemePreferences.load(this)
        AuthRepository.initialize(applicationContext)
        try {
            val opts = com.google.firebase.FirebaseApp.getInstance().options
            android.util.Log.d("FIREBASE_DEBUG", "ANDROID FIREBASE CONFIG -> projectId: ${opts.projectId}, appId: ${opts.applicationId}")
        } catch (e: Exception) {
            android.util.Log.e("FIREBASE_DEBUG", "Failed to read Firebase options", e)
        }
        enableEdgeToEdge()

        setContent {
            OrthofinixAiTheme {
                val navController = rememberNavController()
                val authVm: AuthViewModel = viewModel()
                authViewModel = authVm
                val authState by authVm.uiState.collectAsState()

                val startRoute = when (authState) {
                    is AuthState.Authenticated -> Screen.Dashboard.route
                    else -> Screen.Splash.route
                }

                LaunchedEffect(authState) {
                    if (authState is AuthState.Authenticated) {
                        val current = navController.currentDestination?.route
                        if (current == Screen.Login.route || current == Screen.Splash.route) {
                            navController.navigate(Screen.Dashboard.route) {
                                popUpTo(0) { inclusive = true }
                            }
                        }
                    }
                }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    OrthofinixNavGraph(
                        navController = navController,
                        modifier = Modifier.fillMaxSize(),
                        startDestination = startRoute,
                        onGoogleSignInClick = {
                            googleSignInLauncher.launch(authVm.googleSignInClient.signInIntent)
                        }
                    )
                }
            }
        }
    }
}
