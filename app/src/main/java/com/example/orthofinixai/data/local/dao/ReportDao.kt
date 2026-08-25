package com.example.orthofinixai.data.local.dao

import androidx.room.*
import com.example.orthofinixai.data.local.entity.ReportEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ReportDao {
    @Query("SELECT * FROM reports WHERE userId = :userId AND caseId = :caseId ORDER BY createdAt DESC LIMIT 1")
    suspend fun getLatestByCase(userId: String, caseId: String): ReportEntity?

    @Query("SELECT * FROM reports WHERE caseId = :caseId ORDER BY createdAt DESC LIMIT 1")
    suspend fun getLatestByCaseId(caseId: String): ReportEntity?

    @Query("SELECT * FROM reports WHERE userId = :userId ORDER BY createdAt DESC")
    fun getReportsForUser(userId: String): Flow<List<ReportEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertReport(report: ReportEntity)

    @Query("DELETE FROM reports WHERE userId = :userId AND caseId = :caseId")
    suspend fun deleteByCase(userId: String, caseId: String)

    @Query("DELETE FROM reports WHERE caseId = :caseId")
    suspend fun deleteByCaseId(caseId: String)
}
