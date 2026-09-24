package com.example.animoon.ui.minigame.game2

import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.game2.model.CategoriaMensaje
import com.example.animoon.ui.minigame.game2.model.Conexion
import com.example.animoon.ui.minigame.game2.model.DestinoConexion
import com.example.animoon.ui.minigame.game2.model.MensajeJuego
import com.example.animoon.ui.minigame.game2.model.RondaJuego
import com.example.animoon.ui.minigame.game2.view.CableBoardView
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch


class Game2Activity : BaseActivity() {


    // =========================================================
    // CONFIGURACIÓN GENERAL
    // =========================================================

    companion object {

        const val TOTAL_RONDAS = 5
    }


    /**
     * Los colores pertenecen a las posiciones visuales
     * de los cuatro puertos superiores.
     *
     * NO dependen del ID del mensaje.
     */
    private val coloresCables =
        listOf(

            Color.parseColor("#6674D9"),

            Color.parseColor("#43A5A5"),

            Color.parseColor("#E79846"),

            Color.parseColor("#B967C7")
        )


    // =========================================================
    // DATOS DE LA PARTIDA
    // =========================================================

    private var rondaActual =
        1


    private var puntaje =
        0


    /**
     * Ronda que actualmente se encuentra
     * jugando el usuario.
     */
    private lateinit var datosRondaActual:
            RondaJuego


    /**
     * Evita modificar una ronda después
     * de pulsar COMPROBAR.
     */
    private var rondaBloqueada =
        false


    // =========================================================
    // MENSAJES TEMPORALES
    // =========================================================

    /**
     * IMPORTANTE:
     *
     * Estos cuatro mensajes existen únicamente
     * para probar el funcionamiento del juego.
     *
     * Serán sustituidos cuando Silvia entregue
     * el documento con las situaciones reales.
     */
    private val mensajesTemporales =
        listOf(

            MensajeJuego(
                id = 101,
                texto = "Mensaje de prueba A",
                categoria = CategoriaMensaje.PERSONAL
            ),

            MensajeJuego(
                id = 102,
                texto = "Mensaje de prueba B",
                categoria = CategoriaMensaje.JUEGO
            ),

            MensajeJuego(
                id = 103,
                texto = "Mensaje de prueba C",
                categoria = CategoriaMensaje.ESCOLAR
            ),

            MensajeJuego(
                id = 104,
                texto = "Mensaje de prueba D",
                categoria = CategoriaMensaje.ENTRETENIMIENTO
            )
        )


    // =========================================================
    // ESTADO DE INTERACCIÓN
    // =========================================================

    /**
     * ID lógico del mensaje seleccionado.
     *
     * No representa su posición visual.
     */
    private var mensajeSeleccionadoId:
            Int? =
        null


    /**
     * Conexiones creadas durante
     * la ronda actual.
     */
    private val conexiones =
        mutableSetOf<Conexion>()


    // =========================================================
    // HUD
    // =========================================================

    private lateinit var txtRound:
            TextView

    private lateinit var txtScore:
            TextView


    // =========================================================
    // PUERTOS DE SALIDA
    // =========================================================

    private lateinit var btnOutput1:
            MaterialButton

    private lateinit var btnOutput2:
            MaterialButton

    private lateinit var btnOutput3:
            MaterialButton

    private lateinit var btnOutput4:
            MaterialButton


    /**
     * Representa las cuatro POSICIONES
     * disponibles en la parte superior.
     */
    private lateinit var botonesSalida:
            List<MaterialButton>


    // =========================================================
    // PUERTOS DE ENTRADA
    // =========================================================

    private lateinit var btnParents:
            MaterialButton

    private lateinit var btnTeachers:
            MaterialButton

    private lateinit var btnAnimoon:
            MaterialButton


    // =========================================================
    // TABLERO
    // =========================================================

    private lateinit var cableBoard:
            CableBoardView


    // =========================================================
    // COMPROBAR
    // =========================================================

    private lateinit var btnCheck:
            MaterialButton


    // =========================================================
    // ON CREATE
    // =========================================================

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {

        super.onCreate(
            savedInstanceState
        )


        setContentView(
            R.layout.activity_game2
        )


        inicializarVistas()

        configurarBotones()

        prepararPartida()
    }


    // =========================================================
    // INICIALIZACIÓN DE VISTAS
    // =========================================================

    private fun inicializarVistas() {


        // -----------------------------------------------------
        // HUD
        // -----------------------------------------------------

        txtRound =
            findViewById(
                R.id.txtGame2Round
            )


        txtScore =
            findViewById(
                R.id.txtGame2Score
            )


        // -----------------------------------------------------
        // SALIDAS
        // -----------------------------------------------------

        btnOutput1 =
            findViewById(
                R.id.btnOutput1
            )


        btnOutput2 =
            findViewById(
                R.id.btnOutput2
            )


        btnOutput3 =
            findViewById(
                R.id.btnOutput3
            )


        btnOutput4 =
            findViewById(
                R.id.btnOutput4
            )


        botonesSalida =
            listOf(

                btnOutput1,
                btnOutput2,
                btnOutput3,
                btnOutput4
            )


        // -----------------------------------------------------
        // DESTINOS
        // -----------------------------------------------------

        btnParents =
            findViewById(
                R.id.btnParents
            )


        btnTeachers =
            findViewById(
                R.id.btnTeachers
            )


        btnAnimoon =
            findViewById(
                R.id.btnAnimoon
            )


        // -----------------------------------------------------
        // TABLERO
        // -----------------------------------------------------

        cableBoard =
            findViewById(
                R.id.cableBoard
            )


        // -----------------------------------------------------
        // COMPROBAR
        // -----------------------------------------------------

        btnCheck =
            findViewById(
                R.id.btnGame2Check
            )
    }


    // =========================================================
    // CONFIGURAR BOTONES
    // =========================================================

    private fun configurarBotones() {


        // -----------------------------------------------------
        // PUERTOS SUPERIORES
        // -----------------------------------------------------

        botonesSalida.forEach { boton ->

            boton.setOnClickListener {


                val mensajeId =
                    boton.tag as? Int


                if (mensajeId != null) {

                    seleccionarMensaje(
                        mensajeId
                    )
                }
            }
        }


        // -----------------------------------------------------
        // DESTINOS
        // -----------------------------------------------------

        btnParents.setOnClickListener {

            alternarConexion(
                DestinoConexion.PADRES
            )
        }


        btnTeachers.setOnClickListener {

            alternarConexion(
                DestinoConexion.PROFESORES
            )
        }


        btnAnimoon.setOnClickListener {

            alternarConexion(
                DestinoConexion.ANIMOON
            )
        }


        // -----------------------------------------------------
        // COMPROBAR
        // -----------------------------------------------------

        btnCheck.setOnClickListener {

            comprobarRondaTemporal()
        }
    }


    // =========================================================
    // PREPARAR PARTIDA
    // =========================================================

    private fun prepararPartida() {

        rondaActual =
            1


        puntaje =
            0


        prepararRonda(
            rondaActual
        )


        actualizarHud()
    }


    // =========================================================
    // CREAR RONDA TEMPORAL
    // =========================================================

    /**
     * Por ahora utilizamos siempre los cuatro
     * mensajes temporales.
     *
     * shuffled() modifica únicamente
     * su posición visual.
     */
    private fun crearRondaTemporal(
        numero: Int
    ): RondaJuego {


        val mensajesAleatorios =

            mensajesTemporales
                .shuffled()


        return RondaJuego(

            numero = numero,

            mensajes = mensajesAleatorios
        )
    }


    // =========================================================
    // PREPARAR RONDA
    // =========================================================

    private fun prepararRonda(
        numero: Int
    ) {


        // -----------------------------------------------------
        // CREAR RONDA
        // -----------------------------------------------------

        datosRondaActual =
            crearRondaTemporal(
                numero
            )


        // -----------------------------------------------------
        // REINICIAR ESTADO
        // -----------------------------------------------------

        rondaBloqueada =
            false


        mensajeSeleccionadoId =
            null


        conexiones.clear()


        // -----------------------------------------------------
        // MOSTRAR MENSAJES
        // -----------------------------------------------------

        mostrarMensajesRonda()


        // -----------------------------------------------------
        // CONFIGURAR TABLERO
        // -----------------------------------------------------

        configurarPuertosCableBoard()

        configurarColoresCableBoard()


        // -----------------------------------------------------
        // LIMPIAR CABLES
        // -----------------------------------------------------

        cableBoard.actualizarConexiones(
            conexiones
        )


        // -----------------------------------------------------
        // REACTIVAR BOTONES
        // -----------------------------------------------------

        habilitarInteraccionRonda(
            true
        )


        btnCheck.text =
            "Comprobar"


        actualizarSeleccionVisual()

        actualizarEstadoBotonComprobar()


        // -----------------------------------------------------
        // LOG
        // -----------------------------------------------------

        Log.d(

            "Game2Activity",

            "Ronda $numero - orden: " +
                    datosRondaActual
                        .mensajes
                        .map {
                            "${it.id}-${it.categoria}"
                        }
        )
    }


    // =========================================================
    // MOSTRAR MENSAJES
    // =========================================================

    private fun mostrarMensajesRonda() {


        datosRondaActual
            .mensajes
            .forEachIndexed {

                    indice,
                    mensaje ->


                val boton =
                    botonesSalida[indice]


                /*
                 * Texto visible.
                 */
                boton.text =
                    mensaje.texto


                /*
                 * ID lógico correspondiente
                 * al mensaje actual.
                 */
                boton.tag =
                    mensaje.id
            }
    }


    // =========================================================
    // CONFIGURAR PUERTOS DEL CABLE BOARD
    // =========================================================

    private fun configurarPuertosCableBoard() {


        val salidas =
            mutableMapOf<Int, View>()


        botonesSalida.forEach { boton ->


            val mensajeId =
                boton.tag as? Int


            if (mensajeId != null) {

                salidas[mensajeId] =
                    boton
            }
        }


        val destinos:
                Map<DestinoConexion, View> =
            mapOf(

                DestinoConexion.PADRES
                        to btnParents,

                DestinoConexion.PROFESORES
                        to btnTeachers,

                DestinoConexion.ANIMOON
                        to btnAnimoon
            )


        cableBoard.configurarPuertos(

            salidas = salidas,

            destinos = destinos
        )
    }


    // =========================================================
    // CONFIGURAR COLORES DE CABLES
    // =========================================================

    /**
     * El color depende de la posición
     * visual del botón durante la ronda.
     */
    private fun configurarColoresCableBoard() {


        val colores =
            mutableMapOf<Int, Int>()


        botonesSalida.forEachIndexed {

                indice,
                boton ->


            val mensajeId =
                boton.tag as? Int


            if (mensajeId != null) {

                colores[mensajeId] =
                    coloresCables[indice]
            }
        }


        cableBoard.configurarColores(
            colores
        )
    }


    // =========================================================
    // SELECCIÓN DE MENSAJE
    // =========================================================

    private fun seleccionarMensaje(
        mensajeId: Int
    ) {


        /*
         * Protección adicional.
         */
        if (rondaBloqueada) {

            return
        }


        /*
         * Tocar nuevamente el mismo mensaje
         * elimina la selección.
         */
        mensajeSeleccionadoId =

            if (
                mensajeSeleccionadoId ==
                mensajeId
            ) {

                null

            } else {

                mensajeId
            }


        actualizarSeleccionVisual()
    }


    // =========================================================
    // CREAR / ELIMINAR CONEXIÓN
    // =========================================================

    private fun alternarConexion(
        destino: DestinoConexion
    ) {


        /*
         * Protección adicional.
         */
        if (rondaBloqueada) {

            return
        }


        val mensajeId =
            mensajeSeleccionadoId


        /*
         * No puede existir un cable sin
         * seleccionar primero una salida.
         */
        if (mensajeId == null) {

            Toast.makeText(

                this,

                "Selecciona primero un mensaje",

                Toast.LENGTH_SHORT

            ).show()


            return
        }


        val conexion =
            Conexion(

                mensajeId = mensajeId,

                destino = destino
            )


        /*
         * Toggle:
         *
         * existe    → eliminar
         * no existe → agregar
         */
        if (
            conexiones.contains(
                conexion
            )
        ) {

            conexiones.remove(
                conexion
            )

        } else {

            conexiones.add(
                conexion
            )
        }


        /*
         * Actualizamos visualmente
         * los cables.
         */
        cableBoard.actualizarConexiones(
            conexiones
        )


        /*
         * Revisamos si los cuatro mensajes
         * tienen al menos una conexión.
         */
        actualizarEstadoBotonComprobar()
    }


    // =========================================================
    // SELECCIÓN VISUAL
    // =========================================================

    private fun actualizarSeleccionVisual() {


        botonesSalida.forEach { boton ->


            val mensajeId =
                boton.tag as? Int


            val seleccionado =

                mensajeId != null &&
                        mensajeId ==
                        mensajeSeleccionadoId


            actualizarEstiloSalida(

                boton,

                seleccionado
            )
        }
    }


    private fun actualizarEstiloSalida(

        boton: MaterialButton,

        seleccionado: Boolean
    ) {


        if (seleccionado) {


            boton.strokeWidth =
                dpToPx(4)


            boton.strokeColor =
                ColorStateList.valueOf(

                    Color.parseColor(
                        "#6674D9"
                    )
                )


            boton.backgroundTintList =
                ColorStateList.valueOf(

                    Color.parseColor(
                        "#E8EBFF"
                    )
                )


        } else {


            boton.strokeWidth =
                dpToPx(2)


            boton.strokeColor =
                ColorStateList.valueOf(

                    Color.parseColor(
                        "#AEBBF0"
                    )
                )


            boton.backgroundTintList =
                ColorStateList.valueOf(
                    Color.WHITE
                )
        }
    }


    // =========================================================
    // ESTADO DEL BOTÓN COMPROBAR
    // =========================================================

    private fun actualizarEstadoBotonComprobar() {


        /*
         * Una ronda ya enviada
         * nunca puede volver a comprobarse.
         */
        if (rondaBloqueada) {

            btnCheck.isEnabled =
                false


            btnCheck.alpha =
                0.45f


            return
        }


        /*
         * Mensajes que tienen al menos
         * una conexión.
         */
        val mensajesConConexion =

            conexiones
                .map {
                    it.mensajeId
                }
                .toSet()


        /*
         * COMPROBAR solo se habilita
         * cuando los cuatro mensajes
         * tienen al menos un cable.
         */
        val puedeComprobar =

            mensajesConConexion.size ==
                    datosRondaActual
                        .mensajes
                        .size


        btnCheck.isEnabled =
            puedeComprobar


        btnCheck.alpha =

            if (puedeComprobar) {

                1f

            } else {

                0.45f
            }
    }


    // =========================================================
    // COMPROBAR RONDA
    // =========================================================

    /**
     * TEMPORAL.
     *
     * Todavía no evalúa si las conexiones
     * realizadas son correctas.
     *
     * Esa validación será el siguiente punto.
     */
    private fun comprobarRondaTemporal() {


        if (rondaBloqueada) {

            return
        }


        // -----------------------------------------------------
        // BLOQUEAR RONDA
        // -----------------------------------------------------

        rondaBloqueada =
            true


        habilitarInteraccionRonda(
            false
        )


        btnCheck.isEnabled =
            false


        btnCheck.alpha =
            0.45f


        // -----------------------------------------------------
        // MENSAJE TEMPORAL
        // -----------------------------------------------------

        Toast.makeText(

            this,

            "Ronda $rondaActual completada",

            Toast.LENGTH_SHORT

        ).show()


        // -----------------------------------------------------
        // ESPERA TEMPORAL
        // -----------------------------------------------------

        /*
         * Posteriormente estos 900 ms
         * serán sustituidos por el modal
         * de retroalimentación.
         */
        lifecycleScope.launch {


            delay(900)


            if (
                rondaActual <
                TOTAL_RONDAS
            ) {

                avanzarRonda()

            } else {

                finalizarPartidaTemporal()
            }
        }
    }


    // =========================================================
    // HABILITAR / DESHABILITAR INTERACCIÓN
    // =========================================================

    private fun habilitarInteraccionRonda(
        habilitada: Boolean
    ) {


        botonesSalida.forEach {

            it.isEnabled =
                habilitada
        }


        btnParents.isEnabled =
            habilitada


        btnTeachers.isEnabled =
            habilitada


        btnAnimoon.isEnabled =
            habilitada
    }


    // =========================================================
    // AVANZAR RONDA
    // =========================================================

    private fun avanzarRonda() {


        rondaActual++


        prepararRonda(
            rondaActual
        )


        actualizarHud()
    }


    // =========================================================
    // FINAL TEMPORAL
    // =========================================================

    private fun finalizarPartidaTemporal() {


        rondaBloqueada =
            true


        habilitarInteraccionRonda(
            false
        )


        btnCheck.isEnabled =
            false


        /*
         * Lo dejamos completamente visible
         * para mostrar el estado final.
         */
        btnCheck.alpha =
            1f


        btnCheck.text =
            "Partida completada"


        Toast.makeText(

            this,

            "¡Prueba completada! Se jugaron las 5 rondas.",

            Toast.LENGTH_LONG

        ).show()
    }


    // =========================================================
    // HUD
    // =========================================================

    private fun actualizarHud() {


        txtRound.text =
            "Ronda $rondaActual de $TOTAL_RONDAS"


        txtScore.text =
            "★ $puntaje"
    }


    // =========================================================
    // UTILIDADES
    // =========================================================

    private fun dpToPx(
        dp: Int
    ): Int {


        return (

                dp *
                        resources
                            .displayMetrics
                            .density

                ).toInt()
    }
}