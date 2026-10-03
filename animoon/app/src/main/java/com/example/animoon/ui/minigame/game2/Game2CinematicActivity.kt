package com.example.animoon.ui.minigame.game2

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton


class Game2CinematicActivity : BaseActivity() {


    private data class Escena(

        val drawableName: String,

        val texto: String
    )


    private val escenas =
        listOf(

            Escena(

                drawableName =
                    "game2_cinematic_01",

                texto =
                    "Después del gran golpe, Moonie descubre que varios cables de sus sistemas de comunicación se desconectaron."
            ),

            Escena(

                drawableName =
                    "game2_cinematic_02",

                texto =
                    "Por esos cables viajan distintos tipos de mensajes. Algunos contienen información que debemos proteger."
            ),

            Escena(

                drawableName =
                    "game2_cinematic_03",

                texto =
                    "Los mensajes pueden dirigirse a padres o tutores, profesores y, en algunos casos, a ANIMOON."
            ),

            Escena(

                drawableName =
                    "game2_cinematic_04",

                texto =
                    "Pero recuerda: no toda la información debe compartirse con todos. Los datos personales y escolares necesitan más cuidado."
            ),

            Escena(

                drawableName =
                    "game2_cinematic_05",

                texto =
                    "Ayuda a Moonie a conectar cada mensaje con los lugares correctos y aprende a compartir información de forma segura."
            )
        )


    private lateinit var imgCinematic:
            ImageView


    private lateinit var txtStory:
            TextView


    private lateinit var txtScene:
            TextView


    private lateinit var btnNext:
            MaterialButton


    private lateinit var btnSkip:
            MaterialButton


    private var escenaActual =
        0


    override fun onCreate(
        savedInstanceState: Bundle?
    ) {

        super.onCreate(
            savedInstanceState
        )


        setContentView(
            R.layout.activity_game2_cinematic
        )


        inicializarVistas()

        configurarBotones()

        mostrarEscena()
    }


    private fun inicializarVistas() {


        imgCinematic =
            findViewById(
                R.id.imgGame2Cinematic
            )


        txtStory =
            findViewById(
                R.id.txtGame2Story
            )


        txtScene =
            findViewById(
                R.id.txtGame2SceneIndicator
            )


        btnNext =
            findViewById(
                R.id.btnGame2CinematicNext
            )


        btnSkip =
            findViewById(
                R.id.btnGame2CinematicSkip
            )
    }


    private fun configurarBotones() {


        btnNext.setOnClickListener {


            if (
                escenaActual <
                escenas.lastIndex
            ) {

                escenaActual++


                mostrarEscena()

            } else {

                iniciarJuego()
            }
        }


        btnSkip.setOnClickListener {

            iniciarJuego()
        }
    }


    private fun mostrarEscena() {


        val escena =
            escenas[
                escenaActual
            ]


        txtStory.text =
            escena.texto


        txtScene.text =
            "${escenaActual + 1} / ${escenas.size}"


        btnNext.text =

            if (
                escenaActual ==
                escenas.lastIndex
            ) {

                "Comenzar"

            } else {

                "Siguiente"
            }


        cargarImagenOpcional(
            escena.drawableName
        )


        /*
         * Animación sencilla de entrada.
         */
        imgCinematic.alpha =
            0f


        imgCinematic
            .animate()
            .alpha(1f)
            .setDuration(300)
            .start()


        txtStory.alpha =
            0f


        txtStory
            .animate()
            .alpha(1f)
            .setDuration(300)
            .start()
    }


    private fun cargarImagenOpcional(
        drawableName: String
    ) {


        val drawableId =
            resources.getIdentifier(

                drawableName,

                "drawable",

                packageName
            )


        if (
            drawableId != 0
        ) {


            imgCinematic.visibility =
                View.VISIBLE


            imgCinematic.setImageResource(
                drawableId
            )


        } else {


            /*
             * La cinemática continúa funcionando aunque
             * todavía no hayas generado la ilustración.
             */
            imgCinematic.setImageDrawable(
                null
            )


            imgCinematic.setBackgroundColor(
                0xFFDDE5FF.toInt()
            )
        }
    }


    private fun iniciarJuego() {


        val intent =
            Intent(

                this,

                Game2Activity::class.java
            )


        startActivity(
            intent
        )


        /*
         * Así al terminar Game2Activity no regresamos
         * accidentalmente a la cinemática.
         */
        finish()
    }
}