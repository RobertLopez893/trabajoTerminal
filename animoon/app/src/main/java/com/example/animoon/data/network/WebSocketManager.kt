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

    var isConnected: Boolean = false
        private set

    var currentZone: String = "base_principal"
        private set

    // Estado observable de los jugadores en la zona actual
    private val _playersInZone = MutableStateFlow<List<PlayerState>>(emptyList())
    val playersInZone: StateFlow<List<PlayerState>> = _playersInZone.asStateFlow()

    fun connect(zonaInicial: String = "base_principal", initialX: Float = 0f, initialY: Float = 0f) {
        val token = TokenManager.getToken()
        if (token.isNullOrEmpty()) {
            Log.e(TAG, "No se puede conectar al WebSocket: Token no encontrado")
            return
        }

        // Si ya hay una conexión activa y saludable
        if (webSocket != null && isConnected) {
            if (currentZone != zonaInicial) {
                Log.d(TAG, "Reutilizando conexión WS: cambiando de $currentZone a $zonaInicial")
                switchZone(zonaInicial, initialX, initialY)
            } else {
                Log.d(TAG, "Conexión WS ya activa en la zona $zonaInicial")
                if (initialX > 0f && initialY > 0f) {
                    sendMessage(MoveMessage(initialX, initialY))
                }
            }
            return
        }

        // Si había una conexión previa no conectada, limpiarla
        if (webSocket != null && !isConnected) {
            try {
                webSocket?.cancel()
            } catch (ignored: Exception) {}
            webSocket = null
        }

        currentZone = zonaInicial
        _playersInZone.value = emptyList()

        // Convertir http:// a ws:// y https:// a wss://
        val httpUrl = BuildConfig.API_BASE_URL
        val wsBaseUrl = httpUrl.replaceFirst("http://", "ws://").replaceFirst("https://", "wss://")
        
        // Incluir token, zona inicial y coordenadas de spawn en los query parameters
        val url = "${wsBaseUrl}api/env/ws?token=$token&zona=$zonaInicial&x=$initialX&y=$initialY"

        val request = Request.Builder()
            .url(url)
            .build()

        webSocket = ApiClient.okHttpClient.newWebSocket(request, this)
        Log.d(TAG, "Intentando conectar a WS: $url")
    }

    fun switchZone(newZone: String, x: Float = 0f, y: Float = 0f) {
        currentZone = newZone
        _playersInZone.value = emptyList()

        if (webSocket != null && isConnected) {
            Log.d(TAG, "Enviando ChangeZoneMessage a $newZone ($x, $y)")
            sendMessage(ChangeZoneMessage(newZone, x, y))
        } else {
            Log.d(TAG, "No hay conexión abierta para cambiar de zona; iniciando connect($newZone)")
            connect(newZone, x, y)
        }
    }

    fun disconnect() {
        isConnected = false
        try {
            webSocket?.close(1000, "User disconnected")
        } catch (ignored: Exception) {}
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
        isConnected = true
        Log.d(TAG, "Conexión WebSocket abierta exitosamente en zona $currentZone")
    }

    override fun onMessage(webSocket: WebSocket, text: String) {
        super.onMessage(webSocket, text)
        Log.d(TAG, "Mensaje recibido: $text")

        try {
            val jsonObject = gson.fromJson(text, JsonObject::class.java)
            val type = jsonObject.get("type")?.asString

            when (type) {
                "zone_state", "tick" -> {
                    val msg = gson.fromJson(text, ZoneStateMessage::class.java)
                    // Filtrar estrictamente: solo aceptar ticks correspondientes a la zona actual
                    if (msg.zona.isNullOrEmpty() || msg.zona == currentZone) {
                        _playersInZone.value = msg.players
                    } else {
                        Log.d(TAG, "Ignorando tick de zona ${msg.zona} porque la zona actual es $currentZone")
                    }
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
        isConnected = false
        this.webSocket = null
        _playersInZone.value = emptyList()
    }

    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        super.onFailure(webSocket, t, response)
        Log.e(TAG, "Error en WebSocket: ${t.message}")
        isConnected = false
        this.webSocket = null
        _playersInZone.value = emptyList()

        if (response?.code == 401) {
            TokenManager.sessionExpiredFlow.tryEmit(Unit)
        }
    }
}
