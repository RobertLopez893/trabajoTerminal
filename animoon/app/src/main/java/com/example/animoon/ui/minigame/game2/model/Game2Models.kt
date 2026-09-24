package com.example.animoon.ui.minigame.game2.model


/**
 * Categorías internas de los mensajes.
 *
 * El jugador NO verá estos nombres.
 */
enum class CategoriaMensaje {

    PERSONAL,
    JUEGO,
    ESCOLAR,
    ENTRETENIMIENTO
}


/**
 * Destinos disponibles.
 */
enum class DestinoConexion {

    PADRES,
    PROFESORES,
    ANIMOON
}


/**
 * Mensaje que participa dentro
 * de una ronda.
 */
data class MensajeJuego(

    val id: Int,

    val texto: String,

    val categoria: CategoriaMensaje
)


/**
 * Conexión creada por el jugador.
 */
data class Conexion(

    val mensajeId: Int,

    val destino: DestinoConexion
)


/**
 * Representa una ronda completa.
 *
 * Cada ronda contiene exactamente
 * cuatro mensajes.
 */
data class RondaJuego(

    val numero: Int,

    val mensajes: List<MensajeJuego>
) {

    init {

        /*
         * Por diseño, todas las rondas
         * deben contener cuatro mensajes.
         */
        require(
            mensajes.size == 4
        ) {
            "Una ronda del Minijuego 2 debe contener exactamente 4 mensajes."
        }


        /*
         * Cada uno debe pertenecer a una
         * categoría diferente.
         *
         * Es decir:
         *
         * PERSONAL
         * JUEGO
         * ESCOLAR
         * ENTRETENIMIENTO
         */
        require(
            mensajes
                .map { it.categoria }
                .toSet()
                .size == 4
        ) {
            "La ronda debe contener una categoría diferente por mensaje."
        }
    }
}