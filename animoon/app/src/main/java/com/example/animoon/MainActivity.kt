package com.example.animoon

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.animoon.data.network.ApiClient
import com.example.animoon.ui.minigame.Game1CinematicActivity
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

import com.example.animoon.ui.base.BaseActivity

class MainActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnPlayGame1 = findViewById<MaterialButton>(R.id.btnPlayGame1)
        val btnCheckUsers = findViewById<MaterialButton>(R.id.btnCheckUsers)
        val btnLogout = findViewById<MaterialButton>(R.id.btnLogout)

        btnPlayGame1.setOnClickListener {
            startActivity(Intent(this, Game1CinematicActivity::class.java))
        }

        btnCheckUsers.setOnClickListener {
            checkActiveUsers()
        }

        btnLogout.setOnClickListener {
            logout()
        }
    }

    private fun logout() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // Notificar al backend
                ApiClient.authService.logout()
            } catch (e: Exception) {
                // Ignorar si hay error de red, igual borramos token
            }
            
            withContext(Dispatchers.Main) {
                // Borrar token local
                com.example.animoon.data.network.TokenManager.clearToken()
                Toast.makeText(this@MainActivity, "Sesión cerrada", Toast.LENGTH_SHORT).show()
                
                // Redirigir a Splash
                val intent = Intent(this@MainActivity, com.example.animoon.ui.splash.SplashActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(intent)
                finish()
            }
        }
    }

    private fun checkActiveUsers() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = ApiClient.envService.getActiveUsers()
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        val body = response.body()
                        var message = ""
                        body?.zonas?.forEach { (zona, usuarios) ->
                            message += "[$zona]: ${usuarios.size} usuarios\n"
                            usuarios.forEach { user ->
                                message += "  - ${user.nickname} (x:${user.x}, y:${user.y})\n"
                            }
                        }
                        
                        if (message.isBlank()) {
                            message = "No hay usuarios conectados."
                        }

                        AlertDialog.Builder(this@MainActivity)
                            .setTitle("Usuarios Activos (SD)")
                            .setMessage(message)
                            .setPositiveButton("Cerrar", null)
                            .show()
                    } else {
                        Toast.makeText(this@MainActivity, "Error al consultar SD: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error de red: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}