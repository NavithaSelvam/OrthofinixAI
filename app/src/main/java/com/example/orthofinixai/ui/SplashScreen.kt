package com.example.orthofinixai.ui

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.orthofinixai.ui.theme.*
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(
    isLoggedIn: Boolean = false,
    onTimeout: () -> Unit
) {
    var progress by remember { mutableFloatStateOf(0f) }
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "logoPulse"
    )

    LaunchedEffect(Unit) {
        for (i in 1..20) {
            delay(60)
            progress = i / 20f
        }
        delay(300)
        onTimeout()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color.White,
                        Color(0xFFF0F7FF),
                        Color(0xFFE8F5E9)
                    )
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(24.dp)
        ) {
            // Brand Logo Box with Emerald Sparkle Badge
            Box(
                modifier = Modifier
                    .scale(pulseScale)
                    .size(96.dp),
                contentAlignment = Alignment.Center
            ) {
                // Outer Gradient Border Container
                Box(
                    modifier = Modifier
                        .size(88.dp)
                        .shadow(12.dp, RoundedCornerShape(24.dp), spotColor = Color(0x330284C7))
                        .background(
                            Brush.linearGradient(
                                colors = listOf(Color(0xFF0284C7), Color(0xFF14B8A6), Color(0xFF10B981))
                            ),
                            shape = RoundedCornerShape(24.dp)
                        )
                        .padding(2.dp),
                    contentAlignment = Alignment.Center
                ) {
                    // Inner White Card
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(Color.White, RoundedCornerShape(22.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "O",
                            fontSize = 38.sp,
                            fontWeight = FontWeight.Black,
                            color = Color(0xFF0284C7)
                        )
                    }
                }

                // Sparkle Badge
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .size(24.dp)
                        .background(Color(0xFF10B981), CircleShape)
                        .border(1.5.dp, Color.White, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.AutoAwesome,
                        contentDescription = "Sparkle",
                        tint = Color.White,
                        modifier = Modifier.size(13.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Title: OrthofinixAI
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "Orthofinix",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Black,
                    color = BrandDarkNavy
                )
                Text(
                    text = "AI",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Black,
                    color = Color(0xFF0284C7)
                )
            }

            Spacer(modifier = Modifier.height(6.dp))

            // Subtitle Tagline
            Text(
                text = "AI-POWERED ORTHODONTIC ASSESSMENT",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = BrandGray,
                letterSpacing = 0.8.sp
            )

            Spacer(modifier = Modifier.height(36.dp))

            // Gradient Progress Bar
            Box(
                modifier = Modifier
                    .fillMaxWidth(0.6f)
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp))
                    .background(Color(0xFFE2E8F0))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(progress)
                        .background(
                            Brush.horizontalGradient(
                                colors = listOf(Color(0xFF0284C7), Color(0xFF10B981))
                            ),
                            RoundedCornerShape(3.dp)
                        )
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Status Progress Text
            Text(
                text = when {
                    progress < 0.3f -> "Initializing clinical AI engine..."
                    progress < 0.6f -> "Loading orthodontic finishing models..."
                    progress < 0.9f -> "Preparing analysis pipeline & Firestore..."
                    else -> "Ready"
                },
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
                color = BrandGray,
                textAlign = TextAlign.Center
            )
        }

        // Bottom Footer Version Info
        Text(
            text = "Version 2.4.0 • Clinical CE & ABO Framework",
            fontSize = 10.sp,
            fontWeight = FontWeight.Medium,
            color = Color(0xFF94A3B8),
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 24.dp)
        )
    }
}
