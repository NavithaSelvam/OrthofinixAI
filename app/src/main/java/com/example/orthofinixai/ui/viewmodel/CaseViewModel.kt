package com.example.orthofinixai.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.repository.CaseRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

sealed class CaseListState {
    object Loading : CaseListState()
    data class Success(val cases: List<SavedCase>) : CaseListState()
    data class Error(val message: String) : CaseListState()
}

class CaseViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = CaseRepository(application.applicationContext)
    private val searchQuery = MutableStateFlow("")

    val uiState: StateFlow<CaseListState> = combine(
        repository.getCasesFlow(),
        searchQuery
    ) { allCases, query ->
        val filtered = if (query.isBlank()) {
            allCases
        } else {
            allCases.filter {
                it.patientName.contains(query, ignoreCase = true) ||
                it.id.contains(query, ignoreCase = true)
            }
        }
        CaseListState.Success(filtered) as CaseListState
    }.catch { e ->
        if (e is kotlinx.coroutines.CancellationException) throw e
        emit(CaseListState.Error(e.message ?: "Failed to load cases"))
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.Eagerly,
        initialValue = CaseListState.Loading
    )

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            repository.syncCasesFromCloud()
        }
    }

    fun loadCases() {
        refresh()
    }

    fun deleteCase(caseId: String) {
        viewModelScope.launch {
            repository.deleteCase(caseId)
        }
    }

    fun search(query: String) {
        searchQuery.value = query
    }
}
