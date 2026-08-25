package com.example.orthofinixai.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.AddAPhoto
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.orthofinixai.ui.theme.BorderColor
import com.example.orthofinixai.ui.theme.BrandGreen
import com.example.orthofinixai.ui.theme.BrandNavy
import com.example.orthofinixai.ui.theme.TextGray
import com.example.orthofinixai.ui.viewmodel.SharedCaseViewModel

private val photoViews = listOf(
    "Front View",
    "Left Side",
    "Right Side",
    "Upper Arch",
    "Lower Arch",
    "Smile",
    "Teeth Close",
    "Jaw Alignment",
    "Extra View"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PhotoUploadScreen(
    onNext: () -> Unit, 
    onBack: () -> Unit,
    viewModel: SharedCaseViewModel
) {

    val images = viewModel.clinicalPhotos

    var activeIndex by remember { mutableIntStateOf(-1) }

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        if (uri != null && activeIndex != -1) {
            images[activeIndex] = uri
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Upload Clinical Photos",
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { padding ->

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {

            LinearProgressIndicator(
                progress = { 0.75f },
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(4.dp)),
                color = BrandGreen,
                trackColor = Color(0xFFE5E7EB)
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                "Step 3 of 4",
                color = BrandGreen,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp
            )

            Text(
                "Upload 5-9 high-quality intraoral views",
                color = TextGray,
                fontSize = 16.sp
            )

            Spacer(modifier = Modifier.height(24.dp))

            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier.weight(1f),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                itemsIndexed(photoViews) { index, view ->
                    PhotoUploadBox(
                        label = view,
                        imageUri = images[index],
                        onClick = {
                            activeIndex = index
                            launcher.launch("image/*")
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            val uploadedCount = images.count { it != null }
            val canProceed = uploadedCount >= 5

            Button(
                onClick = onNext,
                enabled = canProceed,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = BrandGreen,
                    disabledContainerColor = Color.LightGray
                )
            ) {
                Text(
                    if (canProceed)
                        "Proceed to OPG Upload ($uploadedCount/9)"
                    else
                        "Upload at least 5 photos ($uploadedCount/9)",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun PhotoUploadBox(
    label: String,
    imageUri: Uri?,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(150.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(Color(0xFFF9FAFB))
            .border(
                width = if (imageUri != null) 2.dp else 1.dp,
                color = if (imageUri != null) BrandGreen else BorderColor,
                shape = RoundedCornerShape(16.dp)
            )
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {

        if (imageUri != null) {

            AsyncImage(
                model = imageUri,
                contentDescription = label,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.2f))
            )

            Icon(
                Icons.Default.CheckCircle,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(12.dp)
                    .size(24.dp)
            )

        } else {

            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier.padding(12.dp)
            ) {

                Icon(
                    Icons.Default.AddAPhoto,
                    contentDescription = null,
                    tint = TextGray,
                    modifier = Modifier.size(36.dp)
                )

                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    label,
                    fontSize = 13.sp,
                    color = Color.Black,
                    fontWeight = FontWeight.SemiBold,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}