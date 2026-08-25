package com.example.orthofinixai.data.local.dao

import androidx.room.*
import com.example.orthofinixai.data.local.entity.CaseEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CaseDao {
    @Query("SELECT * FROM cases WHERE userId = :userId ORDER BY createdAt DESC")
    fun getCasesForUser(userId: String): Flow<List<CaseEntity>>

    @Query("SELECT * FROM cases ORDER BY createdAt DESC")
    fun getAllCases(): Flow<List<CaseEntity>>

    @Query("SELECT * FROM cases ORDER BY createdAt DESC")
    suspend fun getAllCasesList(): List<CaseEntity>

    @Query("SELECT * FROM cases WHERE (userId = :userId OR :userId = '') AND (id = :id OR patientId = :id OR reportId = :id OR patientName = :id OR LOWER(patientName) = LOWER(:id)) LIMIT 1")
    suspend fun getCase(userId: String, id: String): CaseEntity?

    @Query("SELECT * FROM cases WHERE id = :id OR patientId = :id OR reportId = :id OR patientName = :id OR LOWER(patientName) = LOWER(:id) LIMIT 1")
    suspend fun getCaseById(id: String): CaseEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCase(caseEntity: CaseEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(cases: List<CaseEntity>)

    @Query("DELETE FROM cases WHERE id = :id OR (userId = :userId AND id = :id) OR patientId = :id OR patientName = :id OR LOWER(patientName) = LOWER(:id)")
    suspend fun deleteCase(userId: String, id: String)

    @Query("DELETE FROM cases WHERE id = :id OR patientId = :id OR reportId = :id OR patientName = :id OR LOWER(patientName) = LOWER(:id)")
    suspend fun deleteCaseById(id: String)

    @Query("DELETE FROM cases WHERE patientName = :name OR LOWER(patientName) = LOWER(:name)")
    suspend fun deleteCaseByName(name: String)

    @Query("SELECT * FROM cases WHERE userId = :userId AND (patientName LIKE '%' || :q || '%' OR id LIKE '%' || :q || '%') ORDER BY createdAt DESC")
    fun searchCases(userId: String, q: String): Flow<List<CaseEntity>>
}
