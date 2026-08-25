package com.example.orthofinixai.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.example.orthofinixai.data.local.dao.CaseDao
import com.example.orthofinixai.data.local.dao.PatientDao
import com.example.orthofinixai.data.local.dao.ReportDao
import com.example.orthofinixai.data.local.entity.CaseEntity
import com.example.orthofinixai.data.local.entity.PatientEntity
import com.example.orthofinixai.data.local.entity.ReportEntity

@Database(
    entities = [PatientEntity::class, CaseEntity::class, ReportEntity::class],
    version = 4,
    exportSchema = false
)
abstract class OrthofinixDatabase : RoomDatabase() {
    abstract fun patientDao(): PatientDao
    abstract fun caseDao(): CaseDao
    abstract fun reportDao(): ReportDao

    companion object {
        @Volatile private var INSTANCE: OrthofinixDatabase? = null

        fun getInstance(context: Context): OrthofinixDatabase =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    OrthofinixDatabase::class.java,
                    "orthofinix.db"
                ).fallbackToDestructiveMigration().build().also { INSTANCE = it }
            }
    }
}
