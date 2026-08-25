package com.example.orthofinixai.ui.viewmodel

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.orthofinixai.data.AnalysisSession
import com.example.orthofinixai.data.model.AIReport
import com.example.orthofinixai.data.repository.AnalysisProgress
import com.example.orthofinixai.data.repository.AnalysisRepository
import com.example.orthofinixai.data.repository.AuthRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

sealed class AnalysisState {
    object Idle : AnalysisState()
    data class Processing(val progress: Float, val message: String) : AnalysisState()
    data class Success(val report: AIReport) : AnalysisState()
    data class Error(val message: String) : AnalysisState()
}

class AnalysisViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AnalysisRepository(application.applicationContext)

    private val _uiState = MutableStateFlow<AnalysisState>(AnalysisState.Idle)
    val uiState: StateFlow<AnalysisState> = _uiState.asStateFlow()

    fun startAnalysis(
        caseId: String,
        patientName: String,
        dob: String,
        gender: String,
        imageUri: Uri?,
        imageBytes: ByteArray,
        viewType: String
    ) {
        viewModelScope.launch {
            try {
                _uiState.value = AnalysisState.Processing(0.02f, "Initializing clinical vision pipeline...")
                ensureSession()
                AnalysisSession.imageUri = imageUri

                repository.analyzeImageWithProgress(
                    caseId = caseId,
                    imageBytes = imageBytes,
                    patientName = patientName,
                    dob = dob,
                    gender = gender,
                    imageUri = imageUri,
                    viewType = viewType
                )
                .catch { e ->
                    if (e is CancellationException) throw e
                    _uiState.value = AnalysisState.Error(e.message ?: "Analysis failed")
                }
                .collect { progress ->
                    when (progress) {
                        is AnalysisProgress.Step -> {
                            _uiState.value = AnalysisState.Processing(
                                progress.progress.coerceIn(0f, 0.99f),
                                progress.message
                            )
                        }
                        is AnalysisProgress.Complete -> {
                            _uiState.value = AnalysisState.Processing(1f, "Clinical report generated")
                            delay(300)
                            _uiState.value = AnalysisState.Success(progress.report)
                        }
                        is AnalysisProgress.Failed -> {
                            _uiState.value = AnalysisState.Error(progress.error)
                        }
                    }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.value = AnalysisState.Error(e.message ?: "Analysis failed")
            }
        }
    }

    fun uploadAndAnalyze(
        caseId: String,
        imageBytes: ByteArray,
        patientName: String,
        dob: String,
        gender: String,
        imageUri: Uri?,
        viewType: String = "frontal"
    ) {
        startAnalysis(caseId, patientName, dob, gender, imageUri, imageBytes, viewType)
    }

    fun loadReport(caseId: String) {
        viewModelScope.launch {
            _uiState.value = AnalysisState.Processing(0.3f, "Loading saved report...")
            try {
                repository.getReport(caseId)
                    .catch { e ->
                        if (e is CancellationException) throw e
                        _uiState.value = AnalysisState.Error(e.message ?: "Failed to load report")
                    }
                    .collect { result ->
                        result.onSuccess { report ->
                            com.example.orthofinixai.data.AnalysisSession.lastReport = report
                            _uiState.value = AnalysisState.Success(report)
                        }.onFailure {
                            _uiState.value = AnalysisState.Error(it.message ?: "Failed to load report")
                        }
                    }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.value = AnalysisState.Error(e.message ?: "Failed to load report")
            }
        }
    }

    fun loadDemoReport() {
        val report = com.example.orthofinixai.data.DemoCaseProvider.buildDemoReport()
        com.example.orthofinixai.data.AnalysisSession.lastReport = report
        _uiState.value = AnalysisState.Success(report)
    }

    fun reset() {
        _uiState.value = AnalysisState.Idle
    }

    private fun emitProgress(fraction: Float, message: String) {
        _uiState.value = AnalysisState.Processing(fraction.coerceIn(0f, 1f), message)
    }

    private fun ensureSession() {
        val context = getApplication<Application>().applicationContext
        if (com.example.orthofinixai.data.SessionManager.currentUserId == null) {
            com.example.orthofinixai.data.SessionManager.restore(context)
        }
        if (com.example.orthofinixai.data.SessionManager.currentUserId == null) {
            val uid = AuthRepository.getCurrentUserId()
            com.example.orthofinixai.data.SessionManager.onLogin(
                com.example.orthofinixai.data.model.User(uid, "local@orthofinix.ai", "Doctor"),
                context
            )
        }
    }


}
