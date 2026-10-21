package com.example.animoon.ui.minigame.game3.data

import android.content.Context
import android.util.Log
import com.example.animoon.data.network.ApiClient
import com.example.animoon.ui.minigame.game3.model.Game3Conversacion
import com.example.animoon.ui.minigame.game3.model.Game3Mensaje
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import org.json.JSONObject

class Game3Repository(
    private val context: Context
) {

    companion object {
        private const val TAG = "Game3Repository"
        private const val ARCHIVO_LOCAL = "game3_conversaciones.json"
        private const val TIEMPO_ESPERA_SERVIDOR_MS = 5000L
    }

    suspend fun obtenerPartida(cantidad: Int): List<Game3Conversacion> =
        withContext(Dispatchers.IO) {
            val desdeServidor = withTimeoutOrNull(TIEMPO_ESPERA_SERVIDOR_MS) {
                cargarDesdeServidor(cantidad)
            } ?: emptyList()

            if (desdeServidor.isNotEmpty()) {
                desdeServidor
            } else {
                armarPartida(cargarDesdeAssets(), cantidad)
            }
        }

    private suspend fun cargarDesdeServidor(cantidad: Int): List<Game3Conversacion> {
        return try {
            val respuesta = ApiClient.minigameService.obtenerConversacionesGame3(cantidad)

            if (respuesta.isSuccessful) {
                parsear(respuesta.body()?.string().orEmpty())
            } else {
                Log.w(TAG, "El servidor respondió ${respuesta.code()}, se usarán las conversaciones locales")
                emptyList()
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            Log.w(TAG, "No se pudo contactar al servidor, se usarán las conversaciones locales", e)
            emptyList()
        }
    }

    private fun cargarDesdeAssets(): List<Game3Conversacion> {
        val json = context.assets
            .open(ARCHIVO_LOCAL)
            .bufferedReader()
            .use { it.readText() }

        return parsear(json)
    }

    private fun parsear(json: String): List<Game3Conversacion> {
        val arreglo = JSONObject(json).getJSONArray("conversaciones")
        val lista = mutableListOf<Game3Conversacion>()

        for (i in 0 until arreglo.length()) {
            val conversacionJson = arreglo.getJSONObject(i)
            val mensajesJson = conversacionJson.getJSONArray("mensajes")
            val mensajes = mutableListOf<Game3Mensaje>()

            for (j in 0 until mensajesJson.length()) {
                val mensajeJson = mensajesJson.getJSONObject(j)

                mensajes.add(
                    Game3Mensaje(
                        delJugador = mensajeJson.getString("emisor") == "yo",
                        texto = mensajeJson.getString("texto")
                    )
                )
            }

            if (mensajes.isEmpty()) {
                continue
            }

            lista.add(
                Game3Conversacion(
                    id = conversacionJson.getString("id"),
                    contacto = conversacionJson.getString("contacto"),
                    hayRiesgo = conversacionJson.getBoolean("riesgo"),
                    mensajes = mensajes,
                    retroalimentacion = conversacionJson.getString("retroalimentacion")
                )
            )
        }

        return lista
    }

    private fun armarPartida(
        todas: List<Game3Conversacion>,
        cantidad: Int
    ): List<Game3Conversacion> {
        val conRiesgo = todas.filter { it.hayRiesgo }.shuffled()
        val seguras = todas.filter { !it.hayRiesgo }.shuffled()

        val total = minOf(cantidad, todas.size)
        val minimoRiesgo = minOf(2, conRiesgo.size, total)
        val maximoRiesgo = maxOf(minimoRiesgo, minOf(3, conRiesgo.size, total))

        var cantidadRiesgo = (minimoRiesgo..maximoRiesgo).random()
        var cantidadSeguras = total - cantidadRiesgo

        if (cantidadSeguras > seguras.size) {
            cantidadSeguras = seguras.size
            cantidadRiesgo = total - cantidadSeguras
        }

        return (conRiesgo.take(cantidadRiesgo) + seguras.take(cantidadSeguras)).shuffled()
    }
}
