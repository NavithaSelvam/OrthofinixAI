package com.example.orthofinixai.data.model

data class User(
    val uid: String,
    val email: String,
    val displayName: String? = null,
    val role: String = "doctor"
) {
    /** Legacy snake_case accessor used across Compose screens */
    val display_name: String? get() = displayName
}
