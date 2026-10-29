package com.example.animoon.data.network

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Path

data class ParentRequestCodeResponse(
    @SerializedName("message") val message: String,
    @SerializedName("masked_phone") val maskedPhone: String,
    @SerializedName("expires_in_seconds") val expiresInSeconds: Int,
    @SerializedName("status") val status: String
)

data class ParentVerifyCodeRequest(
    @SerializedName("codigo") val codigo: String
)

data class ParentVerifyCodeResponse(
    @SerializedName("message") val message: String,
    @SerializedName("parent_token") val parentToken: String,
    @SerializedName("expires_in_seconds") val expiresInSeconds: Int,
    @SerializedName("status") val status: String
)

data class ParentAlertDto(
    @SerializedName("id") val id: String,
    @SerializedName("dateLabel") val dateLabel: String,
    @SerializedName("title") val title: String,
    @SerializedName("summary") val summary: String,
    @SerializedName("is_read") val isRead: Boolean
)

data class ParentDashboardResponse(
    @SerializedName("child_nickname") val childNickname: String,
    @SerializedName("child_description") val childDescription: String,
    @SerializedName("alerts") val alerts: List<ParentAlertDto>
)

data class ParentIncidentMessageDto(
    @SerializedName("author") val author: String,
    @SerializedName("time") val time: String,
    @SerializedName("text") val text: String,
    @SerializedName("fromChild") val fromChild: Boolean
)

data class ParentIncidentDetailResponse(
    @SerializedName("id") val id: String,
    @SerializedName("dateLabel") val dateLabel: String,
    @SerializedName("title") val title: String,
    @SerializedName("summary") val summary: String,
    @SerializedName("confidence_score") val confidenceScore: Double,
    @SerializedName("fase_detectada") val faseDetectada: String,
    @SerializedName("messages") val messages: List<ParentIncidentMessageDto>,
    @SerializedName("guidance") val guidance: String
)

interface ParentApiService {

    @POST("/api/parents/request-code")
    suspend fun requestCode(): Response<ParentRequestCodeResponse>

    @POST("/api/parents/verify-code")
    suspend fun verifyCode(
        @Body req: ParentVerifyCodeRequest
    ): Response<ParentVerifyCodeResponse>

    @GET("/api/parents/dashboard")
    suspend fun getDashboard(
        @Header("X-Parent-Token") parentToken: String
    ): Response<ParentDashboardResponse>

    @GET("/api/parents/incident/{alert_id}")
    suspend fun getIncidentDetail(
        @Header("X-Parent-Token") parentToken: String,
        @Path("alert_id") alertId: String
    ): Response<ParentIncidentDetailResponse>
}
