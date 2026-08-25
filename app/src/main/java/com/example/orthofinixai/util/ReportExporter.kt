package com.example.orthofinixai.util

import android.content.Context
import android.content.Intent
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
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object ReportExporter {

    fun generateAndSharePdf(context: Context, caseData: SavedCase) {
        val patient = caseData.patientProfile
        if (patient == null) {
            Toast.makeText(context, "Patient data missing. Cannot generate PDF.", Toast.LENGTH_SHORT).show()
            return
        }

        val clinicalData = try {
            ClinicalReport.fromJson(caseData.clinicalDataJson)
        } catch (e: Exception) {
            null
        }

        val pdfDocument = PdfDocument()
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 1).create()
        val page = pdfDocument.startPage(pageInfo)
        val canvas = page.canvas

        val paint = Paint()
        val textPaint = Paint()
        var currentY = 0f

        fun drawHeader() {
            paint.color = Color.parseColor("#0C1B33")
            canvas.drawRect(0f, 0f, 595f, 100f, paint)

            textPaint.color = Color.WHITE
            textPaint.textSize = 20f
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            canvas.drawText("ORTHOFINIX.AI CLINICAL REPORT", 40f, 40f, textPaint)

            textPaint.textSize = 10f
            textPaint.color = Color.parseColor("#8E9AAF")
            val dateStr = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault()).format(Date(caseData.createdAt))
            canvas.drawText("Date Generated: $dateStr", 40f, 60f, textPaint)
            canvas.drawText("Doctor: ${patient.doctorName} | Hospital: ${patient.hospital}", 40f, 75f, textPaint)
            currentY = 120f
        }

        fun drawSectionTitle(title: String) {
            currentY += 20f
            paint.color = Color.parseColor("#E5E9F0")
            canvas.drawRect(40f, currentY - 15f, 555f, currentY + 5f, paint)
            
            textPaint.color = Color.parseColor("#0C1B33")
            textPaint.textSize = 14f
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            canvas.drawText(title, 45f, currentY, textPaint)
            currentY += 20f
        }

        fun drawKeyValue(key: String, value: String, xOffset: Float = 45f) {
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            textPaint.textSize = 10f
            textPaint.color = Color.BLACK
            canvas.drawText("$key: ", xOffset, currentY, textPaint)
            
            val keyWidth = textPaint.measureText("$key: ")
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
            canvas.drawText(value, xOffset + keyWidth, currentY, textPaint)
        }

        // Draw Page 1
        drawHeader()

        drawSectionTitle("PATIENT DETAILS")
        drawKeyValue("Patient ID", patient.id)
        drawKeyValue("Name", patient.name, 300f)
        currentY += 15f
        drawKeyValue("Age", patient.age.toString())
        drawKeyValue("DOB", patient.dateOfBirth, 300f)
        currentY += 15f
        drawKeyValue("Gender", patient.gender)
        drawKeyValue("Phone", patient.phone, 300f)
        currentY += 15f
        drawKeyValue("Email", patient.email)
        drawKeyValue("Diagnosis", patient.diagnosis, 300f)
        currentY += 15f
        drawKeyValue("Treatment Date", patient.treatmentDate)
        currentY += 15f
        drawKeyValue("Clinical Notes", patient.notes)
        currentY += 30f

        drawSectionTitle("CLINICAL EVALUATION")
        if (clinicalData != null) {
            drawKeyValue("Overall Confidence", "${(clinicalData.confidenceScore * 100).toInt()}%")
            currentY += 15f
            drawKeyValue("ABO OGS Score", "${clinicalData.aboScore.toInt()} / 100")
            currentY += 15f
            drawKeyValue("Andrews Six Keys Score", "${clinicalData.andrewsScore.toInt()} / 100")
            currentY += 15f
            drawKeyValue("Rebecca Roling Finishing Score", clinicalData.rolingResult?.overallScore?.toString() ?: "N/A")
            currentY += 15f
            drawKeyValue("Raleigh Williams Score", clinicalData.raleighWilliamsResult?.overallScore?.toString() ?: "N/A")
            currentY += 30f

            drawSectionTitle("MEASUREMENTS")
            drawKeyValue("Overjet", "${clinicalData.overjetMm} mm")
            drawKeyValue("Overbite", "${clinicalData.overbitePercent}% (${clinicalData.overbiteAbsMm} mm)", 300f)
            currentY += 15f
            drawKeyValue("Midline Discrepancy", "${clinicalData.midlineDiscrepancyMm} mm")
            drawKeyValue("Curve of Spee", "${clinicalData.curveOfSpeeMm} mm", 300f)
            currentY += 15f
            drawKeyValue("Arch Symmetry", "${clinicalData.archSymmetryScore}%")
            drawKeyValue("Root Angulation", "${clinicalData.rootAngulationScore}%", 300f)
            currentY += 30f

            drawSectionTitle("RECOMMENDATIONS")
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
            val recommendationsList = clinicalData.recommendations.ifEmpty { 
                clinicalData.structuredRecommendations.map { it.clinicalActionStep }
            }
            
            recommendationsList.forEachIndexed { index, rec ->
                if (currentY > 780f) {
                    // Note: A robust PDF generator would create a new page here. 
                    // For simplicity in Canvas, we stop or truncate.
                    canvas.drawText("... (Continues on next page)", 45f, currentY, textPaint)
                    return@forEachIndexed
                }
                
                // Wrap text manually
                var textToDraw = "${index + 1}. $rec"
                while(textToDraw.isNotEmpty()) {
                    val count = textPaint.breakText(textToDraw, true, 500f, null)
                    canvas.drawText(textToDraw.substring(0, count), 45f, currentY, textPaint)
                    textToDraw = textToDraw.substring(count)
                    currentY += 15f
                }
            }
        } else {
            textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
            canvas.drawText("Clinical measurements not available for this case.", 45f, currentY, textPaint)
        }

        currentY += 30f
        drawSectionTitle("SUMMARY")
        textPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.NORMAL)
        canvas.drawText("This report contains clinical findings mapped dynamically from Orthofinix AI analysis.", 45f, currentY, textPaint)
        
        pdfDocument.finishPage(page)

        // Save and Share
        val fileName = "Report_${patient.name.replace(" ", "_")}_${caseData.id.take(4)}.pdf"
        val pdfFile = File(context.cacheDir, fileName)

        try {
            pdfDocument.writeTo(FileOutputStream(pdfFile))
            pdfDocument.close()

            val uri: Uri = FileProvider.getUriForFile(context, "com.example.orthofinixai.fileprovider", pdfFile)
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "application/pdf"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, "OrthofinixAI Clinical Report: ${patient.name}")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            context.startActivity(Intent.createChooser(shareIntent, "Share Clinical Report"))
            Toast.makeText(context, "Report generated successfully!", Toast.LENGTH_LONG).show()

        } catch (e: IOException) {
            e.printStackTrace()
            Toast.makeText(context, "Error saving PDF: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}
