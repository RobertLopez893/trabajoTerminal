package com.example.animoon.ui.auth

import android.os.Bundle
import android.widget.CheckBox
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val etApelativo =
            findViewById<TextInputEditText>(R.id.etRegisterApelativo)

        val etPhone =
            findViewById<TextInputEditText>(R.id.etTutorPhone)

        val etPassword =
            findViewById<TextInputEditText>(R.id.etRegisterPassword)

        val etConfirmPassword =
            findViewById<TextInputEditText>(R.id.etConfirmPassword)

        val checkTerms =
            findViewById<CheckBox>(R.id.checkTerms)

        val btnSendSms =
            findViewById<MaterialButton>(R.id.btnSendSms)

        val btnCancel =
            findViewById<MaterialButton>(R.id.btnCancel)

        /*
         * Terminos y condiciones
         */
        btnSendSms.isEnabled = false

        checkTerms.setOnCheckedChangeListener { _, isChecked ->
            btnSendSms.isEnabled = isChecked
        }

        btnCancel.setOnClickListener {
            finish()
        }

        btnSendSms.setOnClickListener {

            val apelativo =
                etApelativo.text.toString().trim()

            val phone =
                etPhone.text.toString().trim()

            val password =
                etPassword.text.toString()

            val confirmPassword =
                etConfirmPassword.text.toString()

            if (
                apelativo.isEmpty() ||
                phone.isEmpty() ||
                password.isEmpty() ||
                confirmPassword.isEmpty()
            ) {

                Toast.makeText(
                    this,
                    "Completa todos los campos",
                    Toast.LENGTH_SHORT
                ).show()

                return@setOnClickListener
            }

            if (phone.length != 10) {

                Toast.makeText(
                    this,
                    "El teléfono debe tener 10 dígitos",
                    Toast.LENGTH_SHORT
                ).show()

                return@setOnClickListener
            }

            if (password.length < 8) {

                Toast.makeText(
                    this,
                    "La contraseña debe tener al menos 8 caracteres",
                    Toast.LENGTH_SHORT
                ).show()

                return@setOnClickListener
            }

            if (password != confirmPassword) {

                Toast.makeText(
                    this,
                    "Las contraseñas no coinciden",
                    Toast.LENGTH_SHORT
                ).show()

                return@setOnClickListener
            }

            /*
             * Más adelante:
             *
             * 1. Enviaremos los datos al backend.
             * 2. El backend solicitará el SMS.
             * 3. Navegaremos a la pantalla de verificación.
             */

            Toast.makeText(
                this,
                "Formulario listo para conectar al backend",
                Toast.LENGTH_SHORT
            ).show()
        }
    }
}