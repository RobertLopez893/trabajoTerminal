package com.example.animoon.ui.world

enum class WorldZone(
    val id: String,
    val title: String
) {
    BASE(
        id = "base_principal",
        title = "Base Principal"
    ),
    CRATERS(
        id = "crateres_gigantes",
        title = "Cráteres gigantes"
    ),
    VILLAGE(
        id = "aldea_lunatica",
        title = "Aldea lunática"
    ),
    DARK_SIDE(
        id = "lado_oscuro_de_la_luna",
        title = "El lado oscuro de la luna"
    );

    companion object {
        fun fromId(id: String?): WorldZone {
            return values().firstOrNull { it.id == id } ?: BASE
        }
    }
}