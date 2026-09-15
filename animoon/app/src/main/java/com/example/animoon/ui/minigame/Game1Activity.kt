package com.example.animoon.ui.minigame

import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import com.example.animoon.ui.minigame.game1.data.PreguntasRepository
import com.example.animoon.ui.minigame.game1.model.Pregunta
import com.google.android.material.button.MaterialButton

class Game1Activity : AppCompatActivity() {

    // 10 preguntas utilizadas durante esta partida
    private lateinit var preguntasPartida: List<Pregunta>

    // Índice de la pregunta que se muestra actualmente
    private var indicePreguntaActual = 0

    // Evita que el jugador pueda responder varias veces
    private var preguntaRespondida = false

    // ELEMENTOS DEL XML PRINCIPAL
    private lateinit var txtProgress: TextView
    private lateinit var txtQuestion: TextView
    private lateinit var txtMoonieMessage: TextView

    private lateinit var btnAnswer1: MaterialButton
    private lateinit var btnAnswer2: MaterialButton
    private lateinit var btnAnswer3: MaterialButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_game1)

        inicializarVistas()
        configurarBotones()
        prepararPartida()
        mostrarPreguntaActual()
    }

    /**
     * Conecta las vistas de activity_game1.xml
     * con las variables de Kotlin.
     */
    private fun inicializarVistas() {

        txtProgress = findViewById(R.id.txtProgress)
        txtQuestion = findViewById(R.id.txtQuestion)
        txtMoonieMessage = findViewById(R.id.txtMoonieMessage)

        btnAnswer1 = findViewById(R.id.btnAnswer1)
        btnAnswer2 = findViewById(R.id.btnAnswer2)
        btnAnswer3 = findViewById(R.id.btnAnswer3)
    }

    /**
     * Define qué ocurre al tocar cada respuesta.
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
    }

    /**
     * Carga las preguntas desde el JSON
     * y selecciona 10 al azar.
     */
    private fun prepararPartida() {

        val repository = PreguntasRepository(this)

        val todasLasPreguntas = repository.cargarPreguntas()

        preguntasPartida = todasLasPreguntas
            .shuffled()
            .take(10)

        indicePreguntaActual = 0

        Log.d(
            "Game1Activity",
            "Preguntas cargadas: ${todasLasPreguntas.size}"
        )

        Log.d(
            "Game1Activity",
            "Preguntas seleccionadas: ${preguntasPartida.map { it.id }}"
        )
    }

    /**
     * Muestra la pregunta actual y sus tres respuestas.
     */
    private fun mostrarPreguntaActual() {

        val pregunta = preguntasPartida[indicePreguntaActual]

        preguntaRespondida = false

        txtProgress.text =
            "Pregunta ${indicePreguntaActual + 1} de ${preguntasPartida.size}"

        txtQuestion.text = pregunta.texto

        btnAnswer1.text = pregunta.opciones[0].texto
        btnAnswer2.text = pregunta.opciones[1].texto
        btnAnswer3.text = pregunta.opciones[2].texto

        txtMoonieMessage.text =
            "¡Piensa con cuidado y elige la opción más segura!"

        habilitarRespuestas()

        Log.d(
            "Game1Activity",
            "Mostrando pregunta ${pregunta.id}"
        )
    }

    /**
     * Procesa la respuesta seleccionada.
     */
    private fun seleccionarRespuesta(indiceOpcion: Int) {

        if (preguntaRespondida) {
            return
        }

        preguntaRespondida = true

        val pregunta = preguntasPartida[indicePreguntaActual]

        val opcionSeleccionada = pregunta.opciones[indiceOpcion]

        deshabilitarRespuestas()

        Log.d(
            "Game1Activity",
            "Respuesta seleccionada: ${opcionSeleccionada.texto}"
        )

        Log.d(
            "Game1Activity",
            "¿Respuesta correcta?: ${opcionSeleccionada.correcta}"
        )

        mostrarRetroalimentacion(
            mensaje = opcionSeleccionada.retroalimentacion,
            esCorrecta = opcionSeleccionada.correcta
        )
    }

    /**
     * Abre la ventana de retroalimentación.
     */
    private fun mostrarRetroalimentacion(
        mensaje: String,
        esCorrecta: Boolean
    ) {

        val dialog = Dialog(this)

        dialog.setContentView(R.layout.dialog_game1_feedback)

        // Evita cerrar el diálogo tocando fuera de él
        dialog.setCancelable(false)
        dialog.setCanceledOnTouchOutside(false)

        // Fondo transparente para conservar las esquinas de la tarjeta
        dialog.window?.setBackgroundDrawable(
            ColorDrawable(Color.TRANSPARENT)
        )

        val txtFeedbackTitle =
            dialog.findViewById<TextView>(R.id.txtFeedbackTitle)

        val txtFeedbackMessage =
            dialog.findViewById<TextView>(R.id.txtFeedbackMessage)

        val imgFeedbackMoonie =
            dialog.findViewById<ImageView>(R.id.imgFeedbackMoonie)

        val btnFeedbackContinue =
            dialog.findViewById<MaterialButton>(R.id.btnFeedbackContinue)

        // Título diferente según el resultado
        if (esCorrecta) {

            txtFeedbackTitle.text = "¡Muy bien!"

        } else {

            txtFeedbackTitle.text = "¡Cuidado!"
        }

        // Retroalimentación correspondiente a la opción seleccionada
        txtFeedbackMessage.text = mensaje

        // De momento utilizamos la imagen neutral
        imgFeedbackMoonie.setImageResource(
            R.drawable.moonie_neutral
        )

        btnFeedbackContinue.setOnClickListener {

            dialog.dismiss()

            siguientePregunta()
        }

        dialog.show()
    }

    /**
     * Avanza a la siguiente pregunta.
     */
    private fun siguientePregunta() {

        if (indicePreguntaActual < preguntasPartida.size - 1) {

            indicePreguntaActual++

            mostrarPreguntaActual()

        } else {

            finalizarPartida()
        }
    }

    /**
     * Temporal.
     *
     * Más adelante esta función abrirá
     * la pantalla de resultados.
     */
    private fun finalizarPartida() {

        Toast.makeText(
            this,
            "¡Terminaste las 10 preguntas!",
            Toast.LENGTH_LONG
        ).show()

        Log.d(
            "Game1Activity",
            "Partida terminada"
        )
    }

    private fun deshabilitarRespuestas() {

        btnAnswer1.isEnabled = false
        btnAnswer2.isEnabled = false
        btnAnswer3.isEnabled = false
    }

    private fun habilitarRespuestas() {

        btnAnswer1.isEnabled = true
        btnAnswer2.isEnabled = true
        btnAnswer3.isEnabled = true
    }
}