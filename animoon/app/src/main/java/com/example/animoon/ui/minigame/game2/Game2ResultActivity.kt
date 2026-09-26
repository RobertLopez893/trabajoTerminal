package com.example.animoon.ui.minigame.game2

import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton


class Game2ResultActivity : BaseActivity() {


    companion object {

        const val EXTRA_SCORE =
            "game2_score"


        const val EXTRA_MAX_SCORE =
            "game2_max_score"
    }


    private lateinit var txtScore:
            TextView


    private lateinit var txtMessage:
            TextView


    private lateinit var btnRetry:
            MaterialButton


    private lateinit var btnReturn:
            MaterialButton


    override fun onCreate(
        savedInstanceState: Bundle?
    ) {

        super.onCreate(
            savedInstanceState
        )


        setContentView(
            R.layout.activity_game2_result
        )


        inicializarVistas()


        val score =
            intent.getIntExtra(
                EXTRA_SCORE,
                0
            )


        val maxScore = intent.getIntExtra(
            EXTRA_MAX_SCORE,
            Game2Activity.PUNTAJE_MAXIMO
        )


        mostrarResultado(

            score,

            maxScore
        )


        configurarBotones()
    }


    private fun inicializarVistas() {


        txtScore =
            findViewById(
                R.id.txtGame2ResultScore
            )


        txtMessage =
            findViewById(
                R.id.txtGame2ResultMessage
            )


        btnRetry =
            findViewById(
                R.id.btnGame2Retry
            )


        btnReturn =
            findViewById(
                R.id.btnGame2Return
            )
    }


    private fun mostrarResultado(
        score: Int,
        maxScore: Int
    ) {
        txtScore.text = "★ $score / $maxScore"

        val porcentaje = if (maxScore > 0) {
            score.toDouble() / maxScore * 100.0
        } else {
            0.0
        }

        txtMessage.text = when {
            porcentaje >= 90.0 ->
                "¡Excelente! Moonie recuperó sus comunicaciones y demostraste que sabes proteger muy bien tu información."

            porcentaje >= 70.0 ->
                "¡Muy buen trabajo! Moonie está funcionando mucho mejor. Recuerda pensar antes de compartir información."

            porcentaje >= 50.0 ->
                "¡Buen esfuerzo! Ya conoces varias reglas importantes. Sigue practicando para proteger mejor tus datos."

            else ->
                "Moonie todavía necesita un poco de ayuda. Inténtalo nuevamente y revisa con cuidado qué información puede compartirse."
        }
    }


    private fun configurarBotones() {


        btnRetry.setOnClickListener {


            val intent =
                Intent(

                    this,

                    Game2Activity::class.java
                )


            startActivity(
                intent
            )


            finish()
        }


        btnReturn.setOnClickListener {


            /*
             * No enviamos al jugador a MainActivity
             * de forma fija.
             *
             * finish() devuelve al lugar desde donde
             * entró al flujo.
             */
            finish()
        }
    }
}