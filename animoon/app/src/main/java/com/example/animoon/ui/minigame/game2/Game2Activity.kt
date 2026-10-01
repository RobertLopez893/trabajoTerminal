package com.example.animoon.ui.minigame.game2

import android.app.Dialog
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.game2.model.CategoriaMensaje
import com.example.animoon.ui.minigame.game2.model.Conexion
import com.example.animoon.ui.minigame.game2.model.DestinoConexion
import com.example.animoon.ui.minigame.game2.model.MensajeJuego
import com.example.animoon.ui.minigame.game2.model.RondaJuego
import com.example.animoon.ui.minigame.game2.view.CableBoardView
import com.google.android.material.button.MaterialButton


class Game2Activity : BaseActivity() {


    companion object {
        const val TOTAL_RONDAS = 5
        const val MENSAJES_POR_RONDA = 4
        const val PUNTOS_POR_CASO = 5

        const val PUNTAJE_MAXIMO =
            TOTAL_RONDAS * MENSAJES_POR_RONDA * PUNTOS_POR_CASO
    }


    // =========================================================
    // COLORES
    // =========================================================

    private val coloresCables =
        listOf(

            Color.parseColor("#6674D9"),

            Color.parseColor("#43A5A5"),

            Color.parseColor("#E79846"),

            Color.parseColor("#B967C7")
        )


    // =========================================================
    // PARTIDA
    // =========================================================

    private lateinit var rondasPartida:
            List<RondaJuego>


    private lateinit var datosRondaActual:
            RondaJuego


    private var rondaActual =
        1


    private var puntaje =
        0


    private var rondaBloqueada =
        false


    private var juegoPausado =
        false


    // =========================================================
    // INTERACCIÓN
    // =========================================================

    private var mensajeSeleccionadoId:
            Int? =
        null


    private val conexiones =
        mutableSetOf<Conexion>()


    // =========================================================
    // VISTAS
    // =========================================================

    private lateinit var txtRound:
            TextView


    private lateinit var txtScore:
            TextView


    private lateinit var btnOutput1:
            MaterialButton


    private lateinit var btnOutput2:
            MaterialButton


    private lateinit var btnOutput3:
            MaterialButton


    private lateinit var btnOutput4:
            MaterialButton


    private lateinit var botonesSalida:
            List<MaterialButton>


    private lateinit var btnParents:
            MaterialButton


    private lateinit var btnTeachers:
            MaterialButton


    private lateinit var btnAnimoon:
            MaterialButton


    private lateinit var btnCheck:
            MaterialButton


    private lateinit var btnPause:
            ImageButton


    private lateinit var cableBoard:
            CableBoardView


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

        configurarBotonAtras()

        prepararPartida()
    }


    // =========================================================
    // VISTAS
    // =========================================================

    private fun inicializarVistas() {


        txtRound =
            findViewById(
                R.id.txtGame2Round
            )


        txtScore =
            findViewById(
                R.id.txtGame2Score
            )


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


        btnCheck =
            findViewById(
                R.id.btnGame2Check
            )


        btnPause =
            findViewById(
                R.id.btnGame2Pause
            )


        cableBoard =
            findViewById(
                R.id.cableBoard
            )
    }


    // =========================================================
    // BOTONES
    // =========================================================

    private fun configurarBotones() {


        botonesSalida.forEach { boton ->


            boton.setOnClickListener {


                if (
                    rondaBloqueada ||
                    juegoPausado
                ) {

                    return@setOnClickListener
                }


                val mensajeId =
                    boton.tag as? Int


                if (mensajeId != null) {

                    seleccionarMensaje(
                        mensajeId
                    )
                }
            }
        }


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


        btnCheck.setOnClickListener {

            comprobarRonda()
        }


        btnPause.setOnClickListener {

            mostrarDialogPausa()
        }
    }


    private fun configurarBotonAtras() {


        onBackPressedDispatcher.addCallback(

            this,

            object :
                OnBackPressedCallback(true) {


                override fun handleOnBackPressed() {

                    mostrarDialogPausa()
                }
            }
        )
    }


    // =========================================================
    // PREPARAR PARTIDA
    // =========================================================

    private fun prepararPartida() {


        rondaActual =
            1


        puntaje =
            0


        rondasPartida =
            generarRondasPartida()


        prepararRonda(
            rondaActual
        )


        actualizarHud()
    }


    // =========================================================
    // GENERACIÓN REAL
    // =========================================================

    private fun generarRondasPartida():
            List<RondaJuego> {


        require(
            Game2MessageBank
                .personales
                .size >= TOTAL_RONDAS
        )


        require(
            Game2MessageBank
                .juego
                .size >= TOTAL_RONDAS
        )


        require(
            Game2MessageBank
                .escolares
                .size >= TOTAL_RONDAS
        )


        require(
            Game2MessageBank
                .entretenimiento
                .size >= TOTAL_RONDAS
        )


        /*
         * Seleccionamos cinco mensajes DIFERENTES
         * de cada categoría.
         *
         * Por ello ninguna situación puede repetirse
         * dentro de la misma partida.
         */
        val personales =
            Game2MessageBank
                .personales
                .shuffled()
                .take(TOTAL_RONDAS)


        val juego =
            Game2MessageBank
                .juego
                .shuffled()
                .take(TOTAL_RONDAS)


        val escolares =
            Game2MessageBank
                .escolares
                .shuffled()
                .take(TOTAL_RONDAS)


        val entretenimiento =
            Game2MessageBank
                .entretenimiento
                .shuffled()
                .take(TOTAL_RONDAS)


        return (0 until TOTAL_RONDAS)
            .map { indice ->


                val mensajes =
                    listOf(

                        personales[indice],

                        juego[indice],

                        escolares[indice],

                        entretenimiento[indice]
                    )
                        .shuffled()


                RondaJuego(

                    numero =
                        indice + 1,

                    mensajes =
                        mensajes
                )
            }
    }


    // =========================================================
    // PREPARAR RONDA
    // =========================================================

    private fun prepararRonda(
        numero: Int
    ) {


        datosRondaActual =
            rondasPartida[
                numero - 1
            ]


        rondaBloqueada =
            false


        juegoPausado =
            false


        mensajeSeleccionadoId =
            null


        conexiones.clear()


        mostrarMensajesRonda()

        configurarPuertosCableBoard()

        configurarColoresCableBoard()


        cableBoard.actualizarConexiones(
            conexiones
        )


        habilitarInteraccionRonda(
            true
        )


        btnPause.isEnabled =
            true


        actualizarSeleccionVisual()

        actualizarEstadoBotonComprobar()

        actualizarHud()
    }


    private fun mostrarMensajesRonda() {


        datosRondaActual
            .mensajes
            .forEachIndexed {

                    indice,
                    mensaje ->


                val boton =
                    botonesSalida[
                        indice
                    ]


                boton.text =
                    mensaje.texto


                boton.tag =
                    mensaje.id
            }
    }


    // =========================================================
    // CABLE BOARD
    // =========================================================

    private fun configurarPuertosCableBoard() {


        val salidas =
            mutableMapOf<Int, View>()


        botonesSalida.forEach { boton ->


            val mensajeId =
                boton.tag as? Int


            if (mensajeId != null) {

                salidas[
                    mensajeId
                ] =
                    boton
            }
        }


        val destinos =
            mapOf(

                DestinoConexion.PADRES
                        to btnParents,

                DestinoConexion.PROFESORES
                        to btnTeachers,

                DestinoConexion.ANIMOON
                        to btnAnimoon
            )


        cableBoard.configurarPuertos(

            salidas =
                salidas,

            destinos =
                destinos
        )
    }


    private fun configurarColoresCableBoard() {


        val colores =
            mutableMapOf<Int, Int>()


        botonesSalida
            .forEachIndexed {

                    indice,
                    boton ->


                val mensajeId =
                    boton.tag as? Int


                if (mensajeId != null) {

                    colores[
                        mensajeId
                    ] =
                        coloresCables[
                            indice
                        ]
                }
            }


        cableBoard.configurarColores(
            colores
        )
    }


    // =========================================================
    // SELECCIÓN
    // =========================================================

    private fun seleccionarMensaje(
        mensajeId: Int
    ) {


        if (
            rondaBloqueada ||
            juegoPausado
        ) {

            return
        }


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


    private fun alternarConexion(
        destino: DestinoConexion
    ) {


        if (
            rondaBloqueada ||
            juegoPausado
        ) {

            return
        }


        val mensajeId =
            mensajeSeleccionadoId


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

                mensajeId =
                    mensajeId,

                destino =
                    destino
            )


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


        cableBoard.actualizarConexiones(
            conexiones
        )


        actualizarEstadoBotonComprobar()
    }


    // =========================================================
    // ESTILO
    // =========================================================

    private fun actualizarSeleccionVisual() {


        botonesSalida.forEach { boton ->


            val mensajeId =
                boton.tag as? Int


            actualizarEstiloSalida(

                boton,

                mensajeId != null &&
                        mensajeId ==
                        mensajeSeleccionadoId
            )
        }
    }


    private fun actualizarEstiloSalida(

        boton: MaterialButton,

        seleccionado: Boolean
    ) {


        if (seleccionado) {


            boton.strokeWidth =
                dpToPx(
                    4
                )


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
                dpToPx(
                    2
                )


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
    // COMPROBAR
    // =========================================================

    private fun actualizarEstadoBotonComprobar() {


        if (
            rondaBloqueada ||
            juegoPausado
        ) {

            btnCheck.isEnabled =
                false


            btnCheck.alpha =
                0.45f


            return
        }


        val mensajesConConexion =
            conexiones
                .map {
                    it.mensajeId
                }
                .toSet()


        val puedeComprobar =

            mensajesConConexion.size ==
                    MENSAJES_POR_RONDA


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
    // REGLAS
    // =========================================================

    private fun obtenerDestinosCorrectos(
        categoria: CategoriaMensaje
    ): Set<DestinoConexion> {


        return when (
            categoria
        ) {


            CategoriaMensaje.PERSONAL,
            CategoriaMensaje.ESCOLAR -> {

                setOf(

                    DestinoConexion.PADRES,

                    DestinoConexion.PROFESORES
                )
            }


            CategoriaMensaje.JUEGO,
            CategoriaMensaje.ENTRETENIMIENTO -> {

                setOf(

                    DestinoConexion.PADRES,

                    DestinoConexion.PROFESORES,

                    DestinoConexion.ANIMOON
                )
            }
        }
    }


    private fun obtenerDestinosSeleccionados(
        mensajeId: Int
    ): Set<DestinoConexion> {


        return conexiones
            .filter {

                it.mensajeId ==
                        mensajeId
            }
            .map {

                it.destino
            }
            .toSet()
    }


    private fun comprobarRonda() {


        if (
            rondaBloqueada ||
            juegoPausado
        ) {

            return
        }


        rondaBloqueada =
            true


        habilitarInteraccionRonda(
            false
        )


        btnPause.isEnabled =
            false


        var puntosRonda =
            0


        val resultados =
            datosRondaActual
                .mensajes
                .map { mensaje ->


                    val correctos =
                        obtenerDestinosCorrectos(
                            mensaje.categoria
                        )


                    val seleccionados =
                        obtenerDestinosSeleccionados(
                            mensaje.id
                        )


                    val esCorrecto =
                        seleccionados ==
                                correctos


                    if (esCorrecto) {

                        puntosRonda++
                    }


                    mensaje to
                            esCorrecto
                }


        puntaje += puntosRonda * PUNTOS_POR_CASO


        actualizarHud()


        mostrarFeedbackRonda(

            resultados =
                resultados,

            puntosRonda =
                puntosRonda
        )
    }


    // =========================================================
    // FEEDBACK
    // =========================================================

    private fun mostrarFeedbackRonda(

        resultados:
        List<Pair<MensajeJuego, Boolean>>,

        puntosRonda: Int
    ) {


        val dialog =
            Dialog(
                this
            )


        dialog.setContentView(
            R.layout.dialog_game2_feedback
        )


        dialog.setCancelable(
            false
        )


        dialog.setCanceledOnTouchOutside(
            false
        )


        dialog.window
            ?.setBackgroundDrawable(
                ColorDrawable(
                    Color.TRANSPARENT
                )
            )


        val txtTitle =
            dialog.findViewById<TextView>(
                R.id.txtGame2FeedbackTitle
            )


        val txtScore =
            dialog.findViewById<TextView>(
                R.id.txtGame2FeedbackScore
            )


        val txtMessage =
            dialog.findViewById<TextView>(
                R.id.txtGame2FeedbackMessage
            )


        val btnContinue =
            dialog.findViewById<MaterialButton>(
                R.id.btnGame2FeedbackContinue
            )


        txtTitle.text =

            when (
                puntosRonda
            ) {

                4 ->
                    "¡Excelente trabajo!"

                3 ->
                    "¡Muy bien!"

                2 ->
                    "¡Vas aprendiendo!"

                else ->
                    "Revisemos los cables"
            }


        val puntosGanados = puntosRonda * PUNTOS_POR_CASO

        txtScore.text =
            "$puntosRonda de $MENSAJES_POR_RONDA casos correctos · +$puntosGanados puntos"


        txtMessage.text =
            construirTextoFeedback(
                resultados
            )


        btnContinue.setOnClickListener {


            dialog.dismiss()


            if (
                rondaActual <
                TOTAL_RONDAS
            ) {

                rondaActual++


                prepararRonda(
                    rondaActual
                )

            } else {

                finalizarPartida()
            }
        }


        dialog.show()
        ajustarTamanoDialogo(dialog)
    }


    private fun construirTextoFeedback(
        resultados:
        List<Pair<MensajeJuego, Boolean>>
    ): String {


        return resultados
            .joinToString(
                separator =
                    "\n\n"
            ) {

                    (
                        mensaje,
                        correcto
                    ) ->


                if (correcto) {


                    "✅ \"${mensaje.texto}\"\n${mensaje.explicacion}"


                } else {


                    val seleccionados =
                        obtenerDestinosSeleccionados(
                            mensaje.id
                        )


                    val correctos =
                        obtenerDestinosCorrectos(
                            mensaje.categoria
                        )


                    "⚠️ \"${mensaje.texto}\"\n" +
                            "${mensaje.explicacion}\n" +
                            "Elegiste: ${formatearDestinos(seleccionados)}\n" +
                            "Lo correcto era: ${formatearDestinos(correctos)}"
                }
            }
    }


    private fun formatearDestinos(
        destinos:
        Set<DestinoConexion>
    ): String {


        if (destinos.isEmpty()) {

            return "Ninguno"
        }


        return destinos
            .sortedBy {
                it.ordinal
            }
            .joinToString(
                separator =
                    ", "
            ) {

                when (it) {

                    DestinoConexion.PADRES ->
                        "Padres/Tutores"

                    DestinoConexion.PROFESORES ->
                        "Profesores"

                    DestinoConexion.ANIMOON ->
                        "ANIMOON"
                }
            }
    }


    // =========================================================
    // PAUSA
    // =========================================================

    private fun mostrarDialogPausa() {


        if (
            juegoPausado ||
            rondaBloqueada
        ) {

            return
        }


        juegoPausado =
            true


        habilitarInteraccionRonda(
            false
        )


        btnPause.isEnabled =
            false


        val dialog =
            Dialog(
                this
            )


        dialog.setContentView(
            R.layout.dialog_game2_pause
        )


        dialog.setCancelable(
            false
        )


        dialog.setCanceledOnTouchOutside(
            false
        )


        dialog.window
            ?.setBackgroundDrawable(
                ColorDrawable(
                    Color.TRANSPARENT
                )
            )


        val btnContinue =
            dialog.findViewById<MaterialButton>(
                R.id.btnGame2PauseContinue
            )


        val btnExit =
            dialog.findViewById<MaterialButton>(
                R.id.btnGame2PauseExit
            )


        btnContinue.setOnClickListener {


            dialog.dismiss()


            juegoPausado =
                false


            btnPause.isEnabled =
                true


            habilitarInteraccionRonda(
                true
            )


            actualizarEstadoBotonComprobar()
        }


        btnExit.setOnClickListener {


            dialog.dismiss()


            finish()
        }


        dialog.show()
        ajustarTamanoDialogo(dialog)
    }


    // =========================================================
    // INTERACCIÓN
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


        if (!habilitada) {


            btnCheck.isEnabled =
                false


            btnCheck.alpha =
                0.45f


        } else {


            actualizarEstadoBotonComprobar()
        }
    }


    // =========================================================
    // FINAL
    // =========================================================

    private fun finalizarPartida() {


        rondaBloqueada =
            true


        val intent =
            Intent(

                this,

                Game2ResultActivity::class.java
            )


        intent.putExtra(

            Game2ResultActivity.EXTRA_SCORE,

            puntaje
        )


        intent.putExtra(

            Game2ResultActivity.EXTRA_MAX_SCORE,

            PUNTAJE_MAXIMO
        )


        startActivity(
            intent
        )


        /*
         * Quitamos Game2Activity de la pila.
         *
         * Resultado -> finish()
         * regresará a la pantalla que abrió
         * originalmente el minijuego.
         */
        finish()
    }


    // =========================================================
    // HUD
    // =========================================================

    private fun actualizarHud() {


        txtRound.text =
            "Ronda $rondaActual de $TOTAL_RONDAS"


        txtScore.text =
            "★ $puntaje / $PUNTAJE_MAXIMO"
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

                )
            .toInt()
    }
}