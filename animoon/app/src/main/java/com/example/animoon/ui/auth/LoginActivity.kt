package com.example.animoon.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import android.util.Log

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val etApelativo = findViewById<TextInputEditText>(R.id.etLoginApelativo)
        val etPassword = findViewById<TextInputEditText>(R.id.etLoginPassword)

        val btnLogin = findViewById<MaterialButton>(R.id.btnLogin)
        val btnCreateAccount =
            findViewById<MaterialButton>(R.id.btnCreateAccount)

        val tvForgotPassword =
            findViewById<TextView>(R.id.tvForgotPassword)

        btnLogin.setOnClickListener {

            val apelativo = etApelativo.text.toString().trim()
            val password = etPassword.text.toString()

            if (apelativo.isEmpty() || password.isEmpty()) {
                Toast.makeText(
                    this,
                    "Completa tu apelativo y contraseña",
                    Toast.LENGTH_SHORT
                ).show()

                return@setOnClickListener
            }

            btnLogin.isEnabled = false

            // Generar par de llaves X25519 para el canal seguro
            val clientKeyPair = com.example.animoon.security.CryptoManager.generateEphemeralKeyPair()
            val clientPubKeyB64 = com.example.animoon.security.CryptoManager.getPublicKeyBase64(clientKeyPair)

            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val request = com.example.animoon.data.model.LoginRequest(apelativo, password, clientPubKeyB64)
                    val response = com.example.animoon.data.network.ApiClient.authService.login(request)
                    
                    withContext(Dispatchers.Main) {
                        btnLogin.isEnabled = true
                        if (response.isSuccessful) {
                            val token = response.body()?.access_token
                            if (!token.isNullOrEmpty()) {
                                com.example.animoon.data.network.TokenManager.saveToken(token)
                            }

                            // 1. Recibir llave del servidor y computar el Shared Secret (AES-256)
                            val serverPubKeyB64 = response.body()?.server_ecdhe_public_key
                            if (!serverPubKeyB64.isNullOrEmpty()) {
                                val sharedSecretB64 = com.example.animoon.security.CryptoManager.computeSharedSecret(
                                    clientKeyPair, serverPubKeyB64
                                )
                                com.example.animoon.data.network.TokenManager.saveSessionSecret(sharedSecretB64)
                                Log.d("ECDHE", "Secreto AES-256 derivado y guardado correctamente.")
                            }

                            Toast.makeText(
                                this@LoginActivity,
                                response.body()?.message ?: "Login exitoso",
                                Toast.LENGTH_SHORT
                            ).show()
                            // Aquí puedes navegar a la MainActivity
                            val intent = Intent(this@LoginActivity, com.example.animoon.MainActivity::class.java)
                            startActivity(intent)
                            finish()
                        } else {
                            var errorMsg = "Error en el inicio de sesión"
                            try {
                                val errorBody = response.errorBody()?.string()
                                if (errorBody != null) {
                                    val jsonObject = org.json.JSONObject(errorBody)
                                    if (jsonObject.has("detail")) {
                                        errorMsg = jsonObject.getString("detail")
                                    }
                                }
                            } catch (e: Exception) {
                                e.printStackTrace()
                            }
                            Toast.makeText(
                                this@LoginActivity,
                                errorMsg,
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }
                } catch (e: Exception) {
                    withContext(Dispatchers.Main) {
                        btnLogin.isEnabled = true
                        Log.e("LoginActivity", "Error de red", e)
                        Toast.makeText(
                            this@LoginActivity,
                            "Error de conexión",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
            }
        }

        btnCreateAccount.setOnClickListener {

            val intent = Intent(
                this,
                RegisterActivity::class.java
            )

            startActivity(intent)
        }

        tvForgotPassword.setOnClickListener {

            Toast.makeText(
                this,
                "Recuperación de contraseña pendiente",
                Toast.LENGTH_SHORT
            ).show()
        }
    }
}