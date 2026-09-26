package com.example.animoon.ui.minigame.game2.model


enum class CategoriaMensaje {

    PERSONAL,

    JUEGO,

    ESCOLAR,

    ENTRETENIMIENTO
}


enum class DestinoConexion {

    PADRES,

    PROFESORES,

    ANIMOON
}


data class MensajeJuego(

    val id: Int,

    val texto: String,

    val categoria: CategoriaMensaje,

    val explicacion: String
)


data class Conexion(

    val mensajeId: Int,

    val destino: DestinoConexion
)


data class RondaJuego(

    val numero: Int,

    val mensajes: List<MensajeJuego>
) {

    init {

        require(mensajes.size == 4) {
            "Cada ronda debe contener exactamente 4 mensajes."
        }


        require(
            mensajes
                .map { it.categoria }
                .toSet()
                .size == 4
        ) {

            "Cada ronda debe contener una categoría diferente."
        }
    }
}