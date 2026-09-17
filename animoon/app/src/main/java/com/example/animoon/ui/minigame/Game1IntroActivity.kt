package com.example.animoon.ui.minigame

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton

class Game1IntroActivity : BaseActivity() {

    // ---------------------------------------------------------
    // ELEMENTOS DE LA INTERFAZ
    // ---------------------------------------------------------

    private lateinit var imgIntroMoonie: ImageView

    private lateinit var txtIntroProgress: TextView
    private lateinit var txtIntroTitle: TextView
    private lateinit var txtIntroMessage: TextView

    private lateinit var btnIntroBack: MaterialButton
    private lateinit var btnIntroNext: MaterialButton


    // ---------------------------------------------------------
    // ESTADO DE LA INTRODUCCIÓN
    // ---------------------------------------------------------

    private var escenaActual = 0


    /*
     * Cada escena contiene:
     *
     * - título
     * - mensaje
     * - imagen de Moonie
     */
    private val escenas by lazy {

        listOf(

            EscenaIntro(
                titulo = "¡Oh no!",
                mensaje =
                    "¡Hola! Soy Moonie. Algo salió mal con mi sistema de seguridad " +
                            "y necesito tu ayuda para volver a funcionar correctamente.",
                imagen = R.drawable.moonie_very_damaged
            ),

            EscenaIntro(
                titulo = "¿Me ayudas?",
                mensaje =
                    "Te mostraré diferentes situaciones que pueden ocurrir mientras " +
                            "usas Internet. Piensa con cuidado y elige siempre la opción más segura.",
                imagen = R.drawable.moonie_very_damaged
            ),

            EscenaIntro(
                titulo = "¡Reparemos mi sistema!",
                mensaje =
                    "Cada respuesta correcta me ayudará a recuperarme. " +
                            "Después de cada elección te explicaré cómo puedes protegerte mejor. " +
                            "¡Vamos a comenzar!",
                imagen = R.drawable.moonie_very_damaged
            )
        )
    }


    // ---------------------------------------------------------
    // ON CREATE
    // ---------------------------------------------------------

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_game1_intro)

        inicializarVistas()

        configurarBotones()

        mostrarEscena()
    }


    // ---------------------------------------------------------
    // INICIALIZACIÓN
    // ---------------------------------------------------------

    private fun inicializarVistas() {

        imgIntroMoonie =
            findViewById(R.id.imgIntroMoonie)

        txtIntroProgress =
            findViewById(R.id.txtIntroProgress)

        txtIntroTitle =
            findViewById(R.id.txtIntroTitle)

        txtIntroMessage =
            findViewById(R.id.txtIntroMessage)

        btnIntroBack =
            findViewById(R.id.btnIntroBack)

        btnIntroNext =
            findViewById(R.id.btnIntroNext)
    }


    // ---------------------------------------------------------
    // BOTONES
    // ---------------------------------------------------------

    private fun configurarBotones() {

        /*
         * Regresar a la escena anterior.
         */
        btnIntroBack.setOnClickListener {

            if (escenaActual > 0) {

                escenaActual--

                mostrarEscena(
                    animarDesdeIzquierda = true
                )
            }
        }


        /*
         * Avanzar a la siguiente escena.
         *
         * Si estamos en la última,
         * comienza el minijuego.
         */
        btnIntroNext.setOnClickListener {

            if (escenaActual < escenas.size - 1) {

                escenaActual++

                mostrarEscena(
                    animarDesdeIzquierda = false
                )

            } else {

                comenzarMinijuego()
            }
        }
    }


    // ---------------------------------------------------------
    // MOSTRAR ESCENA
    // ---------------------------------------------------------

    private fun mostrarEscena(
        animarDesdeIzquierda: Boolean = false
    ) {

        val escena =
            escenas[escenaActual]


        // -----------------------------------------------------
        // CONTENIDO
        // -----------------------------------------------------

        txtIntroProgress.text =
            "${escenaActual + 1} de ${escenas.size}"


        txtIntroTitle.text =
            escena.titulo


        txtIntroMessage.text =
            escena.mensaje


        imgIntroMoonie.setImageResource(
            escena.imagen
        )


        // -----------------------------------------------------
        // BOTÓN ATRÁS
        // -----------------------------------------------------

        if (escenaActual == 0) {

            /*
             * Lo ocultamos en la primera escena.
             *
             * INVISIBLE conserva su espacio
             * para no mover el otro botón.
             */
            btnIntroBack.visibility =
                View.INVISIBLE

        } else {

            btnIntroBack.visibility =
                View.VISIBLE
        }


        // -----------------------------------------------------
        // TEXTO DEL BOTÓN PRINCIPAL
        // -----------------------------------------------------

        if (escenaActual == escenas.size - 1) {

            btnIntroNext.text =
                "¡Comenzar!"

        } else {

            btnIntroNext.text =
                "Siguiente"
        }


        // -----------------------------------------------------
        // ANIMACIÓN
        // -----------------------------------------------------

        animarEscena(
            animarDesdeIzquierda
        )
    }


    // ---------------------------------------------------------
    // ANIMACIÓN ENTRE ESCENAS
    // ---------------------------------------------------------

    private fun animarEscena(
        desdeIzquierda: Boolean
    ) {

        /*
         * Dirección de entrada.
         */
        val desplazamiento =
            if (desdeIzquierda) {
                -80f
            } else {
                80f
            }


        // -----------------------------------------------------
        // MOONIE
        // -----------------------------------------------------

        imgIntroMoonie.animate().cancel()

        imgIntroMoonie.alpha = 0f
        imgIntroMoonie.translationX =
            desplazamiento
        imgIntroMoonie.scaleX = 0.95f
        imgIntroMoonie.scaleY = 0.95f


        imgIntroMoonie.animate()
            .alpha(1f)
            .translationX(0f)
            .scaleX(1f)
            .scaleY(1f)
            .setDuration(350)
            .start()


        // -----------------------------------------------------
        // TÍTULO
        // -----------------------------------------------------

        txtIntroTitle.animate().cancel()

        txtIntroTitle.alpha = 0f
        txtIntroTitle.translationY = 20f


        txtIntroTitle.animate()
            .alpha(1f)
            .translationY(0f)
            .setDuration(300)
            .start()


        // -----------------------------------------------------
        // MENSAJE
        // -----------------------------------------------------

        txtIntroMessage.animate().cancel()

        txtIntroMessage.alpha = 0f
        txtIntroMessage.translationY = 20f


        txtIntroMessage.animate()
            .alpha(1f)
            .translationY(0f)
            .setStartDelay(80)
            .setDuration(300)
            .start()
    }


    // ---------------------------------------------------------
    // COMENZAR JUEGO
    // ---------------------------------------------------------

    private fun comenzarMinijuego() {

        val intent =
            Intent(
                this,
                Game1Activity::class.java
            )

        startActivity(intent)


        /*
         * Cerramos la introducción.
         *
         * De esta manera el jugador no puede
         * regresar accidentalmente a la intro
         * usando el botón Atrás.
         */
        finish()
    }


    // ---------------------------------------------------------
    // MODELO DE UNA ESCENA
    // ---------------------------------------------------------

    private data class EscenaIntro(

        val titulo: String,

        val mensaje: String,

        val imagen: Int
    )
}