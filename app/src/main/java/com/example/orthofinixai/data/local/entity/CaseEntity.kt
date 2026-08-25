package com.example.orthofinixai.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "cases",
    indices = [Index("userId"), Index("patientId")]
)
data class CaseEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val patientId: String,
    val patientName: String,
    val title: String,
    val viewType: String,
    val imagePath: String = "",
    val reportJson: String = "",
    val reportId: String = "",
    val confidenceScore: Float = 0f,
    val aboScore: Float = 0f,
    val andrewsScore: Float = 0f,
    val status: String = "Analyzed",
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
