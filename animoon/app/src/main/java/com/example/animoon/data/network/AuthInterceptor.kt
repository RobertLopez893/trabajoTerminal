package com.example.animoon.data.network

import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val requestBuilder = chain.request().newBuilder()
        
        // Recuperamos el token de las SharedPreferences
        val token = TokenManager.getToken()
        
        // Si hay un token guardado, lo inyectamos en la cabecera Authorization
        if (!token.isNullOrEmpty()) {
            requestBuilder.addHeader("Authorization", "Bearer $token")
        }
        
        val response = chain.proceed(requestBuilder.build())
        
        // Si el servidor responde 401 (Sesión expirada o revocada)
        if (response.code == 401) {
            TokenManager.sessionExpiredFlow.tryEmit(Unit)
        }
        
        return response
    }
}
