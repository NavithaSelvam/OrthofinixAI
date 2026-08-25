package com.example.orthofinixai.ui.viewmodel

import android.net.Uri
import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import com.example.orthofinixai.data.AnalysisSession

class SharedCaseViewModel : ViewModel() {
    var patientName: String = ""
    var dob: String = ""
    var gender: String = ""
    
    val clinicalPhotos = mutableStateListOf<Uri?>()
    var opgPhoto: Uri? = null

    init {
        // Initialize with nulls for 9 photos
        repeat(9) { clinicalPhotos.add(null) }
    }

    fun reset() {
        patientName = ""
        dob = ""
        gender = ""
        clinicalPhotos.clear()
        repeat(9) { clinicalPhotos.add(null) }
        opgPhoto = null
        AnalysisSession.clear()
    }
}
