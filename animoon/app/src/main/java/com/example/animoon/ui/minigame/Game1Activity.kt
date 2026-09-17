package com.example.animoon.ui.minigame

import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import android.widget.ImageButton
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.game1.data.PreguntasRepository
import com.example.animoon.ui.minigame.game1.model.Pregunta
import com.google.android.material.button.MaterialButton
import android.content.Intent

class Game1Activity : BaseActivity() {

    // ---------------------------------------------------------
    // DATOS DE LA PARTIDA
    // ---------------------------------------------------------

    // 10 preguntas utilizadas durante esta partida
    private lateinit var preguntasPartida: List<Pregunta>

    // Índice de la pregunta que se muestra actualmente
    private var indicePreguntaActual = 0

    // Evita que el jugador pueda responder varias veces
    private var preguntaRespondida = false

    // Puntaje actual
    private var puntaje = 0

    // Número de respuestas correctas
    private var respuestasCorrectas = 0

    // Indica si el minijuego está pausado
    private var juegoPausado = false

    // Referencia al diálogo para evitar abrir varios al mismo tiempo
    private var dialogPausa: Dialog? = null


    // ---------------------------------------------------------
    // ELEMENTOS DEL XML
    // ---------------------------------------------------------

    private lateinit var txtProgress: TextView
    private lateinit var txtScore: TextView
    private lateinit var txtQuestion: TextView
    private lateinit var txtMoonieMessage: TextView

    private lateinit var imgMoonie: ImageView

    private lateinit var btnPause: ImageButton

    private lateinit var btnAnswer1: MaterialButton
    private lateinit var btnAnswer2: MaterialButton
    private lateinit var btnAnswer3: MaterialButton


    companion object {

        // Puntos otorgados por cada respuesta correcta
        private const val PUNTOS_RESPUESTA_CORRECTA = 100
    }


    // ---------------------------------------------------------
    // ON CREATE
    // ---------------------------------------------------------

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game1)

        inicializarVistas()

        configurarBotones()

        prepararPartida()

        mostrarPreguntaActual()
    }


    // ---------------------------------------------------------
    // INICIALIZACIÓN
    // ---------------------------------------------------------

    /**
     * Conecta los elementos de activity_game1.xml
     * con las variables de Kotlin.
     */
    private fun inicializarVistas() {

        txtProgress = findViewById(R.id.txtProgress)
        txtScore = findViewById(R.id.txtScore)
        txtQuestion = findViewById(R.id.txtQuestion)
        txtMoonieMessage = findViewById(R.id.txtMoonieMessage)

        imgMoonie = findViewById(R.id.imgMoonie)

        btnPause = findViewById(R.id.btnPause)

        btnAnswer1 = findViewById(R.id.btnAnswer1)
        btnAnswer2 = findViewById(R.id.btnAnswer2)
        btnAnswer3 = findViewById(R.id.btnAnswer3)
    }


    /**
     * Define qué ocurre cuando el jugador
     * toca cada una de las respuestas.
     */
    private fun configurarBotones() {

        btnAnswer1.setOnClickListener {

            seleccionarRespuesta(0)
        }

        btnAnswer2.setOnClickListener {

            seleccionarRespuesta(1)
        }

        btnAnswer3.setOnClickListener {

            seleccionarRespuesta(2)
        }

        btnPause.setOnClickListener {

            mostrarPausa()
        }
    }


    // ---------------------------------------------------------
    // PREPARACIÓN DE LA PARTIDA
    // ---------------------------------------------------------

    /**
     * Carga todas las preguntas desde el JSON
     * y selecciona 10 al azar.
     */
    private fun prepararPartida() {

        val repository = PreguntasRepository(this)

        val todasLasPreguntas =
            repository.cargarPreguntas()

        preguntasPartida =
            todasLasPreguntas
                .shuffled()
                .take(10)

        // Reiniciamos la partida
        indicePreguntaActual = 0

        puntaje = 0

        respuestasCorrectas = 0

        preguntaRespondida = false


        // Actualizamos los elementos visuales iniciales
        actualizarPuntaje()

        actualizarEstadoMoonie()


        Log.d(
            "Game1Activity",
            "Preguntas cargadas: ${todasLasPreguntas.size}"
        )

        Log.d(
            "Game1Activity",
            "Preguntas seleccionadas: ${preguntasPartida.map { it.id }}"
        )
    }


    // ---------------------------------------------------------
    // MOSTRAR PREGUNTA
    // ---------------------------------------------------------

    /**
     * Muestra la pregunta actual y sus
     * tres respuestas.
     */
    private fun mostrarPreguntaActual() {

        val pregunta =
            preguntasPartida[indicePreguntaActual]

        preguntaRespondida = false


        txtProgress.text =
            "Pregunta ${indicePreguntaActual + 1} de ${preguntasPartida.size}"


        txtQuestion.text =
            pregunta.texto


        btnAnswer1.text =
            pregunta.opciones[0].texto

        btnAnswer2.text =
            pregunta.opciones[1].texto

        btnAnswer3.text =
            pregunta.opciones[2].texto


        /*
         * Mostramos un mensaje relacionado
         * con el estado actual de Moonie.
         */
        actualizarMensajeMoonie()


        habilitarRespuestas()


        Log.d(
            "Game1Activity",
            "Mostrando pregunta ${pregunta.id}"
        )
    }


    // ---------------------------------------------------------
    // RESPUESTA DEL JUGADOR
    // ---------------------------------------------------------

    /**
     * Procesa la respuesta seleccionada.
     */
    private fun seleccionarRespuesta(
        indiceOpcion: Int
    ) {

        /*
         * Impide que el jugador pueda sumar
         * puntos varias veces tocando rápidamente.
         */
        if (preguntaRespondida || juegoPausado) {
            return
        }


        preguntaRespondida = true


        val pregunta =
            preguntasPartida[indicePreguntaActual]


        val opcionSeleccionada =
            pregunta.opciones[indiceOpcion]


        deshabilitarRespuestas()


        /*
         * Si la respuesta es correcta:
         *
         * +100 puntos
         * +1 respuesta correcta
         *
         * y Moonie avanza en su reparación.
         */
        if (opcionSeleccionada.correcta) {

            puntaje +=
                PUNTOS_RESPUESTA_CORRECTA

            respuestasCorrectas++


            actualizarPuntaje()

            actualizarEstadoMoonie()
        }


        /*
         * Moonie reacciona tanto si
         * acertamos como si fallamos.
         */
        reaccionarMoonie(
            opcionSeleccionada.correcta
        )


        Log.d(
            "Game1Activity",
            "Respuesta seleccionada: ${opcionSeleccionada.texto}"
        )

        Log.d(
            "Game1Activity",
            "¿Respuesta correcta?: ${opcionSeleccionada.correcta}"
        )

        Log.d(
            "Game1Activity",
            "Puntaje actual: $puntaje"
        )

        Log.d(
            "Game1Activity",
            "Respuestas correctas: $respuestasCorrectas"
        )


        /*
         * Después mostramos la ventana
         * educativa de retroalimentación.
         */
        mostrarRetroalimentacion(
            mensaje = opcionSeleccionada.retroalimentacion,
            esCorrecta = opcionSeleccionada.correcta
        )
    }


    // ---------------------------------------------------------
    // PUNTAJE
    // ---------------------------------------------------------

    /**
     * Actualiza el puntaje mostrado
     * en el HUD.
     */
    private fun actualizarPuntaje() {

        txtScore.text =
            "★ $puntaje puntos"
    }


    // ---------------------------------------------------------
    // ESTADOS DE MOONIE
    // ---------------------------------------------------------

    /**
     * Regresa la imagen correspondiente
     * al estado actual de reparación.
     *
     * 0 - 2  = Muy averiado
     * 3 - 4  = Averiado
     * 5 - 6  = Medio reparado
     * 7 - 8  = Casi reparado
     * 9 - 10 = Reparado
     */
    private fun obtenerImagenMoonie(): Int {

        return when (respuestasCorrectas) {

            in 0..2 -> {

                R.drawable.moonie_very_damaged
            }

            in 3..4 -> {

                R.drawable.moonie_damaged
            }

            in 5..6 -> {

                R.drawable.moonie_half_repaired
            }

            in 7..8 -> {

                R.drawable.moonie_almost_repaired
            }

            else -> {

                R.drawable.moonie_repaired
            }
        }
    }


    /**
     * Cambia la imagen principal de Moonie
     * según las respuestas correctas.
     */
    private fun actualizarEstadoMoonie() {

        imgMoonie.setImageResource(
            obtenerImagenMoonie()
        )
    }


    /**
     * Actualiza el texto de Moonie
     * dependiendo de cuánto ha avanzado
     * su reparación.
     */
    private fun actualizarMensajeMoonie() {

        txtMoonieMessage.text =
            when (respuestasCorrectas) {

                in 0..2 -> {

                    "¡Vamos! Todavía necesito tu ayuda."
                }

                in 3..4 -> {

                    "¡Está funcionando! Sigue así."
                }

                in 5..6 -> {

                    "¡Ya me siento mucho mejor!"
                }

                in 7..8 -> {

                    "¡Casi lo logramos!"
                }

                else -> {

                    "¡Estoy como nuevo!"
                }
            }
    }


    // ---------------------------------------------------------
    // REACCIONES DE MOONIE
    // ---------------------------------------------------------

    /**
     * Decide qué animación ejecutar
     * según el resultado.
     */
    private fun reaccionarMoonie(
        esCorrecta: Boolean
    ) {

        if (esCorrecta) {

            reaccionCorrectaMoonie()

        } else {

            reaccionIncorrectaMoonie()
        }
    }


    /**
     * Moonie celebra una respuesta correcta.
     */
    private fun reaccionCorrectaMoonie() {

        txtMoonieMessage.text =
            "¡Muy bien! ¡Eso me ayuda mucho!"


        /*
         * Cancelamos cualquier animación
         * anterior antes de comenzar.
         */
        imgMoonie.animate().cancel()


        /*
         * Regresamos las propiedades
         * visuales al estado inicial.
         */
        imgMoonie.scaleX = 1f
        imgMoonie.scaleY = 1f
        imgMoonie.rotation = 0f


        /*
         * Moonie crece ligeramente y
         * hace un pequeño movimiento.
         */
        imgMoonie.animate()
            .scaleX(1.12f)
            .scaleY(1.12f)
            .rotation(4f)
            .setDuration(180)
            .withEndAction {

                /*
                 * Después vuelve a
                 * su posición original.
                 */
                imgMoonie.animate()
                    .scaleX(1f)
                    .scaleY(1f)
                    .rotation(0f)
                    .setDuration(180)
                    .start()
            }
            .start()
    }


    /**
     * Moonie se sacude ligeramente
     * cuando la respuesta es incorrecta.
     */
    private fun reaccionIncorrectaMoonie() {

        txtMoonieMessage.text =
            "¡Oh no! Recuerda elegir siempre la opción más segura."


        imgMoonie.animate().cancel()


        imgMoonie.scaleX = 1f
        imgMoonie.scaleY = 1f
        imgMoonie.rotation = 0f


        /*
         * Pequeña sacudida.
         */
        imgMoonie.animate()
            .rotation(-7f)
            .setDuration(90)
            .withEndAction {

                imgMoonie.animate()
                    .rotation(7f)
                    .setDuration(90)
                    .withEndAction {

                        imgMoonie.animate()
                            .rotation(-5f)
                            .setDuration(90)
                            .withEndAction {

                                imgMoonie.animate()
                                    .rotation(0f)
                                    .setDuration(90)
                                    .start()
                            }
                            .start()
                    }
                    .start()
            }
            .start()
    }

    // ---------------------------------------------------------
    // PAUSA
    // ---------------------------------------------------------

    /**
     * Pausa la partida y muestra
     * las opciones Continuar / Salir.
     */
    private fun mostrarPausa() {

        /*
         * Evitamos crear más de una ventana
         * de pausa al mismo tiempo.
         */
        if (juegoPausado) {
            return
        }


        juegoPausado = true


        /*
         * Mientras estamos pausados
         * no se pueden seleccionar respuestas.
         */
        deshabilitarRespuestas()


        /*
         * Detenemos cualquier animación
         * que Moonie esté ejecutando.
         */
        pausarAnimacionesMoonie()


        /*
         * Evitamos pulsar nuevamente
         * el botón de pausa.
         */
        btnPause.isEnabled = false


        val dialog =
            Dialog(this)


        dialogPausa = dialog


        dialog.setContentView(
            R.layout.dialog_game1_pause
        )


        /*
         * La pausa solamente puede cerrarse
         * utilizando los botones del menú.
         */
        dialog.setCancelable(false)

        dialog.setCanceledOnTouchOutside(false)


        /*
         * Permitimos que se vean correctamente
         * las esquinas redondeadas de la tarjeta.
         */
        dialog.window?.setBackgroundDrawable(
            ColorDrawable(Color.TRANSPARENT)
        )


        val btnPauseContinue =
            dialog.findViewById<MaterialButton>(
                R.id.btnPauseContinue
            )


        val btnPauseExit =
            dialog.findViewById<MaterialButton>(
                R.id.btnPauseExit
            )


        // -----------------------------------------------------
        // CONTINUAR
        // -----------------------------------------------------

        btnPauseContinue.setOnClickListener {

            dialog.dismiss()

            dialogPausa = null

            reanudarPartida()
        }


        // -----------------------------------------------------
        // SALIR
        // -----------------------------------------------------

        btnPauseExit.setOnClickListener {

            dialog.dismiss()

            dialogPausa = null

            salirDePartida()
        }


        dialog.show()
    }


    /**
     * Detiene las animaciones activas
     * del personaje.
     */
    private fun pausarAnimacionesMoonie() {

        imgMoonie.animate().cancel()


        /*
         * Lo dejamos nuevamente en
         * una posición visual estable.
         */
        imgMoonie.scaleX = 1f
        imgMoonie.scaleY = 1f
        imgMoonie.rotation = 0f
    }


    /**
     * Continúa exactamente desde
     * el punto donde estaba el jugador.
     */
    private fun reanudarPartida() {

        juegoPausado = false

        btnPause.isEnabled = true


        /*
         * Solo habilitamos las respuestas
         * si la pregunta aún no había sido
         * contestada.
         */
        if (!preguntaRespondida) {

            habilitarRespuestas()
        }
    }


    /**
     * Abandona la partida actual.
     *
     * IMPORTANTE:
     * No se abre Game1ResultActivity,
     * por lo que el récord NO se modifica.
     */
    private fun salirDePartida() {

        juegoPausado = false


        /*
         * Por ahora simplemente cerramos
         * Game1Activity.
         *
         * Cuando el mundo esté implementado,
         * esto permitirá regresar a la Activity
         * anterior o se sustituirá por la lógica
         * de última ubicación del jugador.
         */
        finish()
    }

    // ---------------------------------------------------------
    // RETROALIMENTACIÓN
    // ---------------------------------------------------------

    /**
     * Abre la ventana de retroalimentación
     * educativa después de responder.
     */
    private fun mostrarRetroalimentacion(
        mensaje: String,
        esCorrecta: Boolean
    ) {

        val dialog =
            Dialog(this)


        dialog.setContentView(
            R.layout.dialog_game1_feedback
        )


        /*
         * Evitamos que el jugador cierre
         * accidentalmente la ventana.
         */
        dialog.setCancelable(false)

        dialog.setCanceledOnTouchOutside(false)


        /*
         * Fondo transparente para conservar
         * las esquinas de la tarjeta.
         */
        dialog.window?.setBackgroundDrawable(
            ColorDrawable(Color.TRANSPARENT)
        )


        val txtFeedbackTitle =
            dialog.findViewById<TextView>(
                R.id.txtFeedbackTitle
            )


        val txtFeedbackMessage =
            dialog.findViewById<TextView>(
                R.id.txtFeedbackMessage
            )


        val imgFeedbackMoonie =
            dialog.findViewById<ImageView>(
                R.id.imgFeedbackMoonie
            )


        val btnFeedbackContinue =
            dialog.findViewById<MaterialButton>(
                R.id.btnFeedbackContinue
            )


        // -----------------------------------------------------
        // TÍTULO
        // -----------------------------------------------------

        if (esCorrecta) {

            txtFeedbackTitle.text =
                "¡Muy bien!"

        } else {

            txtFeedbackTitle.text =
                "¡Cuidado!"
        }


        // -----------------------------------------------------
        // MENSAJE EDUCATIVO
        // -----------------------------------------------------

        txtFeedbackMessage.text =
            mensaje


        // -----------------------------------------------------
        // ESTADO ACTUAL DE MOONIE
        // -----------------------------------------------------

        /*
         * La ventana muestra exactamente
         * el mismo nivel de reparación que
         * tiene Moonie en la partida.
         */
        imgFeedbackMoonie.setImageResource(
            obtenerImagenMoonie()
        )


        // -----------------------------------------------------
        // ANIMACIÓN EN EL DIÁLOGO
        // -----------------------------------------------------

        if (esCorrecta) {

            /*
             * Moonie aparece creciendo
             * suavemente.
             */
            imgFeedbackMoonie.scaleX = 0.85f
            imgFeedbackMoonie.scaleY = 0.85f


            imgFeedbackMoonie.animate()
                .scaleX(1f)
                .scaleY(1f)
                .setDuration(250)
                .start()

        } else {

            /*
             * En caso de error realiza
             * una pequeña sacudida.
             */
            imgFeedbackMoonie.animate()
                .rotation(-6f)
                .setDuration(100)
                .withEndAction {

                    imgFeedbackMoonie.animate()
                        .rotation(6f)
                        .setDuration(100)
                        .withEndAction {

                            imgFeedbackMoonie.animate()
                                .rotation(0f)
                                .setDuration(100)
                                .start()
                        }
                        .start()
                }
                .start()
        }


        // -----------------------------------------------------
        // CONTINUAR
        // -----------------------------------------------------

        btnFeedbackContinue.setOnClickListener {

            dialog.dismiss()

            siguientePregunta()
        }


        dialog.show()
    }


    // ---------------------------------------------------------
    // SIGUIENTE PREGUNTA
    // ---------------------------------------------------------

    /**
     * Avanza a la siguiente pregunta.
     */
    private fun siguientePregunta() {

        if (
            indicePreguntaActual
            < preguntasPartida.size - 1
        ) {

            indicePreguntaActual++

            mostrarPreguntaActual()

        } else {

            finalizarPartida()
        }
    }


    // ---------------------------------------------------------
    // FINALIZAR PARTIDA
    // ---------------------------------------------------------

    /**
     * Temporal.
     *
     * Posteriormente esta función abrirá
     * la pantalla completa de resultados.
     */
    private fun finalizarPartida() {

        Log.d(
            "Game1Activity",
            "Partida terminada con $puntaje puntos y $respuestasCorrectas respuestas correctas"
        )


        /*
         * Enviamos los resultados obtenidos
         * a la pantalla final.
         */
        val intent =
            Intent(
                this,
                Game1ResultActivity::class.java
            )


        intent.putExtra(
            Game1ResultActivity.EXTRA_SCORE,
            puntaje
        )


        intent.putExtra(
            Game1ResultActivity.EXTRA_CORRECT,
            respuestasCorrectas
        )


        intent.putExtra(
            Game1ResultActivity.EXTRA_TOTAL,
            preguntasPartida.size
        )


        startActivity(intent)


        /*
         * Cerramos esta partida para evitar que
         * el botón Atrás regrese a la pregunta 10.
         */
        finish()
    }

    // ---------------------------------------------------------
    // ESTADO DE LOS BOTONES
    // ---------------------------------------------------------

    /**
     * Evita que el jugador responda
     * nuevamente mientras ve el feedback.
     */
    private fun deshabilitarRespuestas() {

        btnAnswer1.isEnabled = false
        btnAnswer2.isEnabled = false
        btnAnswer3.isEnabled = false
    }


    /**
     * Habilita las respuestas para
     * la siguiente pregunta.
     */
    private fun habilitarRespuestas() {

        /*
         * Nunca habilitamos las respuestas
         * mientras el juego esté pausado.
         */
        if (juegoPausado) {
            return
        }


        btnAnswer1.isEnabled = true
        btnAnswer2.isEnabled = true
        btnAnswer3.isEnabled = true
    }
}