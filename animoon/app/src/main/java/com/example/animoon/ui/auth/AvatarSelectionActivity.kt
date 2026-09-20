package com.example.animoon.ui.auth

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import kotlinx.coroutines.launch

class AvatarSelectionActivity : AppCompatActivity() {

    // =========================================================
    // SELECCIÓN ACTUAL
    // =========================================================

    private var selectedSpecies: String? = null
    private var selectedColor: String? = null


    // =========================================================
    // OPCIONES DE ESPECIE
    // =========================================================

    private lateinit var btnRabbit: View
    private lateinit var btnCat: View
    private lateinit var btnDog: View
    private lateinit var btnFox: View


    // =========================================================
    // OPCIONES DE COLOR
    // =========================================================

    private lateinit var btnWhite: View
    private lateinit var btnBlue: View
    private lateinit var btnOrange: View
    private lateinit var btnGreen: View


    // =========================================================
    // BOTÓN FINAL
    // =========================================================

    private lateinit var btnContinue: Button


    // =========================================================
    // VISTA PREVIA
    // =========================================================

    private lateinit var imgAvatarPreview: ImageView
    private lateinit var txtAvatarPlaceholder: TextView

    private lateinit var txtPreviewSpecies: TextView
    private lateinit var txtPreviewColor: TextView


    // =========================================================
    // ON CREATE
    // =========================================================

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_avatar_selection)

        initViews()
        configureSpecies()
        configureColors()

        // Primero debe seleccionarse una especie.
        setColorButtonsEnabled(false)

        // El botón final comienza deshabilitado.
        btnContinue.isEnabled = false
        btnContinue.alpha = 0.45f

        btnContinue.setOnClickListener {
            saveAvatar()
        }
    }


    // =========================================================
    // INICIALIZACIÓN DE VISTAS
    // =========================================================

    private fun initViews() {

        // Especies
        btnRabbit = findViewById(R.id.btnRabbit)
        btnCat = findViewById(R.id.btnCat)
        btnDog = findViewById(R.id.btnDog)
        btnFox = findViewById(R.id.btnFox)

        // Colores
        btnWhite = findViewById(R.id.btnWhite)
        btnBlue = findViewById(R.id.btnBlue)
        btnOrange = findViewById(R.id.btnOrange)
        btnGreen = findViewById(R.id.btnGreen)

        // Botón final
        btnContinue = findViewById(R.id.btnContinue)

        // Vista previa
        imgAvatarPreview = findViewById(R.id.imgAvatarPreview)
        txtAvatarPlaceholder = findViewById(R.id.txtAvatarPlaceholder)

        txtPreviewSpecies = findViewById(R.id.txtPreviewSpecies)
        txtPreviewColor = findViewById(R.id.txtPreviewColor)
    }


    // =========================================================
    // CONFIGURAR ESPECIES
    // =========================================================

    private fun configureSpecies() {

        btnRabbit.setOnClickListener {
            selectSpecies("Conejo")
        }

        btnCat.setOnClickListener {
            selectSpecies("Gato")
        }

        btnDog.setOnClickListener {
            selectSpecies("Perro")
        }

        btnFox.setOnClickListener {
            selectSpecies("Zorro")
        }
    }


    // =========================================================
    // CONFIGURAR COLORES
    // =========================================================

    private fun configureColors() {

        btnWhite.setOnClickListener {
            selectColor("Blanco")
        }

        btnBlue.setOnClickListener {
            selectColor("Azul")
        }

        btnOrange.setOnClickListener {
            selectColor("Naranja")
        }

        btnGreen.setOnClickListener {
            selectColor("Verde")
        }
    }


    // =========================================================
    // SELECCIONAR ESPECIE
    // =========================================================

    private fun selectSpecies(species: String) {

        selectedSpecies = species

        /*
         * Siempre que se selecciona una especie,
         * la previsualización comienza con el traje blanco.
         *
         * El color todavía no queda confirmado hasta que
         * el usuario presione uno de los cuatro botones.
         */
        selectedColor = null

        txtPreviewSpecies.text =
            "Especie: $species"

        txtPreviewColor.text =
            "Traje: Elige un color"

        // Habilitar colores después de seleccionar especie.
        setColorButtonsEnabled(true)

        // Vista previa inicial blanca.
        updateAvatarPreview(
            species = species,
            color = "Blanco"
        )

        updateContinueButton()
    }


    // =========================================================
    // SELECCIONAR COLOR
    // =========================================================

    private fun selectColor(color: String) {

        val species =
            selectedSpecies ?: return

        selectedColor = color

        txtPreviewColor.text =
            "Traje: $color"

        updateAvatarPreview(
            species = species,
            color = color
        )

        updateContinueButton()
    }


    // =========================================================
    // ACTUALIZAR VISTA PREVIA
    // =========================================================

    private fun updateAvatarPreview(
        species: String,
        color: String
    ) {

        val drawableId =
            when (species to color) {

                // =================================================
                // CONEJO
                // =================================================

                "Conejo" to "Blanco" ->
                    R.drawable.avatar_rabbit_white

                "Conejo" to "Azul" ->
                    R.drawable.avatar_rabbit_blue

                "Conejo" to "Naranja" ->
                    R.drawable.avatar_rabbit_orange

                "Conejo" to "Verde" ->
                    R.drawable.avatar_rabbit_green


                // =================================================
                // GATO
                // =================================================

                "Gato" to "Blanco" ->
                    R.drawable.avatar_cat_white

                "Gato" to "Azul" ->
                    R.drawable.avatar_cat_blue

                "Gato" to "Naranja" ->
                    R.drawable.avatar_cat_orange

                "Gato" to "Verde" ->
                    R.drawable.avatar_cat_green


                // =================================================
                // PERRO
                // =================================================

                "Perro" to "Blanco" ->
                    R.drawable.avatar_dog_white

                "Perro" to "Azul" ->
                    R.drawable.avatar_dog_blue

                "Perro" to "Naranja" ->
                    R.drawable.avatar_dog_orange

                "Perro" to "Verde" ->
                    R.drawable.avatar_dog_green


                // =================================================
                // ZORRO
                // =================================================

                "Zorro" to "Blanco" ->
                    R.drawable.avatar_fox_white

                "Zorro" to "Azul" ->
                    R.drawable.avatar_fox_blue

                "Zorro" to "Naranja" ->
                    R.drawable.avatar_fox_orange

                "Zorro" to "Verde" ->
                    R.drawable.avatar_fox_green


                else ->
                    return
            }


        // Ocultar el signo "?"
        txtAvatarPlaceholder.visibility =
            View.GONE

        // Mostrar avatar
        imgAvatarPreview.visibility =
            View.VISIBLE

        // Cambiar imagen
        imgAvatarPreview.setImageResource(
            drawableId
        )

        // Accesibilidad
        imgAvatarPreview.contentDescription =
            "$species con traje $color"
    }


    // =========================================================
    // HABILITAR / DESHABILITAR COLORES
    // =========================================================

    private fun setColorButtonsEnabled(
        enabled: Boolean
    ) {

        btnWhite.isEnabled = enabled
        btnBlue.isEnabled = enabled
        btnOrange.isEnabled = enabled
        btnGreen.isEnabled = enabled


        val alphaValue =
            if (enabled) {
                1f
            } else {
                0.35f
            }


        btnWhite.alpha = alphaValue
        btnBlue.alpha = alphaValue
        btnOrange.alpha = alphaValue
        btnGreen.alpha = alphaValue
    }


    // =========================================================
    // ACTUALIZAR BOTÓN CONTINUAR
    // =========================================================

    private fun updateContinueButton() {

        val completed =
            selectedSpecies != null &&
                    selectedColor != null


        btnContinue.isEnabled =
            completed


        btnContinue.alpha =
            if (completed) {
                1f
            } else {
                0.45f
            }
    }


    // =========================================================
    // GUARDAR AVATAR Y FINALIZAR REGISTRO
    // =========================================================

    private fun saveAvatar() {

        val speciesStr =
            selectedSpecies?.lowercase()
                ?: return


        val colorStr =
            selectedColor
                ?: return


        // Datos recibidos de las pantallas anteriores.

        val phoneNumber =
            intent.getStringExtra(
                "PHONE_NUMBER"
            ) ?: ""


        val apelativo =
            intent.getStringExtra(
                "APELATIVO"
            ) ?: ""


        val password =
            intent.getStringExtra(
                "PASSWORD"
            ) ?: ""


        val verificationCode =
            intent.getStringExtra(
                "VERIFICATION_CODE"
            ) ?: ""


        // Evitar múltiples envíos.
        btnContinue.isEnabled = false


        lifecycleScope.launch {

            try {

                val req =
                    com.example.animoon.data.model.FinalRegisterRequest(

                        nickname = apelativo,

                        telefono = phoneNumber,

                        codigo_verificacion =
                            verificationCode,

                        password = password,

                        avatar_especie =
                            speciesStr,

                        avatar_color =
                            colorStr
                    )


                val res =
                    com.example.animoon.data.network
                        .ApiClient
                        .authService
                        .finalRegister(req)


                // =================================================
                // REGISTRO EXITOSO
                // =================================================

                if (res.isSuccessful) {

                    Toast.makeText(
                        this@AvatarSelectionActivity,
                        "Registro exitoso",
                        Toast.LENGTH_SHORT
                    ).show()


                    val intent =
                        android.content.Intent(
                            this@AvatarSelectionActivity,
                            com.example.animoon.ui.auth.LoginActivity::class.java
                        )

                    intent.flags =
                        android.content.Intent.FLAG_ACTIVITY_NEW_TASK or
                                android.content.Intent.FLAG_ACTIVITY_CLEAR_TASK

                    startActivity(intent)
                    finish()
                }


                // =================================================
                // ERROR DEL SERVIDOR
                // =================================================

                else {

                    Toast.makeText(
                        this@AvatarSelectionActivity,
                        "Error al completar el registro",
                        Toast.LENGTH_SHORT
                    ).show()


                    updateContinueButton()
                }
            }


            // =====================================================
            // ERROR DE CONEXIÓN
            // =====================================================

            catch (e: Exception) {

                Toast.makeText(
                    this@AvatarSelectionActivity,
                    "Error de conexión",
                    Toast.LENGTH_SHORT
                ).show()


                updateContinueButton()
            }
        }
    }
}