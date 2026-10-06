package com.example.animoon.data.model

import com.google.gson.annotations.SerializedName

data class ProfileResponse(
    val id: String,
    val nickname: String,
    val species: String,
    val color: String,
    @SerializedName("games_played") val gamesPlayed: Int,
    @SerializedName("highest_score") val highestScore: Int
)
