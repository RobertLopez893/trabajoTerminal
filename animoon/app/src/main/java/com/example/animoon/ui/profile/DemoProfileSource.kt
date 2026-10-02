package com.example.animoon.ui.profile

/**
 * Datos temporales para desarrollar y probar la interfaz.
 * No corresponden a la sesión real.
 */
object DemoProfileSource {

    val myProfile = PlayerProfile(
        id = "demo_me",
        nickname = "ExploradorLunar",
        species = "conejo",
        color = "azul"
    )

    val otherPlayers = listOf(
        PlayerProfile(
            id = "demo_fox",
            nickname = "EstrellaNaranja",
            species = "zorro",
            color = "naranja"
        ),
        PlayerProfile(
            id = "demo_cat",
            nickname = "GatitoCosmico",
            species = "gato",
            color = "blanco"
        ),
        PlayerProfile(
            id = "demo_dog",
            nickname = "GuardianLunar",
            species = "perro",
            color = "verde"
        )
    )

    fun findProfile(userId: String): PlayerProfile? {
        return if (userId == myProfile.id) {
            myProfile
        } else {
            otherPlayers.firstOrNull { it.id == userId }
        }
    }

    fun isMyProfile(userId: String): Boolean {
        return userId == myProfile.id
    }
}