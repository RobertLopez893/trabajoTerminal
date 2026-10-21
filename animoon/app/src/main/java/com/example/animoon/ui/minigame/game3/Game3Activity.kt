package com.example.animoon.ui.minigame.game3

import android.app.Dialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.game3.data.Game3Repository
import com.example.animoon.ui.minigame.game3.model.Game3Conversacion
import com.example.animoon.ui.minigame.game3.model.Game3Mensaje
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class Game3Activity : BaseActivity() {

    companion object {
        private const val TAG = "Game3Activity"
        const val TOTAL_RONDAS = 5
        const val PUNTOS_POR_CASO = 20
        const val PUNTAJE_MAXIMO = TOTAL_RONDAS * PUNTOS_POR_CASO
        private const val PAUSA_ENTRE_MENSAJES_MS = 1100L
    }

    private val recursoMoonieFeliz = R.drawable.moonie_happy
    private val recursoMoonieAlerta = R.drawable.moonie_confused

    private lateinit var txtRound: TextView
    private lateinit var txtScore: TextView
    private lateinit var txtChatTitle: TextView
    private lateinit var btnPause: ImageButton
    private lateinit var scrollChat: ScrollView
    private lateinit var containerChat: LinearLayout
    private lateinit var cardFeliz: MaterialCardView
    private lateinit var cardAlerta: MaterialCardView
    private lateinit var imgFeliz: ImageView
    private lateinit var imgAlerta: ImageView

    private val repositorio by lazy { Game3Repository(applicationContext) }

    private var conversaciones: List<Game3Conversacion> = emptyList()
    private var indiceActual = 0
    private var puntaje = 0
    private var mensajesCompletos = false
    private var juegoPausado = false
    private var rondaBloqueada = false
    private var jobMensajes: Job? = null
    private var dialogoActual: Dialog? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game3)

        inicializarVistas()
        configurarBotones()
        configurarBotonAtras()
        actualizarHud()
        actualizarRespuestas()
        cargarPartida()
    }

    private fun inicializarVistas() {
        txtRound = findViewById(R.id.txtGame3Round)
        txtScore = findViewById(R.id.txtGame3Score)
        txtChatTitle = findViewById(R.id.txtGame3ChatTitle)
        btnPause = findViewById(R.id.btnGame3Pause)
        scrollChat = findViewById(R.id.scrollGame3Chat)
        containerChat = findViewById(R.id.containerGame3Chat)
        cardFeliz = findViewById(R.id.cardGame3Feliz)
        cardAlerta = findViewById(R.id.cardGame3Alerta)
        imgFeliz = findViewById(R.id.imgGame3Feliz)
        imgAlerta = findViewById(R.id.imgGame3Alerta)

        imgFeliz.setImageResource(recursoMoonieFeliz)
        imgAlerta.setImageResource(recursoMoonieAlerta)
    }

    private fun configurarBotones() {
        cardFeliz.setOnClickListener {
            responder(false)
        }

        cardAlerta.setOnClickListener {
            responder(true)
        }

        btnPause.setOnClickListener {
            mostrarDialogPausa()
        }
    }

    private fun configurarBotonAtras() {
        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    mostrarDialogPausa()
                }
            }
        )
    }

    private fun cargarPartida() {
        showLoading("Preparando los oídos de Moonie...")

        lifecycleScope.launch {
            val cargadas = try {
                repositorio.obtenerPartida(TOTAL_RONDAS)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "No se pudieron cargar las conversaciones", e)
                emptyList()
            } finally {
                hideLoading()
            }

            if (cargadas.isEmpty()) {
                Toast.makeText(
                    this@Game3Activity,
                    "No se pudieron cargar las conversaciones.",
                    Toast.LENGTH_LONG
                ).show()
                finish()
                return@launch
            }

            conversaciones = cargadas
            indiceActual = 0
            puntaje = 0
            mostrarRonda()
        }
    }

    private fun mostrarRonda() {
        val conversacion = conversaciones[indiceActual]

        rondaBloqueada = false
        mensajesCompletos = false
        actualizarRespuestas()

        containerChat.removeAllViews()
        txtChatTitle.text = "Chat con ${conversacion.contacto}"
        actualizarHud()

        jobMensajes?.cancel()
        jobMensajes = lifecycleScope.launch {
            for (mensaje in conversacion.mensajes) {
                while (juegoPausado) {
                    delay(100)
                }

                agregarBurbuja(mensaje)
                delay(PAUSA_ENTRE_MENSAJES_MS)
            }

            mensajesCompletos = true
            actualizarRespuestas()
        }
    }

    private fun agregarBurbuja(mensaje: Game3Mensaje) {
        val layout = if (mensaje.delJugador) {
            R.layout.item_game3_bubble_yo
        } else {
            R.layout.item_game3_bubble_otro
        }

        val burbuja = layoutInflater.inflate(layout, containerChat, false)
        burbuja.findViewById<TextView>(R.id.txtGame3Bubble).text = mensaje.texto
        burbuja.alpha = 0f

        containerChat.addView(burbuja)
        burbuja.animate().alpha(1f).setDuration(250).start()

        scrollChat.postDelayed({ scrollChat.fullScroll(View.FOCUS_DOWN) }, 60)
    }

    private fun actualizarRespuestas() {
        val activas = mensajesCompletos && !juegoPausado && !rondaBloqueada
        val alfa = if (activas) 1f else 0.55f

        cardFeliz.isEnabled = activas
        cardAlerta.isEnabled = activas
        cardFeliz.alpha = alfa
        cardAlerta.alpha = alfa
    }

    private fun responder(eligioAlerta: Boolean) {
        if (!mensajesCompletos || juegoPausado || rondaBloqueada) {
            return
        }

        rondaBloqueada = true
        actualizarRespuestas()

        val conversacion = conversaciones[indiceActual]
        val acerto = eligioAlerta == conversacion.hayRiesgo

        if (acerto) {
            puntaje += PUNTOS_POR_CASO
        }

        actualizarHud()
        mostrarFeedback(conversacion, acerto)
    }

    private fun mostrarFeedback(conversacion: Game3Conversacion, acerto: Boolean) {
        val dialog = Dialog(this)

        dialog.setContentView(R.layout.dialog_game3_feedback)
        dialog.setCancelable(false)
        dialog.setCanceledOnTouchOutside(false)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        val imgMoonie = dialog.findViewById<ImageView>(R.id.imgGame3FeedbackMoonie)
        val txtTitle = dialog.findViewById<TextView>(R.id.txtGame3FeedbackTitle)
        val txtScore = dialog.findViewById<TextView>(R.id.txtGame3FeedbackScore)
        val txtMessage = dialog.findViewById<TextView>(R.id.txtGame3FeedbackMessage)
        val btnContinue = dialog.findViewById<MaterialButton>(R.id.btnGame3FeedbackContinue)

        imgMoonie.setImageResource(
            if (conversacion.hayRiesgo) recursoMoonieAlerta else recursoMoonieFeliz
        )

        if (acerto) {
            txtTitle.text = "¡Muy bien!"
            txtScore.text = "+$PUNTOS_POR_CASO puntos"
            txtScore.setTextColor(getColor(R.color.animoon_success))
        } else {
            txtTitle.text = "¡Casi!"
            txtScore.text = "0 puntos"
            txtScore.setTextColor(getColor(R.color.animoon_error))
        }

        val reaccion = if (conversacion.hayRiesgo) {
            "Moonie debía ponerse en alerta."
        } else {
            "Moonie podía estar tranquilo."
        }

        txtMessage.text = "$reaccion\n\n${conversacion.retroalimentacion}"

        val esUltima = indiceActual >= conversaciones.lastIndex
        btnContinue.text = if (esUltima) "Ver resultados" else "Siguiente conversación"

        btnContinue.setOnClickListener {
            dialog.dismiss()
            dialogoActual = null

            if (esUltima) {
                finalizarPartida()
            } else {
                indiceActual++
                mostrarRonda()
            }
        }

        dialogoActual = dialog
        dialog.show()
        ajustarTamanoDialogo(dialog)
    }

    private fun mostrarDialogPausa() {
        if (juegoPausado || rondaBloqueada) {
            return
        }

        juegoPausado = true
        btnPause.isEnabled = false
        actualizarRespuestas()

        val dialog = Dialog(this)

        dialog.setContentView(R.layout.dialog_game3_pause)
        dialog.setCancelable(false)
        dialog.setCanceledOnTouchOutside(false)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        val btnContinue = dialog.findViewById<MaterialButton>(R.id.btnGame3PauseContinue)
        val btnExit = dialog.findViewById<MaterialButton>(R.id.btnGame3PauseExit)

        btnContinue.setOnClickListener {
            dialog.dismiss()
            dialogoActual = null

            juegoPausado = false
            btnPause.isEnabled = true
            actualizarRespuestas()
        }

        btnExit.setOnClickListener {
            dialog.dismiss()
            dialogoActual = null
            finish()
        }

        dialogoActual = dialog
        dialog.show()
        ajustarTamanoDialogo(dialog)
    }

    private fun finalizarPartida() {
        rondaBloqueada = true

        val intent = Intent(this, Game3ResultActivity::class.java)
        intent.putExtra(Game3ResultActivity.EXTRA_SCORE, puntaje)
        intent.putExtra(
            Game3ResultActivity.EXTRA_MAX_SCORE,
            conversaciones.size * PUNTOS_POR_CASO
        )

        startActivity(intent)
        finish()
    }

    private fun actualizarHud() {
        val total = if (conversaciones.isEmpty()) TOTAL_RONDAS else conversaciones.size

        txtRound.text = "Conversación ${indiceActual + 1} de $total"
        txtScore.text = "★ $puntaje / ${total * PUNTOS_POR_CASO}"
    }

    override fun onDestroy() {
        jobMensajes?.cancel()
        dialogoActual?.dismiss()
        dialogoActual = null
        super.onDestroy()
    }
}
