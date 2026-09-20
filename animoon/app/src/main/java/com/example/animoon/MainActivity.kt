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

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnPlayGame1 = findViewById<MaterialButton>(R.id.btnPlayGame1)
        val btnCheckUsers = findViewById<MaterialButton>(R.id.btnCheckUsers)

        btnPlayGame1.setOnClickListener {
            startActivity(Intent(this, Game1CinematicActivity::class.java))
        }

        btnCheckUsers.setOnClickListener {
            checkActiveUsers()
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