package com.example.orthofinixai.util

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import java.io.File
import java.io.FileOutputStream

object ImageStorageUtil {

    fun saveImage(context: Context, userId: String, caseId: String, sourceUri: Uri?): String? {
        if (sourceUri == null) return null
        return try {
            val dir = File(context.filesDir, "cases/$userId").apply { mkdirs() }
            val file = File(dir, "$caseId.jpg")
            context.contentResolver.openInputStream(sourceUri)?.use { input ->
                FileOutputStream(file).use { output -> input.copyTo(output) }
            }
            file.absolutePath
        } catch (_: Exception) {
            null
        }
    }

    fun saveImageBytes(context: Context, userId: String, caseId: String, bytes: ByteArray): String? {
        if (bytes.isEmpty()) return null
        return try {
            val dir = File(context.filesDir, "cases/$userId").apply { mkdirs() }
            val file = File(dir, "$caseId.jpg")
            FileOutputStream(file).use { it.write(bytes) }
            file.absolutePath
        } catch (_: Exception) {
            null
        }
    }

    fun loadBitmap(path: String?): Bitmap? {
        if (path.isNullOrBlank()) return null
        val f = File(path)
        return if (f.exists()) BitmapFactory.decodeFile(path) else null
    }

    fun deleteCaseImages(context: Context, userId: String, caseId: String) {
        File(context.filesDir, "cases/$userId/$caseId.jpg").delete()
    }
}
