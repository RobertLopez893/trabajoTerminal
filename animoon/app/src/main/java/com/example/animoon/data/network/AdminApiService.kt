package com.example.animoon.data.network

import com.example.animoon.data.model.DefaultResponse
import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Path

data class AdminLoginRequest(
    @SerializedName("username") val username: String,
    @SerializedName("password") val password: String
)

data class AdminLoginResponse(
    @SerializedName("message") val message: String,
    @SerializedName("admin_token") val adminToken: String,
    @SerializedName("expires_in_seconds") val expiresInSeconds: Int,
    @SerializedName("status") val status: String
)

data class AdminAppealDto(
    @SerializedName("id") val id: String,
    @SerializedName("nickname") val nickname: String,
    @SerializedName("date") val date: String,
    @SerializedName("incident") val incident: String,
    @SerializedName("explanation") val explanation: String,
    @SerializedName("evidence") val evidence: String,
    @SerializedName("status") val status: String,
    @SerializedName("resolution") val resolution: String,
    @SerializedName("resolvedAt") val resolvedAt: Long,
    @SerializedName("resolvedBy") val resolvedBy: String
)

data class AdminAppealResolveRequest(
    @SerializedName("approved") val approved: Boolean,
    @SerializedName("reason") val reason: String
)

data class UserAppealSubmitRequest(
    @SerializedName("nickname") val nickname: String,
    @SerializedName("justificacion") val justificacion: String
)

interface AdminApiService {

    @POST("/api/admin/login")
    suspend fun login(
        @Body req: AdminLoginRequest
    ): Response<AdminLoginResponse>

    @GET("/api/admin/appeals")
    suspend fun getAppeals(
        @Header("X-Admin-Token") token: String
    ): Response<List<AdminAppealDto>>

    @POST("/api/admin/appeals/{id}/review")
    suspend fun markInReview(
        @Header("X-Admin-Token") token: String,
        @Path("id") id: String
    ): Response<DefaultResponse>

    @POST("/api/admin/appeals/{id}/resolve")
    suspend fun resolve(
        @Header("X-Admin-Token") token: String,
        @Path("id") id: String,
        @Body req: AdminAppealResolveRequest
    ): Response<AdminAppealDto>

    @POST("/api/admin/submit-appeal")
    suspend fun submitAppeal(
        @Body req: UserAppealSubmitRequest
    ): Response<DefaultResponse>
}
