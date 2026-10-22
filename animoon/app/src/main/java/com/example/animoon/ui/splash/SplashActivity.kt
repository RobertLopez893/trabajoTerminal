package com.example.animoon.ui.splash

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.lifecycle.lifecycleScope
import com.example.animoon.MainActivity
import com.example.animoon.R
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager
import com.example.animoon.ui.auth.LoginActivity
import com.example.animoon.ui.base.BaseActivity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SplashActivity : BaseActivity() {
    override val observarSesionExpirada: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        val btnStart = findViewById<Button>(R.id.btnStart)
        TokenManager.init(applicationContext)

        btnStart.setOnClickListener {
            btnStart.isEnabled = false
            val token = TokenManager.getToken()

            if (token.isNullOrEmpty()) {
                goToLogin()
            } else {
                showLoading("Verificando sesión...")
                lifecycleScope.launch(Dispatchers.IO) {
                    try {
                        // Verificamos activamente si la sesión sigue viva en el backend
                        val response = ApiClient.authService.getProfile("me")
                        withContext(Dispatchers.Main) {
                            hideLoading()
                            btnStart.isEnabled = true
                            if (response.isSuccessful) {
                                // Sesión válida: entrar al mundo
                                val intent = Intent(this@SplashActivity, MainActivity::class.java)
                                startActivity(intent)
                                finish()
                            } else {
                                // Token expirado o revocado (401 u otro error de autenticación)
                                TokenManager.clearToken()
                                goToLogin()
                            }
                        }
                    } catch (e: Exception) {
                        withContext(Dispatchers.Main) {
                            hideLoading()
                            btnStart.isEnabled = true
                            // Si no hay conexión al backend, enviamos al login para reintentar limpiamente
                            TokenManager.clearToken()
                            goToLogin()
                        }
                    }
                }
            }
        }
    }

    private fun goToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        startActivity(intent)
        finish()
    }
}
