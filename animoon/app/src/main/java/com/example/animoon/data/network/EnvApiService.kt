package com.example.animoon.data.network

import com.example.animoon.data.model.ActiveUsersResponse
import retrofit2.Response
import retrofit2.http.GET

interface EnvApiService {
    @GET("/api/env/active-users")
    suspend fun getActiveUsers(): Response<ActiveUsersResponse>
}
