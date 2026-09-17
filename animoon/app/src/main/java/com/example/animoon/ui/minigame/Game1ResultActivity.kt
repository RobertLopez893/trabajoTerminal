package com.example.animoon.ui.minigame

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.MainActivity
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton

class Game1ResultActivity : BaseActivity() {

    // ---------------------------------------------------------
    // ELEMENTOS DE LA INTERFAZ
    // ---------------------------------------------------------

    private lateinit var imgResultMoonie: ImageView

    private lateinit var txtResultScore: TextView
    private lateinit var txtResultCorrect: TextView
    private lateinit var txtResultRecord: TextView
    private lateinit var txtResultMessage: TextView

    private lateinit var btnRetry: MaterialButton
    private lateinit var btnReturn: MaterialButton


    companion object {

        // Datos recibidos desde Game1Activity
        const val EXTRA_SCORE = "game1_score"
        const val EXTRA_CORRECT = "game1_correct"
        const val EXTRA_TOTAL = "game1_total"

        // SharedPreferences del minijuego 1
        private const val PREFS_GAME1 = "game1_preferences"

        // Clave donde se guarda el récord
        private const val KEY_RECORD = "game1_record"
    }


    // ---------------------------------------------------------
    // ON CREATE
    // ---------------------------------------------------------

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game1_result)

        inicializarVistas()

        cargarResultado()

        configurarBotones()
    }


    // ---------------------------------------------------------
    // INICIALIZACIÓN DE VISTAS
    // ---------------------------------------------------------

    private fun inicializarVistas() {

        imgResultMoonie =
            findViewById(R.id.imgResultMoonie)

        txtResultScore =
            findViewById(R.id.txtResultScore)

        txtResultCorrect =
            findViewById(R.id.txtResultCorrect)

        txtResultRecord =
            findViewById(R.id.txtResultRecord)

        txtResultMessage =
            findViewById(R.id.txtResultMessage)

        btnRetry =
            findViewById(R.id.btnRetry)

        btnReturn =
            findViewById(R.id.btnReturn)
    }


    // ---------------------------------------------------------
    // RESULTADO DE LA PARTIDA
    // ---------------------------------------------------------

    private fun cargarResultado() {

        // -----------------------------------------------------
        // RECIBIR DATOS
        // -----------------------------------------------------

        val puntaje =
            intent.getIntExtra(
                EXTRA_SCORE,
                0
            )

        val respuestasCorrectas =
            intent.getIntExtra(
                EXTRA_CORRECT,
                0
            )

        val totalPreguntas =
            intent.getIntExtra(
                EXTRA_TOTAL,
                10
            )


        // -----------------------------------------------------
        // RÉCORD PERSONAL
        // -----------------------------------------------------

        /*
         * Obtenemos las preferencias locales
         * correspondientes al minijuego 1.
         */
        val preferencias =
            getSharedPreferences(
                PREFS_GAME1,
                MODE_PRIVATE
            )


        /*
         * Recuperamos el récord anterior.
         *
         * Si nunca se ha jugado antes,
         * el valor inicial será 0.
         */
        val recordAnterior =
            preferencias.getInt(
                KEY_RECORD,
                0
            )


        /*
         * Comprobamos si el puntaje obtenido
         * supera al récord anterior.
         */
        val esNuevoRecord =
            puntaje > recordAnterior


        /*
         * Solo guardamos el puntaje si
         * realmente supera al récord existente.
         */
        if (esNuevoRecord) {

            preferencias.edit()
                .putInt(
                    KEY_RECORD,
                    puntaje
                )
                .apply()
        }


        /*
         * El récord actual será el nuevo puntaje
         * si se superó el anterior.
         *
         * De lo contrario conservamos
         * el récord ya almacenado.
         */
        val recordActual =
            if (esNuevoRecord) {

                puntaje

            } else {

                recordAnterior
            }


        // -----------------------------------------------------
        // MOSTRAR PUNTAJE
        // -----------------------------------------------------

        txtResultScore.text =
            "★ $puntaje puntos"


        // -----------------------------------------------------
        // MOSTRAR ACIERTOS
        // -----------------------------------------------------

        txtResultCorrect.text =
            "$respuestasCorrectas de $totalPreguntas aciertos"


        // -----------------------------------------------------
        // MOSTRAR RÉCORD
        // -----------------------------------------------------

        if (esNuevoRecord) {

            txtResultRecord.text =
                "🏆 ¡Nuevo récord! $recordActual puntos"

        } else {

            txtResultRecord.text =
                "🏆 Récord personal: $recordActual puntos"
        }


        // -----------------------------------------------------
        // ESTADO FINAL DE MOONIE
        // -----------------------------------------------------

        imgResultMoonie.setImageResource(
            obtenerImagenMoonie(
                respuestasCorrectas
            )
        )


        // -----------------------------------------------------
        // MENSAJE FINAL
        // -----------------------------------------------------

        txtResultMessage.text =
            obtenerMensajeResultado(
                respuestasCorrectas
            )


        // Animación de entrada
        animarMoonie()
    }


    // ---------------------------------------------------------
    // ESTADO DE MOONIE
    // ---------------------------------------------------------

    private fun obtenerImagenMoonie(
        respuestasCorrectas: Int
    ): Int {

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


    // ---------------------------------------------------------
    // MENSAJE FINAL
    // ---------------------------------------------------------

    private fun obtenerMensajeResultado(
        respuestasCorrectas: Int
    ): String {

        return when (respuestasCorrectas) {

            in 0..2 -> {

                "¡Cada intento nos ayuda a aprender! " +
                        "Vuelve a intentarlo y ayuda a Moonie a repararse."
            }

            in 3..4 -> {

                "¡Buen intento! Ya conoces algunas formas de protegerte. " +
                        "Sigue practicando junto a Moonie."
            }

            in 5..6 -> {

                "¡Buen trabajo! Moonie está mucho mejor. " +
                        "Sigue aprendiendo para navegar con seguridad."
            }

            in 7..8 -> {

                "¡Gran trabajo! Moonie está casi como nuevo. " +
                        "Tus decisiones ayudan a mantenerte seguro en Internet."
            }

            else -> {

                "¡Excelente! Moonie está como nuevo. " +
                        "Demostraste que sabes tomar decisiones seguras en Internet."
            }
        }
    }


    // ---------------------------------------------------------
    // ANIMACIÓN DE MOONIE
    // ---------------------------------------------------------

    private fun animarMoonie() {

        imgResultMoonie.scaleX = 0.80f
        imgResultMoonie.scaleY = 0.80f
        imgResultMoonie.alpha = 0f


        imgResultMoonie.animate()
            .scaleX(1f)
            .scaleY(1f)
            .alpha(1f)
            .setDuration(450)
            .start()
    }


    // ---------------------------------------------------------
    // BOTONES
    // ---------------------------------------------------------

    private fun configurarBotones() {

        // -----------------------------------------------------
        // REINTENTAR
        // -----------------------------------------------------

        btnRetry.setOnClickListener {

            /*
             * Iniciamos nuevamente Game1Activity.
             *
             * Game1Activity reiniciará:
             *
             * - puntaje
             * - respuestas correctas
             * - Moonie
             * - preguntas aleatorias
             */
            val intent =
                Intent(
                    this,
                    Game1Activity::class.java
                )

            startActivity(intent)

            /*
             * Cerramos esta pantalla de resultados
             * para no acumular Activities.
             */
            finish()
        }


        // -----------------------------------------------------
        // REGRESAR
        // -----------------------------------------------------

        btnReturn.setOnClickListener {

            /*
             * TEMPORAL.
             *
             * Más adelante este botón regresará
             * al jugador a la última ubicación
             * desde la cual entró al minijuego.
             *
             * Por ahora regresamos a MainActivity
             * mientras el sistema de zonas todavía
             * no está implementado.
             */
            val intent =
                Intent(
                    this,
                    MainActivity::class.java
                )


            intent.flags =
                Intent.FLAG_ACTIVITY_CLEAR_TOP or
                        Intent.FLAG_ACTIVITY_SINGLE_TOP


            startActivity(intent)

            finish()
        }
    }
}