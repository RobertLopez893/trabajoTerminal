package com.example.animoon.data.network

import com.example.animoon.data.model.MinijuegoScoreRequest
import com.example.animoon.data.model.DefaultResponse
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface MinigameApiService {
    @POST("/api/minijuegos/guardar-puntaje")
    suspend fun guardarPuntaje(@Body request: MinijuegoScoreRequest): Response<DefaultResponse>

    @GET("/api/minijuegos/minijuego-3/conversaciones")
    suspend fun obtenerConversacionesGame3(@Query("cantidad") cantidad: Int): Response<ResponseBody>
}
