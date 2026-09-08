package com.example.animoon.ui.auth

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

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

        val speciesStr = selectedSpecies?.lowercase() ?: return
        val colorStr = selectedColor ?: return

        val phoneNumber = intent.getStringExtra("PHONE_NUMBER") ?: ""
        val apelativo = intent.getStringExtra("APELATIVO") ?: ""
        val password = intent.getStringExtra("PASSWORD") ?: ""
        val verificationCode = intent.getStringExtra("VERIFICATION_CODE") ?: ""

        btnContinue.isEnabled = false
        
        lifecycleScope.launch {
            try {
                val req = com.example.animoon.data.model.FinalRegisterRequest(
                    nickname = apelativo,
                    telefono = phoneNumber,
                    codigo_verificacion = verificationCode,
                    password = password,
                    avatar_especie = speciesStr,
                    avatar_color = colorStr
                )
                
                val res = com.example.animoon.data.network.ApiClient.authService.finalRegister(req)
                
                if (res.isSuccessful) {
                    Toast.makeText(this@AvatarSelectionActivity, "Registro Exitoso", Toast.LENGTH_SHORT).show()
                    val intent = android.content.Intent(
                        this@AvatarSelectionActivity,
                        com.example.animoon.MainActivity::class.java
                    )
                    // Limpiar el backstack
                    intent.flags = android.content.Intent.FLAG_ACTIVITY_NEW_TASK or android.content.Intent.FLAG_ACTIVITY_CLEAR_TASK
                    startActivity(intent)
                    finish()
                } else {
                    Toast.makeText(this@AvatarSelectionActivity, "Error en el registro", Toast.LENGTH_SHORT).show()
                    btnContinue.isEnabled = true
                }
            } catch (e: Exception) {
                Toast.makeText(this@AvatarSelectionActivity, "Error de red", Toast.LENGTH_SHORT).show()
                btnContinue.isEnabled = true
            }
        }
    }
}