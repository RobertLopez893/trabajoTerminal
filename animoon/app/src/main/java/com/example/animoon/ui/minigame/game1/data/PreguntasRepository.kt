package com.example.animoon.ui.minigame.game1.data

import android.content.Context
import com.example.animoon.ui.minigame.game1.model.Opcion
import com.example.animoon.ui.minigame.game1.model.Pregunta
import org.json.JSONArray

class PreguntasRepository(
    private val context: Context
) {

    fun cargarPreguntas(): List<Pregunta> {

        val json = context.assets
            .open("preguntas_seguridad.json")
            .bufferedReader()
            .use { it.readText() }

        val jsonArray = JSONArray(json)

        val preguntas = mutableListOf<Pregunta>()

        for (i in 0 until jsonArray.length()) {

            val preguntaJson = jsonArray.getJSONObject(i)

            val id = preguntaJson.getInt("id")
            val texto = preguntaJson.getString("texto")

            val opcionesJson = preguntaJson.getJSONArray("opciones")

            val opciones = mutableListOf<Opcion>()

            for (j in 0 until opcionesJson.length()) {

                val opcionJson = opcionesJson.getJSONObject(j)

                val opcion = Opcion(
                    texto = opcionJson.getString("texto"),
                    retroalimentacion = opcionJson.getString("retroalimentacion"),
                    correcta = opcionJson.getBoolean("correcta")
                )

                opciones.add(opcion)
            }

            val pregunta = Pregunta(
                id = id,
                texto = texto,
                opciones = opciones
            )

            preguntas.add(pregunta)
        }

        return preguntas
    }
}