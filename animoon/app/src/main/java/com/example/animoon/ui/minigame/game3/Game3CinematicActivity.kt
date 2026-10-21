package com.example.animoon.ui.minigame.game3

import android.content.Intent
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton

class Game3CinematicActivity : BaseActivity() {

    private data class Escena(
        val drawableName: String,
        val texto: String
    )

    private val escenas = listOf(
        Escena(
            drawableName = "game3_cinematic_01",
            texto = "Moonie sigue reparándose, pero ahora le fallan los sensores con los que escucha."
        ),
        Escena(
            drawableName = "game3_cinematic_02",
            texto = "Con ellos, Moonie lee los mensajes del chat de ANIMOON para saber si todos están seguros."
        ),
        Escena(
            drawableName = "game3_cinematic_03",
            texto = "Algunas conversaciones son amistosas y tranquilas. Otras tienen señales de que algo no está bien."
        ),
        Escena(
            drawableName = "game3_cinematic_04",
            texto = "Cuando alguien te pide secretos, fotos o datos personales, Moonie debe ponerse en alerta."
        ),
        Escena(
            drawableName = "game3_cinematic_05",
            texto = "Lee cada conversación y elige cómo debe reaccionar Moonie: tranquilo o en alerta."
        )
    )

    private lateinit var imgCinematic: ImageView
    private lateinit var txtStory: TextView
    private lateinit var txtScene: TextView
    private lateinit var btnNext: MaterialButton
    private lateinit var btnSkip: MaterialButton

    private var escenaActual = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game3_cinematic)

        inicializarVistas()
        configurarBotones()
        mostrarEscena()
    }

    private fun inicializarVistas() {
        imgCinematic = findViewById(R.id.imgGame3Cinematic)
        txtStory = findViewById(R.id.txtGame3Story)
        txtScene = findViewById(R.id.txtGame3SceneIndicator)
        btnNext = findViewById(R.id.btnGame3CinematicNext)
        btnSkip = findViewById(R.id.btnGame3CinematicSkip)
    }

    private fun configurarBotones() {
        btnNext.setOnClickListener {
            if (escenaActual < escenas.lastIndex) {
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
        val escena = escenas[escenaActual]

        txtStory.text = escena.texto
        txtScene.text = "${escenaActual + 1} / ${escenas.size}"
        btnNext.text = if (escenaActual == escenas.lastIndex) "Comenzar" else "Siguiente"

        cargarImagen(escena.drawableName)

        imgCinematic.alpha = 0f
        imgCinematic.animate().alpha(1f).setDuration(300).start()

        txtStory.alpha = 0f
        txtStory.animate().alpha(1f).setDuration(300).start()
    }

    private fun cargarImagen(drawableName: String) {
        val drawableId = resources.getIdentifier(drawableName, "drawable", packageName)

        if (drawableId != 0) {
            imgCinematic.setImageResource(drawableId)
        } else {
            imgCinematic.setImageResource(R.drawable.game2_bg_base_principal)
        }
    }

    private fun iniciarJuego() {
        startActivity(Intent(this, Game3Activity::class.java))
        finish()
    }
}
