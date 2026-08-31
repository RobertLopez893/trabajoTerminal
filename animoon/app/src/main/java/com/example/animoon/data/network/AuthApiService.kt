package com.example.animoon.data.network

import com.example.animoon.data.model.DefaultResponse
import com.example.animoon.data.model.FinalRegisterRequest
import com.example.animoon.data.model.NicknameCheckRequest
import com.example.animoon.data.model.SmsSendRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApiService {

    @POST("/api/auth/verificar-apelativo")
    suspend fun verifyNickname(
        @Body request: NicknameCheckRequest
    ): Response<DefaultResponse>

    @POST("/api/auth/enviar-codigo-sms")
    suspend fun sendSmsCode(
        @Body request: SmsSendRequest
    ): Response<DefaultResponse>

    @POST("/api/auth/registro-final")
    suspend fun finalRegister(
        @Body request: FinalRegisterRequest
    ): Response<DefaultResponse>
}
