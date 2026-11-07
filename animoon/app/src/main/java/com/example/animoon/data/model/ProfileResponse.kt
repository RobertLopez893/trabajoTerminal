package com.example.animoon.data.model

import com.google.gson.annotations.SerializedName

data class MinijuegoStat(
    @SerializedName("minijuego_id") val minijuegoId: String,
    val nombre: String,
    @SerializedName("record_puntaje") val recordPuntaje: Int,
    @SerializedName("nivel_max_alcanzado") val nivelMaxAlcanzado: Int
)

data class ProfileResponse(
    val id: String,
    val nickname: String,
    val species: String,
    val color: String,
    @SerializedName("games_played") val gamesPlayed: Int,
    @SerializedName("highest_score") val highestScore: Int,
    val minigames: List<MinijuegoStat>? = null
)
