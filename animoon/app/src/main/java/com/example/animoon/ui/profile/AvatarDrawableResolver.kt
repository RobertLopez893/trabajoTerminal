package com.example.animoon.ui.profile

import com.example.animoon.R
import java.util.Locale

object AvatarDrawableResolver {

    private val avatars = mapOf(
        "conejo" to mapOf(
            "blanco" to R.drawable.avatar_rabbit_white,
            "azul" to R.drawable.avatar_rabbit_blue,
            "naranja" to R.drawable.avatar_rabbit_orange,
            "verde" to R.drawable.avatar_rabbit_green
        ),
        "gato" to mapOf(
            "blanco" to R.drawable.avatar_cat_white,
            "azul" to R.drawable.avatar_cat_blue,
            "naranja" to R.drawable.avatar_cat_orange,
            "verde" to R.drawable.avatar_cat_green
        ),
        "perro" to mapOf(
            "blanco" to R.drawable.avatar_dog_white,
            "azul" to R.drawable.avatar_dog_blue,
            "naranja" to R.drawable.avatar_dog_orange,
            "verde" to R.drawable.avatar_dog_green
        ),
        "zorro" to mapOf(
            "blanco" to R.drawable.avatar_fox_white,
            "azul" to R.drawable.avatar_fox_blue,
            "naranja" to R.drawable.avatar_fox_orange,
            "verde" to R.drawable.avatar_fox_green
        )
    )

    fun resolve(species: String, color: String): Int? {
        val normalizedSpecies =
            species.trim().lowercase(Locale.ROOT)

        val normalizedColor =
            color.trim().lowercase(Locale.ROOT)

        return avatars[normalizedSpecies]?.get(normalizedColor)
    }
}