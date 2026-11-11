package com.example.animoon.data.network

import com.example.animoon.data.model.ActiveUsersResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body

data class ChatInviteRequest(
    val target_user_id: String
)

data class ChatInviteResponse(
    val status: String,
    val notified: Boolean
)

interface EnvApiService {
    @GET("/api/env/active-users")
    suspend fun getActiveUsers(): Response<ActiveUsersResponse>

    @POST("/api/env/invite-chat")
    suspend fun inviteToChat(
        @Body req: ChatInviteRequest
    ): Response<ChatInviteResponse>
}

