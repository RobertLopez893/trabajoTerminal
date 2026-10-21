package com.example.animoon.ui.minigame.game3.model

data class Game3Mensaje(
    val delJugador: Boolean,
    val texto: String
)

data class Game3Conversacion(
    val id: String,
    val contacto: String,
    val hayRiesgo: Boolean,
    val mensajes: List<Game3Mensaje>,
    val retroalimentacion: String
)
