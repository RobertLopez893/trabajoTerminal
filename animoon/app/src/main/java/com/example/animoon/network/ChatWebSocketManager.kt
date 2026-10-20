package com.example.animoon.network

import android.util.Log
import com.example.animoon.BuildConfig
import com.example.animoon.data.network.ApiClient
import com.example.animoon.security.AESGCMCipher
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import okhttp3.*

data class EncryptedMessagePayload(
    @SerializedName("ciphertext_b64") val ciphertextB64: String,
    @SerializedName("nonce_b64") val nonceB64: String,
    @SerializedName("tag_b64") val tagB64: String
)

data class ChatMessagePayload(
    val chat_id: String? = null,
    val sender_id: String,
    val target_id: String? = null,
    val encrypted_message: EncryptedMessagePayload,
    val system: Boolean = false,
    val action: String? = null,
    val motivo: String? = null
)

data class DecryptedChatMessage(
    val senderId: String,
    val text: String,
    val isSystem: Boolean,
    val isMine: Boolean,
    val action: String? = null,
    val motivo: String? = null
)

sealed class ChatSecurityEvent {
    data class SafeExit(val message: String, val motivo: String?) : ChatSecurityEvent()
    data class ConnectionBanned(val code: Int, val reason: String) : ChatSecurityEvent()
}

object ChatWebSocketManager : WebSocketListener() {
    private const val TAG = "ChatWebSocketManager"
    private var webSocket: WebSocket? = null
    private val gson = Gson()
    
    private var currentChatId: String = ""
    private var myUserId: String = ""
    private var targetUserId: String = ""

    // Flow to emit received chat messages to UI
    private val _messages = MutableSharedFlow<DecryptedChatMessage>(extraBufferCapacity = 64)
    val messages: SharedFlow<DecryptedChatMessage> = _messages.asSharedFlow()

    // Flow to emit security events (Safe Exit, Ban, etc.)
    private val _securityEvents = MutableSharedFlow<ChatSecurityEvent>(extraBufferCapacity = 16)
    val securityEvents: SharedFlow<ChatSecurityEvent> = _securityEvents.asSharedFlow()

    fun connect(chatId: String, userId: String, targetId: String = "") {
        currentChatId = chatId
        myUserId = userId
        targetUserId = targetId

        val baseUrl = BuildConfig.API_BASE_URL.replaceFirst("http://", "ws://").replaceFirst("https://", "wss://")
        val host = if (baseUrl.contains("10.0.2.2")) "10.0.2.2" else baseUrl.split("://")[1].split(":")[0].split("/")[0]
        
        val scheme = "wss" // El servidor python siempre usa TLS 1.3 con certificados autofirmados
        val wsUrl = "$scheme://$host:8765"

        Log.d(TAG, "Conectando chat a: $wsUrl para chat_id: $chatId")

        val request = Request.Builder().url(wsUrl).build()

        // Usar cliente inseguro por el certificado autofirmado del chat
        val client = UnsafeOkHttpClient.getUnsafeOkHttpClient() 
        webSocket = client.newWebSocket(request, this)
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected from chat")
        webSocket = null
        currentChatId = ""
        Log.d(TAG, "Chat desconectado")
    }

    fun sendMessage(plaintext: String) {
        if (webSocket == null || currentChatId.isEmpty()) {
            Log.e(TAG, "No se puede enviar, no hay conexión o chat_id no está definido.")
            return
        }

        try {
            val encData = AESGCMCipher.encrypt(plaintext)
            val payload = ChatMessagePayload(
                chat_id = currentChatId,
                sender_id = myUserId,
                target_id = targetUserId,
                encrypted_message = EncryptedMessagePayload(
                    encData.ciphertextB64,
                    encData.nonceB64,
                    encData.tagB64
                )
            )

            val json = gson.toJson(payload)
            webSocket?.send(json)
            Log.d(TAG, "Mensaje enviado (cifrado): $json")
        } catch (e: Exception) {
            Log.e(TAG, "Error cifrando mensaje: ${e.message}")
        }
    }

    override fun onMessage(webSocket: WebSocket, text: String) {
        super.onMessage(webSocket, text)
        Log.d(TAG, "Chat WS Recibido: $text")

        try {
            val payload = gson.fromJson(text, ChatMessagePayload::class.java)
            
            // Descifrar mensaje
            val decryptedText = AESGCMCipher.decrypt(
                payload.encrypted_message.ciphertextB64,
                payload.encrypted_message.nonceB64,
                payload.encrypted_message.tagB64
            )

            val msg = DecryptedChatMessage(
                senderId = payload.sender_id,
                text = decryptedText,
                isSystem = payload.system,
                isMine = (payload.sender_id == myUserId),
                action = payload.action,
                motivo = payload.motivo
            )

            _messages.tryEmit(msg)
            Log.d(TAG, "Mensaje descifrado: $decryptedText")

            // Si es un evento de salida segura, emitir al flow de seguridad
            if (payload.action == "SAFE_EXIT") {
                _securityEvents.tryEmit(
                    ChatSecurityEvent.SafeExit(
                        message = decryptedText,
                        motivo = payload.motivo
                    )
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error parseando o descifrando mensaje de chat: ${e.message}")
        }
    }

    override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
        super.onClosing(webSocket, code, reason)
        Log.d(TAG, "Chat WS Closing: code=$code, reason=$reason")
        if (code == 4003) {
            _securityEvents.tryEmit(ChatSecurityEvent.ConnectionBanned(code, reason))
        }
        webSocket.close(1000, null)
    }

    override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
        super.onClosed(webSocket, code, reason)
        Log.d(TAG, "Chat WS Closed: code=$code, reason=$reason")
        if (code == 4003) {
            _securityEvents.tryEmit(ChatSecurityEvent.ConnectionBanned(code, reason))
        }
    }

    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        super.onFailure(webSocket, t, response)
        Log.e(TAG, "Chat WS Error: ${t.message}")
    }
}
