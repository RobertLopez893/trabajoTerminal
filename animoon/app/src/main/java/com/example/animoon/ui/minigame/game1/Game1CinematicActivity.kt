package com.example.animoon.ui.minigame.game1

import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity

class Game1CinematicActivity : BaseActivity() {

    private lateinit var cinematicRoot: FrameLayout
    private lateinit var ivCinematic: ImageView
    private lateinit var storyContainer: LinearLayout

    private lateinit var tvSceneTitle: TextView
    private lateinit var tvStory: TextView

    private lateinit var sceneIndicators: LinearLayout

    private lateinit var btnNext: Button
    private lateinit var btnSkip: TextView

    private var currentScene = 0

    private var isChangingScene = false

    private val images = listOf(
        R.drawable.game1_cinematic_01_moonie_helping,
        R.drawable.game1_cinematic_02_emergency,
        R.drawable.game1_cinematic_03_moonie_running,
        R.drawable.game1_cinematic_04_accident,
        R.drawable.game1_cinematic_05_moonie_damaged
    )

    private val titles = listOf(
        "Moonie1409",
        "¡Una emergencia!",
        "¡Moonie va al rescate!",
        "¡Cuidado, Moonie!",
        "¡Moonie necesita tu ayuda!"
    )

    private val texts = listOf(

        "Moonie es la consejera principal de Animoon. Siempre está lista para ayudar " +
                "cuando algún animalito necesita orientación, ayuda técnica o alguien con quien hablar.",

        "Un día ocurrió un problema en el tablero principal de la zona de escaneo lunar. " +
                "Los animalitos acudieron rápidamente con Moonie para pedirle ayuda.",

        "Moonie se preocupó mucho por la emergencia y salió rápidamente para ayudar a resolver el problema.",

        "Pero iba tan rápido que no alcanzó a ver una de las columnas del Centro de Comando... " +
                "¡y terminó chocando contra ella!",

        "El equipo logró solucionar la emergencia, pero Moonie quedó fuera de servicio. " +
                "Ahora tú formarás parte de su equipo de entrenamiento y la ayudarás a recuperar " +
                "sus conocimientos de seguridad digital."
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game1_cinematic)

        cinematicRoot = findViewById(R.id.cinematicRoot)

        ivCinematic = findViewById(R.id.ivCinematic)

        storyContainer = findViewById(R.id.storyContainer)

        tvSceneTitle = findViewById(R.id.tvSceneTitle)

        tvStory = findViewById(R.id.tvStory)

        sceneIndicators = findViewById(R.id.sceneIndicators)

        btnNext = findViewById(R.id.btnNext)

        btnSkip = findViewById(R.id.btnSkip)

        createIndicators()

        showScene()

        btnNext.setOnClickListener {
            advanceScene()
        }

        btnSkip.setOnClickListener {
            startGame()
        }

        /*
         * Permite avanzar tocando la pantalla.
         */
        cinematicRoot.setOnClickListener {
            advanceScene()
        }
    }

    /*
     * Decide si avanzamos de escena
     * o iniciamos el minijuego.
     */
    private fun advanceScene() {

        if (isChangingScene) {
            return
        }

        if (currentScene < images.size - 1) {

            currentScene++

            changeScene()

        } else {

            startGame()
        }
    }

    /*
     * Muestra la información correspondiente
     * a la escena actual.
     */
    private fun showScene() {

        ivCinematic.setImageResource(
            images[currentScene]
        )

        tvSceneTitle.text =
            titles[currentScene]

        tvStory.text =
            texts[currentScene]

        updateIndicators()

        if (currentScene == images.size - 1) {

            btnNext.text =
                "COMENZAR"

        } else {

            btnNext.text =
                "SIGUIENTE"
        }
    }

    /*
     * Transición entre escenas.
     */
    private fun changeScene() {

        isChangingScene = true

        ivCinematic.animate()
            .alpha(0f)
            .setDuration(200)
            .start()

        storyContainer.animate()
            .alpha(0f)
            .setDuration(180)
            .withEndAction {

                showScene()

                ivCinematic.alpha = 0f
                storyContainer.alpha = 0f

                ivCinematic.animate()
                    .alpha(1f)
                    .setDuration(350)
                    .start()

                storyContainer.animate()
                    .alpha(1f)
                    .translationY(0f)
                    .setDuration(350)
                    .withEndAction {

                        isChangingScene = false
                    }
                    .start()
            }
            .start()
    }

    /*
     * Crea los 5 puntos de progreso.
     */
    private fun createIndicators() {

        sceneIndicators.removeAllViews()

        repeat(images.size) {

            val indicator = View(this)

            val size = dpToPx(13)

            val margin = dpToPx(6)

            val params = LinearLayout.LayoutParams(
                size,
                size
            )

            params.marginEnd = margin

            indicator.layoutParams = params

            sceneIndicators.addView(indicator)
        }
    }

    /*
     * Actualiza visualmente qué escena
     * está seleccionada.
     */
    private fun updateIndicators() {

        for (i in 0 until sceneIndicators.childCount) {

            val dot = sceneIndicators.getChildAt(i)

            val background = GradientDrawable()

            background.shape =
                GradientDrawable.OVAL

            if (i == currentScene) {

                background.setColor(
                    Color.parseColor("#FFE56B")
                )

                dot.scaleX = 1.25f
                dot.scaleY = 1.25f

            } else {

                background.setColor(
                    Color.parseColor("#80FFFFFF")
                )

                dot.scaleX = 1f
                dot.scaleY = 1f
            }

            dot.background = background
        }
    }

    /*
     * Conversión de dp a pixeles.
     */
    private fun dpToPx(dp: Int): Int {

        return (
                dp * resources.displayMetrics.density
                ).toInt()
    }

    /*
     * Inicia realmente el minijuego.
     */
    private fun startGame() {

        val intent = Intent(
            this,
            Game1Activity::class.java
        )

        startActivity(intent)

        finish()
    }
}