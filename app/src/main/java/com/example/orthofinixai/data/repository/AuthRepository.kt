package com.example.orthofinixai.data.repository

import android.content.Context
import android.util.Log
import com.example.orthofinixai.R
import com.example.orthofinixai.data.SessionManager
import com.example.orthofinixai.data.model.User
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.auth.GoogleAuthProvider
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext

class AuthRepository(private val context: Context) {

    private val auth: FirebaseAuth = FirebaseAuth.getInstance()
    private val firestore: FirebaseFirestore = FirebaseFirestore.getInstance()
    private val repositoryScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun getGoogleSignInClient(): GoogleSignInClient {
        val optionsBuilder = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestEmail()
            .requestProfile()

        val webClientId = context.getString(R.string.default_web_client_id).trim()
        if (webClientId.isNotEmpty()) {
            optionsBuilder.requestIdToken(webClientId)
        }

        return GoogleSignIn.getClient(context, optionsBuilder.build())
    }

    fun restoreSession(): User? {
        val firebaseUser = auth.currentUser ?: return null
        val user = mapFirebaseUser(firebaseUser)
        SessionManager.onLogin(user, context)
        
        repositoryScope.launch {
            try {
                val doc = firestore.collection("users").document(user.uid).get().await()
                if (!doc.exists()) {
                    saveUserToFirestore(user)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error checking/creating user doc", e)
            }
        }
        return user
    }

    fun signInWithGoogle(idToken: String, onResult: (Result<User>) -> Unit) {
        repositoryScope.launch {
            try {
                val user = if (idToken.isNotBlank()) {
                    val credential = GoogleAuthProvider.getCredential(idToken, null)
                    auth.signInWithCredential(credential).await()
                    val firebaseUser = auth.currentUser
                        ?: throw IllegalStateException("Firebase user missing after Google sign-in")
                    
                    val userObj = mapFirebaseUser(firebaseUser)
                    
                    // Ensure user exists in Firestore
                    saveUserToFirestore(userObj)
                    
                    userObj
                } else {
                    throw IllegalStateException("ID token is blank")
                }
                SessionManager.onLogin(user, context)
                withContext(Dispatchers.Main) {
                    onResult(Result.success(user))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Google sign-in failed", e)
                withContext(Dispatchers.Main) {
                    onResult(Result.failure(e))
                }
            }
        }
    }

    private suspend fun saveUserToFirestore(user: User) {
        try {
            val userMap = hashMapOf(
                "uid" to user.uid,
                "email" to user.email,
                "display_name" to (user.displayName ?: if (user.email.contains("@")) user.email.substringBefore("@") else "Doctor"),
                "role" to user.role,
                "last_active" to java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", java.util.Locale.US).apply {
                    timeZone = java.util.TimeZone.getTimeZone("UTC")
                }.format(java.util.Date())
            )
            firestore.collection("users").document(user.uid).set(userMap, com.google.firebase.firestore.SetOptions.merge()).await()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to save user to Firestore", e)
        }
    }

    fun sendPasswordResetEmail(email: String, onResult: (Result<Unit>) -> Unit) {
        repositoryScope.launch {
            try {
                auth.sendPasswordResetEmail(email).await()
                withContext(Dispatchers.Main) {
                    onResult(Result.success(Unit))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Password reset failed", e)
                withContext(Dispatchers.Main) {
                    onResult(Result.failure(e))
                }
            }
        }
    }

    suspend fun signInWithEmail(email: String, password: String): Result<User> {
        return try {
            auth.signInWithEmailAndPassword(email, password).await()
            val firebaseUser = auth.currentUser
            
            // Force reload to check status accurately
            firebaseUser?.reload()?.await()
            
            val userResult = getCurrentUserResult()
            userResult.getOrNull()?.let { user ->
                saveUserToFirestore(user)
            }
            userResult
        } catch (e: Exception) {
            Log.e(TAG, "Email sign-in failed", e)
            Result.failure(e)
        }
    }

    suspend fun signUpWithEmail(email: String, password: String, displayName: String): Result<User> {
        return try {
            val authResult = auth.createUserWithEmailAndPassword(email, password).await()
            val profileUpdates = com.google.firebase.auth.userProfileChangeRequest {
                this.displayName = displayName
            }
            authResult.user?.updateProfile(profileUpdates)?.await()
            
            val user = mapFirebaseUser(authResult.user!!)
            
            // Save user profile to Firestore
            saveUserToFirestore(user)
            
            Result.success(user)
        } catch (e: Exception) {
            Log.e(TAG, "Email sign-up failed", e)
            Result.failure(e)
        }
    }

    suspend fun getUserIdToken(): String? {
        return try {
            val user = auth.currentUser
            Log.d("AUTH_DEBUG", "Mobile UID: " + user?.uid)
            Log.d(TAG, "Firebase User UID: ${user?.uid}")
            Log.d(TAG, "Firebase Email: ${user?.email}")

            // ALWAYS pass true to force refresh and ensure token is fresh, fall back to cached token on failure
            val tokenResult = try {
                user?.getIdToken(true)?.await()
            } catch (e: Exception) {
                Log.w(TAG, "Force refresh token failed, fetching cached token", e)
                user?.getIdToken(false)?.await()
            }

            val token = tokenResult?.token
            Log.d(TAG, "TOKEN EXISTS: ${token != null}, LENGTH: ${token?.length ?: 0}")
            Log.d("AUTH_DEBUG", "Mobile Token: Bearer " + (token?.take(15) ?: "null") + "...")
            token
        } catch (e: Exception) {
            Log.e(TAG, "Failed to fetch ID token", e)
            null
        }
    }

    private suspend fun getCurrentUserResult(): Result<User> {
        val user = restoreSession()
        if (user != null) {
            return Result.success(user)
        }
        return Result.failure(IllegalStateException("No user signed in"))
    }

    private fun mapFirebaseUser(firebaseUser: FirebaseUser): User {
        return User(
            uid = firebaseUser.uid,
            email = firebaseUser.email ?: "",
            displayName = firebaseUser.displayName ?: "Doctor"
        )
    }

    fun getCurrentUser(): Flow<Result<User>> = flow {
        val restored = restoreSession()
        if (restored != null) {
            emit(Result.success(restored))
        } else {
            emit(Result.failure(IllegalStateException("Not signed in")))
        }
    }.flowOn(Dispatchers.IO)

    fun logout() {
        auth.signOut()
        getGoogleSignInClient().signOut()
        SessionManager.onLogout(context)
    }



    companion object {
        private const val TAG = "AuthRepository"

        @Volatile
        private var appContext: Context? = null

        fun initialize(context: Context) {
            appContext = context.applicationContext
            SessionManager.restore(context.applicationContext)
            val auth = FirebaseAuth.getInstance()
            auth.currentUser?.let { firebaseUser ->
                SessionManager.onLogin(
                    User(
                        uid = firebaseUser.uid,
                        email = firebaseUser.email ?: "",
                        displayName = firebaseUser.displayName ?: "Doctor"
                    ),
                    context.applicationContext
                )
            }
            auth.addAuthStateListener { fbAuth ->
                val user = fbAuth.currentUser
                if (user != null) {
                    SessionManager.onLogin(
                        User(
                            uid = user.uid,
                            email = user.email ?: "",
                            displayName = user.displayName ?: "Doctor"
                        ),
                        context.applicationContext
                    )
                }
            }
        }

        fun getCurrentUserId(): String {
            return FirebaseAuth.getInstance().currentUser?.uid
                ?: SessionManager.currentUserId
                ?: "anonymous"
        }

        fun getCurrentUserEmail(): String {
            return FirebaseAuth.getInstance().currentUser?.email ?: ""
        }
    }

    fun getCurrentUserEmail(): String = Companion.getCurrentUserEmail()
}
