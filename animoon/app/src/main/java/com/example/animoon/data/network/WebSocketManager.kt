package com.example.animoon.data.network

import android.util.Log
import com.example.animoon.BuildConfig
import com.example.animoon.data.model.*
import com.google.gson.Gson
import com.google.gson.JsonObject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import okhttp3.*
import okio.ByteString

object WebSocketManager : WebSocketListener() {
    private const val TAG = "WebSocketManager"
    private var webSocket: WebSocket? = null
    private val gson = Gson()

    // Estado observable de los jugadores en la zona actual
    private val _playersInZone = MutableStateFlow<List<PlayerState>>(emptyList())
    val playersInZone: StateFlow<List<PlayerState>> = _playersInZone.asStateFlow()

    fun connect(zonaInicial: String = "base_principal") {
        val token = TokenManager.getToken()
        if (token.isNullOrEmpty()) {
            Log.e(TAG, "No se puede conectar al WebSocket: Token no encontrado")
            return
        }

        // Convertir http:// a ws:// y https:// a wss://
        val httpUrl = BuildConfig.API_BASE_URL
        val wsBaseUrl = httpUrl.replaceFirst("http://", "ws://").replaceFirst("https://", "wss://")
        
        // El endpoint requiere el token en el query parameter
        val url = "${wsBaseUrl}api/env/ws?token=$token"

        val request = Request.Builder()
            .url(url)
            .build()

        // Usamos el cliente ya configurado de ApiClient
        webSocket = ApiClient.okHttpClient.newWebSocket(request, this)
        Log.d(TAG, "Intentando conectar a: $url")
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
        _playersInZone.value = emptyList()
        Log.d(TAG, "Desconectado intencionalmente")
    }

    fun sendMessage(message: WsOutgoingMessage) {
        val json = gson.toJson(message)
        webSocket?.send(json)
        Log.d(TAG, "Enviando: $json")
    }

    // ==========================================
    // Callbacks del WebSocketListener
    // ==========================================

    override fun onOpen(webSocket: WebSocket, response: Response) {
        super.onOpen(webSocket, response)
        Log.d(TAG, "Conexión WebSocket abierta")
    }

    override fun onMessage(webSocket: WebSocket, text: String) {
        super.onMessage(webSocket, text)
        Log.d(TAG, "Mensaje recibido: $text")

        try {
            val jsonObject = gson.fromJson(text, JsonObject::class.java)
            val type = jsonObject.get("type")?.asString

            when (type) {
                "zone_state", "tick" -> {
                    // Ambos mensajes traen el array de players completo visible para el usuario
                    val msg = gson.fromJson(text, ZoneStateMessage::class.java) // Funciona para ambos porque la firma JSON es idéntica
                    _playersInZone.value = msg.players
                }
                "player_joined" -> {
                    val msg = gson.fromJson(text, PlayerJoinedMessage::class.java)
                    val newPlayer = PlayerState(
                        usuarioId = msg.usuarioId,
                        nickname = msg.nickname,
                        avatar = msg.avatar,
                        x = msg.x,
                        y = msg.y
                    )
                    _playersInZone.update { current -> current + newPlayer }
                }
                "player_moved" -> {
                    // Con el tick batching esto ya no se usa mucho, pero lo dejamos por compatibilidad
                    val msg = gson.fromJson(text, PlayerMovedMessage::class.java)
                    _playersInZone.update { current ->
                        current.map { player ->
                            if (player.usuarioId == msg.usuarioId) {
                                player.copy(x = msg.x, y = msg.y)
                            } else {
                                player
                            }
                        }
                    }
                }
                "player_left" -> {
                    val msg = gson.fromJson(text, PlayerLeftMessage::class.java)
                    _playersInZone.update { current ->
                        current.filter { it.usuarioId != msg.usuarioId }
                    }
                }
                else -> {
                    Log.w(TAG, "Tipo de mensaje desconocido: $type")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error parseando mensaje WebSocket: ${e.message}")
        }
    }

    override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
        super.onClosed(webSocket, code, reason)
        Log.d(TAG, "Conexión WebSocket cerrada: $code / $reason")
        _playersInZone.value = emptyList()
    }

    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        super.onFailure(webSocket, t, response)
        Log.e(TAG, "Error en WebSocket: ${t.message}")
        _playersInZone.value = emptyList()

        // Si el código de error es 401/403 o el websocket falla por violación de política (código 1008)
        // Podríamos intentar reconectar o lanzar SESSION_EXPIRED si es problema de auth.
        // Por ahora, solo emitiremos sesión expirada si la respuesta HTTP original fue 401.
        if (response?.code == 401) {
            TokenManager.sessionExpiredFlow.tryEmit(Unit)
        }
    }
}
