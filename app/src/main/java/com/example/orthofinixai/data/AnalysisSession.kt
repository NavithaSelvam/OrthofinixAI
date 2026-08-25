package com.example.orthofinixai.data

import android.net.Uri
import com.example.orthofinixai.data.model.AIReport
import com.example.orthofinixai.data.model.ClinicalReport

/** In-memory session for the active case — enables landmark overlay without backend. */
object AnalysisSession {
    var lastReport: AIReport? = null
    var clinicalReport: ClinicalReport? = null
    var imageUri: Uri? = null
    var landmarkPoints: Map<String, Pair<Float, Float>> = emptyMap()
    var detectedTeeth: List<Int> = emptyList()

    fun clear() {
        lastReport = null
        clinicalReport = null
        imageUri = null
        landmarkPoints = emptyMap()
        detectedTeeth = emptyList()
    }
}
