package com.example.animoon.ui.minigame.game3

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import android.widget.TextView
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.data.model.MinijuegoScoreRequest
import com.example.animoon.data.network.ApiClient
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.MinigamesActivity
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class Game3ResultActivity : BaseActivity() {

    companion object {
        private const val TAG = "Game3Result"
        const val EXTRA_SCORE = "game3_score"
        const val EXTRA_MAX_SCORE = "game3_max_score"
    }

    private lateinit var imgMoonie: ImageView
    private lateinit var txtScore: TextView
    private lateinit var txtMessage: TextView
    private lateinit var btnRetry: MaterialButton
    private lateinit var btnReturn: MaterialButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game3_result)

        inicializarVistas()

        val score = intent.getIntExtra(EXTRA_SCORE, 0)
        val maxScore = intent.getIntExtra(EXTRA_MAX_SCORE, Game3Activity.PUNTAJE_MAXIMO)

        mostrarResultado(score, maxScore)
        configurarBotones()

        if (savedInstanceState == null) {
            guardarPuntaje(score)
        }
    }

    private fun inicializarVistas() {
        imgMoonie = findViewById(R.id.imgGame3ResultMoonie)
        txtScore = findViewById(R.id.txtGame3ResultScore)
        txtMessage = findViewById(R.id.txtGame3ResultMessage)
        btnRetry = findViewById(R.id.btnGame3Retry)
        btnReturn = findViewById(R.id.btnGame3Return)
    }

    private fun mostrarResultado(score: Int, maxScore: Int) {
        txtScore.text = "★ $score / $maxScore"

        val porcentaje = if (maxScore > 0) {
            score.toDouble() / maxScore * 100.0
        } else {
            0.0
        }

        imgMoonie.setImageResource(
            if (porcentaje >= 70.0) R.drawable.moonie_happy else R.drawable.moonie_neutral
        )

        txtMessage.text = when {
            porcentaje >= 90.0 ->
                "¡Excelente! Moonie ya escucha muy bien y sabe cuándo ponerse en alerta. Recuerda avisar siempre a un adulto de confianza."

            porcentaje >= 70.0 ->
                "¡Muy buen trabajo! Reconociste casi todas las señales. Si algo en un chat te incomoda, cuéntaselo a un adulto de confianza."

            porcentaje >= 50.0 ->
                "¡Buen esfuerzo! Ya conoces varias señales de alerta. Vuelve a jugar para que Moonie escuche todavía mejor."

            else ->
                "Moonie todavía necesita ayuda con sus oídos. Inténtalo otra vez y fíjate bien en lo que te piden en el chat."
        }
    }

    private fun configurarBotones() {
        btnRetry.setOnClickListener {
            startActivity(Intent(this, Game3Activity::class.java))
            finish()
        }

        btnReturn.setOnClickListener {
            val menuIntent = Intent(this, MinigamesActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            }

            startActivity(menuIntent)
            finish()
        }
    }

    private fun guardarPuntaje(score: Int) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val req = MinijuegoScoreRequest(
                    minijuego_id = "minijuego_3",
                    puntaje = score,
                    nivel_max_alcanzado = 1
                )

                val response = ApiClient.minigameService.guardarPuntaje(req)

                if (response.isSuccessful) {
                    Log.d(TAG, "Puntaje guardado: ${response.body()?.message}")
                } else {
                    Log.e(TAG, "Error al guardar: ${response.errorBody()?.string()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Excepción al guardar", e)
            }
        }
    }
}
