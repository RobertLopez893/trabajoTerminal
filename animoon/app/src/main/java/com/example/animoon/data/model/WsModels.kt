package com.example.animoon.data.model

import com.google.gson.annotations.SerializedName

/**
 * Representa el estado de un jugador en la zona.
 */
data class PlayerState(
    @SerializedName("usuario_id") val usuarioId: String,
    val nickname: String,
    val avatar: Map<String, String>?,
    var x: Float,
    var y: Float
)

/**
 * Modelos para parsear los mensajes que llegan del servidor (INCOMING).
 */
open class WsIncomingMessage(
    val type: String
)

data class ZoneStateMessage(
    val zona: String,
    val players: List<PlayerState>
) : WsIncomingMessage("zone_state")

data class PlayerJoinedMessage(
    @SerializedName("usuario_id") val usuarioId: String,
    val nickname: String,
    val avatar: Map<String, String>?,
    val x: Float,
    val y: Float
) : WsIncomingMessage("player_joined")

data class PlayerMovedMessage(
    @SerializedName("usuario_id") val usuarioId: String,
    val x: Float,
    val y: Float
) : WsIncomingMessage("player_moved")

data class PlayerLeftMessage(
    @SerializedName("usuario_id") val usuarioId: String
) : WsIncomingMessage("player_left")

data class TickMessage(
    val zona: String,
    val players: List<PlayerState>
) : WsIncomingMessage("tick")


/**
 * Modelos para enviar al servidor (OUTGOING).
 */
open class WsOutgoingMessage(
    val type: String
)

data class MoveMessage(
    val x: Float,
    val y: Float
) : WsOutgoingMessage("move")

data class ChangeZoneMessage(
    val zona: String
) : WsOutgoingMessage("change_zone")
