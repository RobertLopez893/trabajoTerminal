package com.example.animoon.ui.auth

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R

class AvatarSelectionActivity : AppCompatActivity() {

    private var selectedSpecies: String? = null
    private var selectedColor: String? = null

    private lateinit var btnRabbit: Button
    private lateinit var btnCat: Button
    private lateinit var btnDog: Button
    private lateinit var btnFox: Button

    private lateinit var btnWhite: Button
    private lateinit var btnBlue: Button
    private lateinit var btnOrange: Button

    private lateinit var btnContinue: Button

    private lateinit var txtPreviewSpecies: TextView
    private lateinit var txtPreviewColor: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_avatar_selection)

        initViews()
        configureSpecies()
        configureColors()

        btnContinue.isEnabled = false
        btnContinue.alpha = 0.45f

        btnContinue.setOnClickListener {
            saveAvatar()
        }
    }

    private fun initViews() {

        btnRabbit = findViewById(R.id.btnRabbit)
        btnCat = findViewById(R.id.btnCat)
        btnDog = findViewById(R.id.btnDog)
        btnFox = findViewById(R.id.btnFox)

        btnWhite = findViewById(R.id.btnWhite)
        btnBlue = findViewById(R.id.btnBlue)
        btnOrange = findViewById(R.id.btnOrange)

        btnContinue = findViewById(R.id.btnContinue)

        txtPreviewSpecies =
            findViewById(R.id.txtPreviewSpecies)

        txtPreviewColor =
            findViewById(R.id.txtPreviewColor)
    }

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
    }

    private fun selectSpecies(species: String) {

        selectedSpecies = species

        txtPreviewSpecies.text =
            "Especie: $species"

        updateContinueButton()
    }

    private fun selectColor(color: String) {

        selectedColor = color

        txtPreviewColor.text =
            "Traje: $color"

        updateContinueButton()
    }

    private fun updateContinueButton() {

        val completed =
            selectedSpecies != null &&
                    selectedColor != null

        btnContinue.isEnabled = completed

        btnContinue.alpha =
            if (completed) 1f
            else 0.45f
    }

    private fun saveAvatar() {

        /*
         *
         * Aquí se mandará al backend:
         *
         * especie
         * color
         * id del perfil
         */

        Toast.makeText(
            this,
            "Avatar: $selectedSpecies - $selectedColor",
            Toast.LENGTH_SHORT
        ).show()

        /*
         * Después:
         *
         * startActivity(
         *     Intent(this, MainActivity::class.java)
         * )
         */
    }
}