package com.example.animoon.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

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

            /*
             * Más adelante aquí llamaremos al backend
             */
            Toast.makeText(
                this,
                "Inicio de sesión listo para conectar al backend",
                Toast.LENGTH_SHORT
            ).show()
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