package com.example.animoon.data.model

data class MinijuegoScoreRequest(
    val minijuego_id: String,
    val puntaje: Int,
    val nivel_max_alcanzado: Int = 1
)
