package com.example.orthofinixai.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.components.BrandedTopBar
import com.example.orthofinixai.ui.components.MainBottomBar
import com.example.orthofinixai.ui.navigation.Screen
import com.example.orthofinixai.ui.theme.BrandGreen
import com.example.orthofinixai.ui.theme.ThemePreferences

import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onBack: (() -> Unit)? = null,
    onBottomNav: (String) -> Unit = {}
) {
    val context = LocalContext.current
    var notificationsEnabled by remember { mutableStateOf(true) }
    var darkMode by remember { mutableStateOf(ThemePreferences.darkMode.value) }

    Scaffold(
        topBar = { BrandedTopBar("Settings", onBack = onBack) },
        bottomBar = {
            MainBottomBar(currentRoute = Screen.Settings.route, onNavigate = onBottomNav)
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text("General", fontWeight = FontWeight.Bold, color = BrandGreen, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))
            SettingToggleItem("Push Notifications", notificationsEnabled) { notificationsEnabled = it }
            SettingToggleItem("Dark Mode", darkMode) {
                darkMode = it
                ThemePreferences.setDarkMode(context, it)
            }
            Spacer(modifier = Modifier.height(24.dp))
            Text("About", fontWeight = FontWeight.Bold, color = BrandGreen, fontSize = 14.sp)
            SettingNavigationItem("OrthofinixAI v1.0.0", Icons.Default.Info)
            SettingNavigationItem("On-device AI • Offline reports", Icons.Default.Memory)
        }
    }
}

@Composable
fun SettingToggleItem(label: String, checked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, fontSize = 16.sp)
        Switch(checked = checked, onCheckedChange = onCheckedChange, colors = SwitchDefaults.colors(checkedThumbColor = BrandGreen))
    }
}

@Composable
fun SettingNavigationItem(label: String, icon: androidx.compose.ui.graphics.vector.ImageVector) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(20.dp))
        Spacer(modifier = Modifier.width(16.dp))
        Text(label, fontSize = 16.sp, modifier = Modifier.weight(1f))
    }
}
