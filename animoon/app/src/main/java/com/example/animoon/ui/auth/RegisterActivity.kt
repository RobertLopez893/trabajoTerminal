package com.example.animoon.ui.auth

import android.os.Bundle
import android.widget.CheckBox
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

import androidx.lifecycle.lifecycleScope
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.model.FinalRegisterRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

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

            // Deshabilitamos el botón mientras carga
            btnSendSms.isEnabled = false

            // Llamada asíncrona a la API
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    // Por ahora mockeamos los datos que faltan en la UI (código y avatar)
                    val request = FinalRegisterRequest(
                        nickname = apelativo,
                        telefono = phone,
                        codigo_verificacion = "123456", // Simulado
                        password = password,
                        avatar_especie = "gato", // Simulado
                        avatar_color = "naranja" // Simulado
                    )

                    val response = ApiClient.authService.finalRegister(request)

                    withContext(Dispatchers.Main) {
                        btnSendSms.isEnabled = true
                        if (response.isSuccessful) {
                            val body = response.body()
                            Toast.makeText(
                                this@RegisterActivity,
                                "¡Éxito! ${body?.message}",
                                Toast.LENGTH_LONG
                            ).show()
                            // Regresar al Login
                            finish()
                        } else {
                            Toast.makeText(
                                this@RegisterActivity,
                                "Error del servidor: ${response.code()}",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        btnSendSms.isEnabled = true
                        Toast.makeText(
                            this@RegisterActivity,
                            "Error de red: ${e.message}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            }
        }
    }
}