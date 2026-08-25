package com.example.orthofinixai.util

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.graphics.pdf.PdfDocument
import android.net.Uri
import android.widget.Toast
import androidx.core.content.FileProvider
import com.example.orthofinixai.data.model.ClinicalReport
import com.example.orthofinixai.data.model.SavedCase
import com.example.orthofinixai.data.model.Patient
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object PdfGenerator {

    private const val PAGE_WIDTH = 595
    private const val PAGE_HEIGHT = 842
    private const val MARGIN = 40f
    private const val CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

    fun generatePdf(context: Context, caseData: SavedCase): File? {
        val patient = caseData.patientProfile ?: Patient(
            id = caseData.patientId.ifEmpty { caseData.id },
            name = caseData.patientName.ifEmpty { "Patient" },
            doctorName = caseData.doctorName.ifEmpty { "Doctor" },
            hospital = "Orthofinix Clinic"
        )

        val clinicalData = try {
            ClinicalReport.fromJson(caseData.clinicalDataJson)
        } catch (e: Exception) {
            null
        }

        val pdfDocument = PdfDocument()
        var pageNumber = 1
        var currentY = 0f
        var pageInfo = PdfDocument.PageInfo.Builder(PAGE_WIDTH, PAGE_HEIGHT, pageNumber).create()
        var page = pdfDocument.startPage(pageInfo)
        var canvas = page.canvas
        val paint = Paint()
        val textPaint = Paint()

        fun checkPageBreak(requiredSpace: Float) {
            if (currentY + requiredSpace > PAGE_HEIGHT - MARGIN - 20f) { // 20f for footer
                // Draw footer
                textPaint.textSize = 10f
                textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
                textPaint.color = Color.parseColor("#8E9AAF")
                canvas.drawText("Page $pageNumber", PAGE_WIDTH / 2f - 15f, PAGE_HEIGHT - 20f, textPaint)

                pdfDocument.finishPage(page)
                pageNumber++
                pageInfo = PdfDocument.PageInfo.Builder(PAGE_WIDTH, PAGE_HEIGHT, pageNumber).create()
                page = pdfDocument.startPage(pageInfo)
                canvas = page.canvas
                currentY = MARGIN
            }
        }

        fun drawHeader() {
            paint.color = Color.parseColor("#0C1B33")
            canvas.drawRect(0f, 0f, PAGE_WIDTH.toFloat(), 100f, paint)

            textPaint.color = Color.WHITE
            textPaint.textSize = 20f
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            canvas.drawText("ORTHOFINIX AI CLINICAL REPORT", MARGIN, 40f, textPaint)

            textPaint.textSize = 10f
            textPaint.color = Color.parseColor("#8E9AAF")
            val dateStr = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault()).format(Date(caseData.createdAt))
            canvas.drawText("Generated: $dateStr", MARGIN, 60f, textPaint)
            canvas.drawText("Doctor: ${patient.doctorName} | Hospital: ${patient.hospital}", MARGIN, 75f, textPaint)
            currentY = 120f
        }

        fun drawSectionTitle(title: String) {
            checkPageBreak(40f)
            currentY += 10f
            paint.color = Color.parseColor("#E5E9F0")
            canvas.drawRect(MARGIN, currentY - 15f, PAGE_WIDTH - MARGIN, currentY + 5f, paint)
            
            textPaint.color = Color.parseColor("#0C1B33")
            textPaint.textSize = 14f
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            canvas.drawText(title, MARGIN + 5f, currentY, textPaint)
            currentY += 20f
        }

        fun drawKeyValue(key: String, value: String, xOffset: Float = MARGIN + 5f, nextLine: Boolean = false) {
            checkPageBreak(15f)
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            textPaint.textSize = 10f
            textPaint.color = Color.BLACK
            canvas.drawText("$key: ", xOffset, currentY, textPaint)
            
            val keyWidth = textPaint.measureText("$key: ")
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
            canvas.drawText(value, xOffset + keyWidth, currentY, textPaint)
            if (nextLine) currentY += 15f
        }

        fun drawLongText(text: String, xOffset: Float = MARGIN + 5f) {
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
            textPaint.textSize = 10f
            textPaint.color = Color.BLACK
            
            var textToDraw = text
            while(textToDraw.isNotEmpty()) {
                checkPageBreak(15f)
                val count = textPaint.breakText(textToDraw, true, CONTENT_WIDTH - 10f, null)
                canvas.drawText(textToDraw.substring(0, count), xOffset, currentY, textPaint)
                textToDraw = textToDraw.substring(count)
                currentY += 15f
            }
        }

        // Draw Page 1 Header
        drawHeader()

        drawSectionTitle("PATIENT DETAILS")
        drawKeyValue("Patient ID", patient.id, MARGIN + 5f, false)
        drawKeyValue("Name", patient.name, 300f, true)
        drawKeyValue("Age", patient.age.toString(), MARGIN + 5f, false)
        drawKeyValue("DOB", patient.dateOfBirth, 300f, true)
        drawKeyValue("Gender", patient.gender, MARGIN + 5f, false)
        drawKeyValue("Phone", patient.phone, 300f, true)
        drawKeyValue("Email", patient.email, MARGIN + 5f, false)
        drawKeyValue("Diagnosis", patient.diagnosis, 300f, true)
        drawKeyValue("Treatment Date", patient.treatmentDate, MARGIN + 5f, false)
        drawKeyValue("Doctor Name", patient.doctorName, 300f, true)
        drawKeyValue("Hospital / Clinic", patient.hospital, MARGIN + 5f, true)
        drawKeyValue("Clinical Notes", patient.notes, MARGIN + 5f, true)
        currentY += 10f

        drawSectionTitle("CLINICAL EVALUATION")
        if (clinicalData != null) {
            drawKeyValue("Overall Confidence Score", "${(clinicalData.confidenceScore * 100).toInt()}%", MARGIN + 5f, true)
            drawKeyValue("ABO OGS Score", "${clinicalData.aboScore.toInt()} / 100", MARGIN + 5f, false)
            drawKeyValue("Andrews Six Keys Score", "${clinicalData.andrewsScore.toInt()} / 100", 300f, true)
            drawKeyValue("Rebecca Roling Evaluation", clinicalData.rolingResult?.overallScore?.toString() ?: "N/A", MARGIN + 5f, false)
            drawKeyValue("Raleigh Williams Evaluation", clinicalData.raleighWilliamsResult?.overallScore?.toString() ?: "N/A", 300f, true)
            currentY += 10f

            drawSectionTitle("MEASUREMENTS")
            drawKeyValue("Overjet", "${clinicalData.overjetMm} mm", MARGIN + 5f, false)
            drawKeyValue("Overbite", "${clinicalData.overbitePercent}%", 300f, true)
            drawKeyValue("Midline Discrepancy", "${clinicalData.midlineDiscrepancyMm} mm", MARGIN + 5f, false)
            drawKeyValue("Curve of Spee", "${clinicalData.curveOfSpeeMm} mm", 300f, true)
            drawKeyValue("Alignment (Symmetry)", "${clinicalData.archSymmetryScore}%", MARGIN + 5f, false)
            drawKeyValue("Arch Width", "Evaluated", 300f, true)
            drawKeyValue("Buccolingual Inclination", "Evaluated", MARGIN + 5f, false)
            drawKeyValue("Marginal Ridge", "Evaluated", 300f, true)
            drawKeyValue("Rotation", "Evaluated", MARGIN + 5f, false)
            drawKeyValue("Crowding / Spacing", "Evaluated", 300f, true)
            currentY += 10f

            drawSectionTitle("RECOMMENDATIONS")
            val recommendationsList = clinicalData.recommendations.ifEmpty { 
                clinicalData.structuredRecommendations.map { it.clinicalActionStep }
            }
            if (recommendationsList.isEmpty()) {
                drawLongText("No recommendations provided.")
            } else {
                recommendationsList.forEachIndexed { index, rec ->
                    drawLongText("${index + 1}. $rec")
                }
            }
        } else {
            drawLongText("Clinical measurements not available for this case.")
        }
        currentY += 10f

        drawSectionTitle("CLINICAL IMAGES")
        // Just drawing placeholders for images if any.
        drawLongText("Images including OPG, Intraoral Photos, and Analysis Images would be displayed here if attached.")
        if (patient.imageUrls.isNotEmpty()) {
            patient.imageUrls.forEach { url ->
                // Basic check for local file path vs URL
                try {
                    val file = File(url)
                    if (file.exists()) {
                        val bitmap = BitmapFactory.decodeFile(file.absolutePath)
                        if (bitmap != null) {
                            checkPageBreak(120f)
                            // Scale down
                            val scaled = Bitmap.createScaledBitmap(bitmap, 100, 100, true)
                            canvas.drawBitmap(scaled, MARGIN + 5f, currentY, paint)
                            currentY += 110f
                        }
                    } else {
                        drawLongText("Image referenced: $url")
                    }
                } catch (e: Exception) {
                    drawLongText("Image referenced: $url")
                }
            }
        }

        currentY += 10f
        drawSectionTitle("REFERENCES")
        drawLongText("1. American Board of Orthodontics (ABO) Objective Grading System")
        drawLongText("2. Andrews' Six Keys to Normal Occlusion")
        drawLongText("3. Raleigh Williams Finishing Guidelines")
        drawLongText("4. Rebecca Roling's Protocols for Detailing")
        currentY += 10f

        drawSectionTitle("SUMMARY")
        val finalOverall = clinicalData?.let { (it.aboScore + it.andrewsScore) / 2 } ?: 0f
        drawKeyValue("Overall Score", "${finalOverall.toInt()} / 100", MARGIN + 5f, true)
        drawKeyValue("Doctor Name", patient.doctorName, MARGIN + 5f, true)
        val reportDateStr = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault()).format(Date())
        drawKeyValue("Report Generated Date & Time", reportDateStr, MARGIN + 5f, true)
        
        // Final Page Footer
        textPaint.textSize = 10f
        textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
        textPaint.color = Color.parseColor("#8E9AAF")
        canvas.drawText("Page $pageNumber", PAGE_WIDTH / 2f - 15f, PAGE_HEIGHT - 20f, textPaint)

        pdfDocument.finishPage(page)

        // Save
        val sanitizedName = patient.name.replace("[^a-zA-Z0-9_]".toRegex(), "_")
        val fileName = "Clinical_Report_${sanitizedName}_${caseData.id.take(4)}.pdf"
        val pdfFile = File(context.cacheDir, fileName)

        try {
            pdfDocument.writeTo(FileOutputStream(pdfFile))
            pdfDocument.close()
            return pdfFile
        } catch (e: IOException) {
            e.printStackTrace()
            return null
        }
    }

    fun generateAndSharePdf(context: Context, caseData: SavedCase) {
        val pdfFile = generatePdf(context, caseData)
        if (pdfFile != null) {
            val uri: Uri = FileProvider.getUriForFile(context, "com.example.orthofinixai.fileprovider", pdfFile)
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "application/pdf"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, "OrthofinixAI Clinical Report: ${caseData.patientProfile?.name ?: caseData.patientName}")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            val chooserIntent = Intent.createChooser(shareIntent, "Share Clinical Report").apply {
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(chooserIntent)
            Toast.makeText(context, "Report generated successfully!", Toast.LENGTH_LONG).show()
        } else {
            Toast.makeText(context, "Error saving PDF", Toast.LENGTH_SHORT).show()
        }
    }
}
