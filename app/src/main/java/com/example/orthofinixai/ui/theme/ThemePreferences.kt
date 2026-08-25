package com.example.orthofinixai.ui.theme

import android.content.Context
import androidx.compose.runtime.mutableStateOf

object ThemePreferences {
    private const val PREFS = "orthofinix_theme"
    private const val KEY_DARK = "dark_mode"

    val darkMode = mutableStateOf(false)

    fun load(context: Context) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        darkMode.value = prefs.getBoolean(KEY_DARK, false)
    }

    fun setDarkMode(context: Context, enabled: Boolean) {
        darkMode.value = enabled
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putBoolean(KEY_DARK, enabled).apply()
    }
}
