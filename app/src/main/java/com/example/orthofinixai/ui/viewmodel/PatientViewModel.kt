package com.example.orthofinixai.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.orthofinixai.data.model.Patient
import com.example.orthofinixai.data.model.PatientCreate
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.repository.CaseRepository
import com.example.orthofinixai.data.repository.PatientRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.combine
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

    private val _uiState = MutableStateFlow<PatientState>(PatientState.Idle)
    val uiState: StateFlow<PatientState> = _uiState.asStateFlow()

    fun fetchPatients() {
        viewModelScope.launch {
            _uiState.value = PatientState.Loading
            combine(
                patientRepository.getPatients(),
                caseRepository.observeCases()
            ) { patientsResult, cases ->
                val rawPatients = patientsResult.getOrNull() ?: emptyList()
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

                PatientState.Success(patientMap.values.toList(), cases)
            }
            .catch { e ->
                if (e is kotlinx.coroutines.CancellationException) throw e
                _uiState.value = PatientState.Error(e.message ?: "Failed to load clinical records")
            }
            .collect { state ->
                _uiState.value = state
            }
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
                _uiState.value = PatientState.Error(e.message ?: "Failed to create patient")
            }
            .collect { result ->
                result.onSuccess { patient ->
                    onSuccess(patient.id)
                    fetchPatients()
                }.onFailure { error ->
                    _uiState.value = PatientState.Error(error.message ?: "Failed to create patient")
                }
            }
        }
    }

    fun deleteCase(caseId: String) {
        viewModelScope.launch {
            val current = _uiState.value
            if (current is PatientState.Success) {
                _uiState.value = PatientState.Success(
                    patients = current.patients.filter { it.id != caseId && it.name != caseId },
                    savedCases = current.savedCases.filter { it.id != caseId && it.patientId != caseId && it.patientName != caseId }
                )
            }
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
