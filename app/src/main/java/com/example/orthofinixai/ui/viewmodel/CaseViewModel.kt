package com.example.orthofinixai.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.repository.CaseRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch

sealed class CaseListState {
    object Loading : CaseListState()
    data class Success(val cases: List<SavedCase>) : CaseListState()
    data class Error(val message: String) : CaseListState()
}

class CaseViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = CaseRepository(application.applicationContext)

    private val _uiState = MutableStateFlow<CaseListState>(CaseListState.Loading)
    val uiState: StateFlow<CaseListState> = _uiState.asStateFlow()

    init { loadCases() }

    fun loadCases() {
        viewModelScope.launch {
            _uiState.value = CaseListState.Loading
            repository.observeCases()
                .catch { e ->
                    if (e is kotlinx.coroutines.CancellationException) throw e
                    _uiState.value = CaseListState.Error(e.message ?: "Failed to load cases")
                }
                .collect { _uiState.value = CaseListState.Success(it) }
        }
    }

    fun deleteCase(caseId: String) {
        viewModelScope.launch {
            val current = _uiState.value
            if (current is CaseListState.Success) {
                _uiState.value = CaseListState.Success(
                    current.cases.filter { it.id != caseId }
                )
            }
            repository.deleteCase(caseId)
            loadCases()
        }
    }

    fun search(query: String) {
        viewModelScope.launch {
            if (query.isBlank()) {
                loadCases()
                return@launch
            }
            repository.observeCases()
                .catch { e ->
                    if (e is kotlinx.coroutines.CancellationException) throw e
                    _uiState.value = CaseListState.Error(e.message ?: "Search failed")
                }
                .collect { cases ->
                    val filtered = cases.filter {
                        it.patientName.contains(query, ignoreCase = true) ||
                        it.id.contains(query, ignoreCase = true)
                    }
                    _uiState.value = CaseListState.Success(filtered)
                }
        }
    }
}
