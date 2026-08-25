package com.example.orthofinixai.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Book
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.style.TextOverflow
import com.example.orthofinixai.ui.navigation.Screen
import com.example.orthofinixai.ui.theme.ClinicalDeepNavy
import com.example.orthofinixai.ui.theme.ClinicalSkyBlue

data class BottomNavItem(
    val route: String,
    val label: String,
    val icon: ImageVector
)

private val mainNavItems = listOf(
    BottomNavItem(Screen.Dashboard.route, "Home", Icons.Default.Home),
    BottomNavItem(Screen.CaseList.route, "Cases", Icons.Default.Folder),
    BottomNavItem(Screen.GuidelinesLibrary.route, "Guidelines", Icons.Default.Book),
    BottomNavItem(Screen.Settings.route, "Settings", Icons.Default.Settings),
    BottomNavItem(Screen.Profile.route, "Profile", Icons.Default.Person)
)

@Composable
fun MainBottomBar(
    currentRoute: String,
    onNavigate: (String) -> Unit
) {
    NavigationBar(
        containerColor = MaterialTheme.colorScheme.surface,
        windowInsets = NavigationBarDefaults.windowInsets
    ) {
        mainNavItems.forEach { item ->
            val selected = currentRoute == item.route
            NavigationBarItem(
                selected = selected,
                onClick = { if (!selected) onNavigate(item.route) },
                icon = { Icon(item.icon, contentDescription = item.label) },
                label = { Text(item.label, maxLines = 1, overflow = TextOverflow.Ellipsis) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = ClinicalSkyBlue,
                    selectedTextColor = ClinicalDeepNavy,
                    indicatorColor = ClinicalSkyBlue.copy(alpha = 0.12f)
                )
            )
        }
    }
}
