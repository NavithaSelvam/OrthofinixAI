package com.example.orthofinixai.data.model

data class Patient(
    val id: String = "",
    val name: String = "",
    val age: Int = 0,
    val dateOfBirth: String = "",
    val gender: String = "",
    val phone: String = "",
    val email: String = "",
    val doctorName: String = "",
    val hospital: String = "",
    val diagnosis: String = "",
    val treatmentDate: String = "",
    val notes: String = "",
    val imageUrls: List<String> = emptyList(),
    val doctorId: String = "",
    val createdAt: Long = System.currentTimeMillis()
)

data class PatientCreate(
    val name: String,
    val dateOfBirth: String,
    val gender: String,
    val phone: String,
    val email: String,
    val doctorName: String,
    val hospital: String,
    val diagnosis: String,
    val treatmentDate: String,
    val notes: String
)
