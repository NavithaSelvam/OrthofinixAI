package com.example.orthofinixai.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = BrandNavy,
    onPrimary = Color.White,
    secondary = BrandGreen,
    tertiary = BrandTeal,
    background = BackgroundClinical,
    surface = SurfaceClinical,
    onBackground = ClinicalDeepNavy,
    onSurface = ClinicalDeepNavy
)

private val DarkColors = darkColorScheme(
    primary = BrandTeal,
    onPrimary = Color.White,
    secondary = BrandGreen,
    background = Color(0xFF0F172A),
    surface = Color(0xFF1E293B),
    onBackground = Color(0xFFF1F5F9),
    onSurface = Color(0xFFF1F5F9)
)

@Composable
fun OrthofinixAiTheme(
    darkTheme: Boolean = ThemePreferences.darkMode.value || isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = if (darkTheme) DarkColors else LightColors
    MaterialTheme(colorScheme = colors, typography = Typography, content = content)
}
