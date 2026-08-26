package com.example.orthofinixai.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.orthofinixai.data.model.Patient
import com.example.orthofinixai.data.model.PatientCreate
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.repository.CaseRepository
import com.example.orthofinixai.data.repository.PatientRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

sealed class PatientState {
    object Idle : PatientState()
    object Loading : PatientState()
    data class Success(val patients: List<Patient>, val savedCases: List<SavedCase> = emptyList()) : PatientState()
    data class Error(val message: String) : PatientState()
}

class PatientViewModel(application: Application) : AndroidViewModel(application) {

    private val patientRepository = PatientRepository(application.applicationContext)
    private val caseRepository = CaseRepository(application.applicationContext)

    val uiState: StateFlow<PatientState> = combine(
        patientRepository.getPatientsFlow(),
        caseRepository.getCasesFlow()
    ) { rawPatients, cases ->
        val patientMap = mutableMapOf<String, Patient>()

        // Add registered patients
        rawPatients.forEach { p ->
            patientMap[p.name.lowercase().trim()] = p
        }

        // Add patients derived from cases if not already present
        cases.forEach { c ->
            val key = c.patientName.lowercase().trim()
            if (!patientMap.containsKey(key)) {
                patientMap[key] = c.patientProfile ?: Patient(
                    id = c.patientId.ifEmpty { c.id },
                    name = c.patientName,
                    age = 25,
                    dateOfBirth = "",
                    gender = "Unknown",
                    phone = "",
                    email = "",
                    doctorName = c.doctorName,
                    hospital = "Orthofinix Clinic",
                    diagnosis = "Orthodontic Finishing Assessment",
                    treatmentDate = "",
                    notes = "",
                    imageUrls = if (c.imagePath.isNotEmpty()) listOf(c.imagePath) else emptyList(),
                    doctorId = "",
                    createdAt = c.createdAt
                )
            }
        }

        PatientState.Success(patientMap.values.toList(), cases) as PatientState
    }.catch { e ->
        if (e is kotlinx.coroutines.CancellationException) throw e
        emit(PatientState.Error(e.message ?: "Failed to load clinical records"))
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = PatientState.Loading
    )

    init {
        fetchPatients()
    }

    fun fetchPatients() {
        viewModelScope.launch {
            patientRepository.syncPatientsFromCloud()
            caseRepository.syncCasesFromCloud()
        }
    }

    fun addPatient(
        name: String, dob: String, gender: String, phone: String = "", 
        email: String = "", doctorName: String = "", hospital: String = "", 
        diagnosis: String = "", treatmentDate: String = "", notes: String = "", 
        onSuccess: (String) -> Unit = {}
    ) {
        viewModelScope.launch {
            patientRepository.createPatient(
                PatientCreate(
                    name = name,
                    dateOfBirth = dob,
                    gender = gender,
                    phone = phone,
                    email = email,
                    doctorName = doctorName,
                    hospital = hospital,
                    diagnosis = diagnosis,
                    treatmentDate = treatmentDate,
                    notes = notes
                )
            )
            .catch { e ->
                if (e is kotlinx.coroutines.CancellationException) throw e
            }
            .collect { result ->
                result.onSuccess { patient ->
                    onSuccess(patient.id)
                    fetchPatients()
                }
            }
        }
    }

    fun deleteCase(caseId: String) {
        viewModelScope.launch {
            caseRepository.deleteCase(caseId)
            patientRepository.deletePatient(caseId)
            fetchPatients()
        }
    }

    fun getSavedCaseForReport(report: com.example.orthofinixai.data.model.AIReport): com.example.orthofinixai.data.model.SavedCase? {
        val state = uiState.value
        if (state is PatientState.Success) {
            return state.savedCases.find { it.id == report.case_id || it.id == report.id }
        }
        return null
    }
}
