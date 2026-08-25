package com.example.orthofinixai

import android.app.Application
import com.example.orthofinixai.data.local.OrthofinixDatabase
import com.example.orthofinixai.data.repository.AuthRepository

class OrthofinixApplication : Application() {
    val database by lazy { OrthofinixDatabase.getInstance(this) }

    override fun onCreate() {
        super.onCreate()
        AuthRepository.initialize(this)
    }
}
