package com.example.animoon.data.network

import com.example.animoon.data.model.MinijuegoScoreRequest
import com.example.animoon.data.model.DefaultResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface MinigameApiService {
    @POST("/api/minijuegos/guardar-puntaje")
    suspend fun guardarPuntaje(@Body request: MinijuegoScoreRequest): Response<DefaultResponse>
}
