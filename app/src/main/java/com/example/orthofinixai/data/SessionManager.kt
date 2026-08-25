package com.example.orthofinixai.data

import android.content.Context
import com.example.orthofinixai.data.model.User
import kotlinx.coroutines.launch

object SessionManager {
    private const val PREFS = "orthofinix_session"
    private const val KEY_UID = "uid"
    private const val KEY_EMAIL = "email"
    private const val KEY_NAME = "name"

    var currentUserId: String? = null
        private set
    var currentUser: User? = null
        private set

    fun requireUserId(): String =
        currentUserId ?: throw IllegalStateException("Sign in required to access clinical data")

    fun restore(context: Context): Boolean {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val uid = prefs.getString(KEY_UID, null) ?: return false
        currentUserId = uid
        currentUser = User(
            uid = uid,
            email = prefs.getString(KEY_EMAIL, "") ?: "",
            displayName = prefs.getString(KEY_NAME, "Doctor") ?: "Doctor"
        )
        return true
    }

    fun onLogin(user: User, context: Context) {
        currentUserId = user.uid
        currentUser = user
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putString(KEY_UID, user.uid)
            .putString(KEY_EMAIL, user.email)
            .putString(KEY_NAME, user.displayName ?: "Doctor")
            .apply()

        // Clean stale local records that do not belong to this user
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
            try {
                val db = com.example.orthofinixai.data.local.OrthofinixDatabase.getInstance(context)
                db.caseDao().deleteCasesNotForUser(user.uid)
            } catch (_: Exception) {}
        }
    }

    fun onLogout(context: Context) {
        val oldUid = currentUserId
        currentUserId = null
        currentUser = null
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().clear().apply()

        // Purge local database on logout for security & privacy
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
            try {
                val db = com.example.orthofinixai.data.local.OrthofinixDatabase.getInstance(context)
                db.caseDao().deleteAllCases()
            } catch (_: Exception) {}
        }
    }
}
