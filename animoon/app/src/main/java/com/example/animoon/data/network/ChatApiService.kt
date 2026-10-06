package com.example.animoon.data.network

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import com.example.animoon.network.EncryptedMessagePayload

data class MensajeResponse(
    val id: String,
    val chat_id: String,
    val emisor_usuario_id: String,
    val contenido_cifrado_aes_gcm: String,
    val iv_nonce: String,
    val aes_gcm_tag: String,
    val orden_global: Int
)

interface ChatApiService {
    @GET("/ws/chat/history/{chat_id}")
    suspend fun getChatHistory(
        @Path("chat_id") chatId: String
    ): Response<List<MensajeResponse>>
}
