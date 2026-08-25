package com.example.orthofinixai.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(tableName = "reports", indices = [Index("userId"), Index("caseId")])
data class ReportEntity(
    @PrimaryKey val id: String,
    val userId: String,
    val caseId: String,
    val patientId: String,
    val viewType: String,
    val reportJson: String,
    val aboScore: Float,
    val andrewsScore: Float,
    val archSymmetryScore: Float,
    val rootAngulationScore: Float,
    val confidenceScore: Float,
    val imagePath: String = "",
    val createdAt: Long = System.currentTimeMillis()
)
