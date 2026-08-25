package com.example.orthofinixai.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.orthofinixai.data.model.User
import com.example.orthofinixai.data.repository.AuthRepository
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.firebase.auth.FirebaseAuth
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await

sealed class AuthState {
    object Idle : AuthState()
    object Loading : AuthState()
    data class Authenticated(val user: User) : AuthState()
    data class Error(val message: String) : AuthState()
}

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AuthRepository(application.applicationContext)

    private val _uiState = MutableStateFlow<AuthState>(AuthState.Idle)
    val uiState: StateFlow<AuthState> = _uiState.asStateFlow()

    val googleSignInClient
        get() = repository.getGoogleSignInClient()

    init {
        checkExistingSession()
    }

    fun checkExistingSession() {
        val firebaseUser = FirebaseAuth.getInstance().currentUser

        if (firebaseUser != null) {
            viewModelScope.launch {
                try {
                    firebaseUser.reload().await()

                    val user = repository.restoreSession()

                    if (user != null) {
                        _uiState.value = AuthState.Authenticated(user)
                    } else {
                        _uiState.value = AuthState.Idle
                    }

                } catch (e: Exception) {
                    _uiState.value = AuthState.Idle
                }
            }
        } else {
            _uiState.value = AuthState.Idle
        }
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = AuthState.Loading

            val result = repository.signInWithEmail(email, password)

            result.onSuccess { user ->
                _uiState.value = AuthState.Authenticated(user)
            }

            result.onFailure { error ->
                _uiState.value =
                    AuthState.Error(error.message ?: "Login failed")
            }
        }
    }

    fun signUp(
        email: String,
        password: String,
        displayName: String
    ) {
        viewModelScope.launch {

            _uiState.value = AuthState.Loading

            val result =
                repository.signUpWithEmail(
                    email,
                    password,
                    displayName
                )

            result.onSuccess { user ->
                _uiState.value =
                    AuthState.Authenticated(user)
            }

            result.onFailure { error ->
                _uiState.value =
                    AuthState.Error(
                        error.message ?: "Sign up failed"
                    )
            }
        }
    }

    fun signInWithGoogle(account: GoogleSignInAccount) {

        viewModelScope.launch {

            _uiState.value = AuthState.Loading

            repository.signInWithGoogle(
                account.idToken ?: ""
            ) { result ->

                result.onSuccess { user ->
                    _uiState.value =
                        AuthState.Authenticated(user)
                }

                result.onFailure { error ->
                    _uiState.value =
                        AuthState.Error(
                            error.message
                                ?: "Google Sign In failed"
                        )
                }
            }
        }
    }

    fun resetPassword(
        email: String,
        onResult: (Boolean, String?) -> Unit
    ) {

        repository.sendPasswordResetEmail(email) { result ->

            result.onSuccess {
                onResult(true, null)
            }

            result.onFailure {
                onResult(
                    false,
                    it.message ?: "Could not send reset email"
                )
            }
        }
    }

    fun logout() {
        repository.logout()
        _uiState.value = AuthState.Idle
    }
}