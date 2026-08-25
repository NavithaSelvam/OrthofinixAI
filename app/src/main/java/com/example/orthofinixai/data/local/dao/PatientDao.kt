package com.example.orthofinixai.data.local.dao

import androidx.room.*
import com.example.orthofinixai.data.local.entity.PatientEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface PatientDao {
    @Query("SELECT * FROM patients WHERE userId = :userId ORDER BY createdAt DESC")
    fun getPatientsForUser(userId: String): Flow<List<PatientEntity>>

    @Query("SELECT * FROM patients ORDER BY createdAt DESC")
    fun getAllPatients(): Flow<List<PatientEntity>>

    @Query("SELECT * FROM patients ORDER BY createdAt DESC")
    suspend fun getAllPatientsList(): List<PatientEntity>

    @Query("SELECT * FROM patients WHERE userId = :userId AND id = :id")
    suspend fun getPatient(userId: String, id: String): PatientEntity?

    @Query("SELECT * FROM patients WHERE id = :id LIMIT 1")
    suspend fun getPatientById(id: String): PatientEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPatient(patient: PatientEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(patients: List<PatientEntity>)

    @Update
    suspend fun updatePatient(patient: PatientEntity)

    @Delete
    suspend fun deletePatient(patient: PatientEntity)

    @Query("DELETE FROM patients WHERE id = :id OR name = :id OR LOWER(name) = LOWER(:id)")
    suspend fun deletePatientById(id: String)

    @Query("DELETE FROM patients WHERE name = :name OR LOWER(name) = LOWER(:name)")
    suspend fun deletePatientByName(name: String)

    @Query("SELECT * FROM patients WHERE userId = :userId AND name LIKE '%' || :query || '%'")
    fun searchPatients(userId: String, query: String): Flow<List<PatientEntity>>
}
