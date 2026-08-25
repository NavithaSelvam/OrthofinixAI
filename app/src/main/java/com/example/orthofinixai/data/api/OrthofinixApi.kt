package com.example.orthofinixai.data.api

import com.google.gson.annotations.SerializedName
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.tasks.await

data class UploadResponse(
    val upload_id: String,
    val image_url: String
)

data class BackendHistoryItem(
    val id: String,
    @SerializedName("patient_name") val patientName: String?,
    @SerializedName("patientName") val patientNameAlt: String? = null,
    @SerializedName("finishing_score") val finishingScore: Float?,
    @SerializedName("overallScore") val overallScore: Float? = null,
    @SerializedName("overall_finishing_score") val overallFinishingScore: Float? = null,
    @SerializedName("confidence_score") val confidenceScore: Float?,
    @SerializedName("confidence") val confidence: Float? = null,
    @SerializedName("alignment_score") val alignmentScore: Float? = null,
    @SerializedName("alignmentScore") val alignmentScoreAlt: Float? = null,
    @SerializedName("created_at") val createdAt: String?,
    @SerializedName("image_url") val imageUrl: String?,
    @SerializedName("imagePath") val imagePath: String? = null,
    @SerializedName("user_id") val userId: String?,
    @SerializedName("doctorId") val doctorId: String? = null
)

data class BackendPatientResponse(
    val id: String,
    @SerializedName("doctor_id") val doctorId: String?,
    val name: String,
    @SerializedName("date_of_birth") val dateOfBirth: String?,
    val gender: String?,
    @SerializedName("contact_info") val contactInfo: String?,
    @SerializedName("created_at") val createdAt: String?
)

data class PatientCreateRequest(
    val name: String,
    @SerializedName("date_of_birth") val dateOfBirth: String? = null,
    val gender: String? = null,
    @SerializedName("contact_info") val contactInfo: String? = null
)

data class BackendAnalysisResponse(
    val id: String,
    val user_id: String = "",
    val patient_name: String = "",
    val image_url: String = "",
    val view_type: String = "opg",
    val status: String = "completed",
    val finishing_score: Float = 0f,
    val overallScore: Float = 0f,
    val overall_finishing_score: Float = 0f,
    val alignment_score: Float = 0f,
    val alignmentScore: Float = 0f,
    val confidence_score: Float = 0.94f,
    val confidence: Float = 0.94f,
    val midline_deviation_mm: Float = 0f,
    val overjet_mm: Float = 0f,
    val overbite_percent: Float = 0f,
    val abo_score: Float = 0f,
    val andrews_score: Float = 0f,
    val prediction: String = "",
    val recommendations: List<String> = emptyList(),
    val metrics: Map<String, Any>? = null,
    val created_at: String? = null,
    val root_angulation_score: Float = 0f,
    val teeth: List<Map<String, Any>> = emptyList(),
    val teeth_data: List<Map<String, Any>> = emptyList()
)

interface OrthofinixApi {

    @Multipart
    @POST("analysis/upload")
    suspend fun uploadImage(
        @Header("Authorization") token: String,
        @Part file: MultipartBody.Part
    ): UploadResponse

    @Multipart
    @POST("analysis/analyze")
    suspend fun analyzeImage(
        @Header("Authorization") token: String,
        @Part("upload_id") uploadId: okhttp3.RequestBody,
        @Part("patient_name") patientName: okhttp3.RequestBody,
        @Part("view_type") viewType: okhttp3.RequestBody,
        @Part("case_id") caseId: okhttp3.RequestBody,
        @Part("dob") dob: okhttp3.RequestBody? = null,
        @Part("gender") gender: okhttp3.RequestBody? = null
    ): BackendAnalysisResponse

    @GET("analysis/history")
    suspend fun getHistory(
        @Header("Authorization") token: String
    ): List<BackendHistoryItem>

    @GET("analysis/report/{record_id}")
    suspend fun getReport(
        @Header("Authorization") token: String,
        @Path("record_id") recordId: String
    ): BackendAnalysisResponse

    @GET("analysis/demo")
    suspend fun getDemoAnalysis(
        @Header("Authorization") token: String
    ): BackendAnalysisResponse

    @DELETE("analysis/{record_id}")
    suspend fun deleteAnalysis(
        @Header("Authorization") token: String,
        @Path("record_id") recordId: String
    ): Map<String, Any>

    @POST("analysis/delete/{record_id}")
    suspend fun deleteAnalysisPost(
        @Header("Authorization") token: String,
        @Path("record_id") recordId: String
    ): Map<String, Any>

    @GET("patients/")
    suspend fun getPatients(
        @Header("Authorization") token: String
    ): List<BackendPatientResponse>

    @POST("patients/")
    suspend fun createPatient(
        @Header("Authorization") token: String,
        @Body patient: PatientCreateRequest
    ): BackendPatientResponse

    @DELETE("patients/{patient_id}")
    suspend fun deletePatient(
        @Header("Authorization") token: String,
        @Path("patient_id") patientId: String
    ): Map<String, Any>

    @DELETE("cases/{case_id}")
    suspend fun deleteCase(
        @Header("Authorization") token: String,
        @Path("case_id") caseId: String
    ): Map<String, Any>

    companion object {

        fun create(): OrthofinixApi {
            // Always read BASE_URL fresh — never cache the instance so URL is correct
            val currentBaseUrl = ApiConfig.BASE_URL

            val retrofit = Retrofit.Builder()
                .baseUrl(currentBaseUrl)
                .client(createOkHttpClient())
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            return retrofit.create(OrthofinixApi::class.java)
        }

        private fun createOkHttpClient(): OkHttpClient {

            val logger = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            val authInterceptor = okhttp3.Interceptor { chain ->
                val request = chain.request()
                val auth = com.google.firebase.auth.FirebaseAuth.getInstance()
                android.util.Log.d("AUTH_DEBUG", "Mobile UID: " + auth.currentUser?.uid)
                val builder = request.newBuilder()
                val existingAuth = request.header("Authorization")
                if (existingAuth.isNullOrEmpty()) {
                    try {
                        val token = kotlinx.coroutines.runBlocking {
                            auth.currentUser?.getIdToken(false)?.await()?.token
                        }
                        if (!token.isNullOrEmpty()) {
                            builder.header("Authorization", "Bearer $token")
                            android.util.Log.d("AUTH_DEBUG", "Attached Bearer token to request: ${request.url}")
                        }
                    } catch (e: Exception) {
                        android.util.Log.w("AUTH_DEBUG", "Notice getting token for request: ${e.message}")
                    }
                } else {
                    android.util.Log.d("AUTH_DEBUG", "Request already has Authorization header: ${request.url}")
                }
                chain.proceed(builder.build())
            }

            val responseInterceptor = okhttp3.Interceptor { chain ->
                val response = chain.proceed(chain.request())
                val responseBody = response.peekBody(Long.MAX_VALUE)
                val rawResponse = responseBody.string()
                android.util.Log.d("OkHttpRawResponse", "Raw response body: $rawResponse")
                android.util.Log.d("OkHttpRawResponse", "Response code: ${response.code}")
                response
            }

            return OkHttpClient.Builder()
                .addInterceptor(authInterceptor)
                .addInterceptor(logger)
                .addInterceptor(responseInterceptor)
                // Render free tier cold start + AI analysis can take 60-120s
                .connectTimeout(180, TimeUnit.SECONDS)
                .readTimeout(180, TimeUnit.SECONDS)
                .writeTimeout(180, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .build()
        }
    }
}