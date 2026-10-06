package com.example.animoon

import android.app.Dialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import com.example.animoon.data.model.PlayerState
import com.example.animoon.ui.profile.AvatarDrawableResolver
import androidx.constraintlayout.widget.ConstraintLayout

import android.view.View
import android.view.Window
import android.widget.Toast
import android.widget.Button
import androidx.appcompat.app.AlertDialog
import androidx.lifecycle.lifecycleScope
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.game1.Game1CinematicActivity
import com.example.animoon.ui.minigame.MinigamesActivity
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.example.animoon.ui.settings.SettingsActivity
import com.example.animoon.ui.profile.ProfileActivity
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import android.widget.ImageView
import com.example.animoon.ui.splash.SplashActivity
import com.example.animoon.ui.world.WorldMapDialogFragment
import com.example.animoon.ui.world.WorldZone

class MainActivity : BaseActivity() {

    companion object {
        private const val STATE_WORLD_ZONE = "state_world_zone"
    }

    private var currentZone = WorldZone.BASE

    // =========================================================
    // ON CREATE
    // =========================================================
    override fun onCreate(savedInstanceState: Bundle?) {
        TokenManager.init(applicationContext)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // =====================================================
        // CONEXIÓN MULTIJUGADOR
        // =====================================================
        com.example.animoon.data.network.WebSocketManager.connect("base_principal")
        
        findViewById<ConstraintLayout>(R.id.worldLayer)?.setOnTouchListener { _, event ->
            if (event.action == android.view.MotionEvent.ACTION_UP) {
                com.example.animoon.data.network.WebSocketManager.sendMessage(
                    com.example.animoon.data.model.MoveMessage(event.x, event.y)
                )
            }
            true
        }

        lifecycleScope.launch {
            com.example.animoon.data.network.WebSocketManager.playersInZone.collectLatest { players ->
                renderPlayersInZone(players)
            }
        }

                // MI PERFIL
        findViewById<MaterialButton>(
            R.id.btnMyProfile
        ).setOnClickListener {
            startActivity(
                ProfileActivity.myProfileIntent(this)
            )
        }

        findViewById<MaterialButton>(R.id.btnDemoProfiles)?.setOnClickListener {
            val players = com.example.animoon.data.network.WebSocketManager.playersInZone.value
            if (players.isEmpty()) {
                android.widget.Toast.makeText(this, "No hay otros jugadores conectados", android.widget.Toast.LENGTH_SHORT).show()
            } else {
                val names = players.map { it.nickname }.toTypedArray()
                android.app.AlertDialog.Builder(this)
                    .setTitle("Jugadores Activos")
                    .setItems(names) { _, which ->
                        startActivity(ProfileActivity.playerProfileIntent(this, players[which].usuarioId))
                    }
                    .show()
            }
        }

        
        

        // Aquí continúa tu código actual:
        // REFERENCIAS DEL HUD, Ajustes, Minijuegos, etc.


        // =====================================================
        // REFERENCIAS DEL HUD
        // =====================================================

        val btnSettings =
            findViewById<MaterialButton>(R.id.btnSettings)

        val btnMinigames =
            findViewById<MaterialButton>(R.id.btnMinigames)


        // =====================================================
        // AJUSTES
        // =====================================================

        btnSettings.setOnClickListener {
            startActivity(
                Intent(
                    this,
                    SettingsActivity::class.java
                )
            )
        }

        currentZone = WorldZone.fromId(
            savedInstanceState?.getString(STATE_WORLD_ZONE)
        )

        supportFragmentManager.setFragmentResultListener(
            WorldMapDialogFragment.REQUEST_KEY,
            this
        ) { _, result ->

            val selectedZone = WorldZone.fromId(
                result.getString(WorldMapDialogFragment.RESULT_ZONE_ID)
            )

            renderZone(selectedZone)
        }

        findViewById<MaterialButton>(
            R.id.btnWorldMap
        ).setOnClickListener {
            openWorldMap()
        }

        renderZone(currentZone)

        // =====================================================
        // BOTÓN GENERAL DE MINIJUEGOS
        // =====================================================

        btnMinigames.setOnClickListener {

            val intent =
                Intent(
                    this,
                    MinigamesActivity::class.java
                )

            startActivity(intent)
        }
    }


    // =========================================================
    // DIÁLOGO DE ENTRADA AL CENTRO DE ENTRENAMIENTO
    // =========================================================

    
    private val playerViews = mutableMapOf<String, android.view.View>()

    private fun renderPlayersInZone(players: List<com.example.animoon.data.model.PlayerState>) {
        val worldLayer = findViewById<androidx.constraintlayout.widget.ConstraintLayout>(R.id.worldLayer)
        if (worldLayer == null) return

        val currentIds = players.map { it.usuarioId }.toSet()
        val toRemove = playerViews.keys.filter { it !in currentIds }
        for (id in toRemove) {
            worldLayer.removeView(playerViews[id])
            playerViews.remove(id)
        }

        for (player in players) {
            val playerView = playerViews[player.usuarioId] ?: run {
                val newView = android.widget.LinearLayout(this)
                newView.orientation = android.widget.LinearLayout.VERTICAL
                newView.gravity = android.view.Gravity.CENTER
                
                val avatarImage = android.widget.ImageView(this)
                avatarImage.layoutParams = android.widget.LinearLayout.LayoutParams(160, 160)
                
                val species = player.avatar?.get("especie") ?: "gato"
                val color = player.avatar?.get("color") ?: "azul"
                val avatarRes = com.example.animoon.ui.profile.AvatarDrawableResolver.resolve(species, color) ?: R.drawable.avatar_cat_blue
                avatarImage.setImageResource(avatarRes)
                
                val nicknameText = android.widget.TextView(this)
                nicknameText.text = player.nickname
                nicknameText.setTextColor(android.graphics.Color.WHITE)
                nicknameText.setShadowLayer(4f, 0f, 0f, android.graphics.Color.BLACK)
                nicknameText.textSize = 14f
                
                newView.addView(avatarImage)
                newView.addView(nicknameText)
                
                newView.setOnClickListener {
                    startActivity(com.example.animoon.ui.profile.ProfileActivity.playerProfileIntent(this, player.usuarioId))
                }
                
                val params = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams(
                    androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.WRAP_CONTENT,
                    androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.WRAP_CONTENT
                )
                params.topToTop = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.PARENT_ID
                params.startToStart = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.PARENT_ID
                newView.layoutParams = params
                
                worldLayer.addView(newView)
                playerViews[player.usuarioId] = newView
                
                // Posicion inicial sin animacion
                newView.translationX = player.x - 80f // centrar
                newView.translationY = player.y - 100f // centrar
                
                newView
            }
            
            // Actualizar posicion con animacion suave
            playerView.animate()
                .translationX(player.x - 80f)
                .translationY(player.y - 100f)
                .setDuration(150)
                .start()
        }
    }

    // =========================================================
    // ABRIR MINIJUEGO 1
    // =========================================================

    private fun openGame1() {

        /*
         * El jugador entra primero a la cinemática.
         *
         * Desde Game1CinematicActivity continuará
         * posteriormente hacia Game1Activity.
         */

        val intent = Intent(
            this,
            Game1CinematicActivity::class.java
        )

        startActivity(intent)
    }


    // =========================================================
    // CERRAR SESIÓN
    // =========================================================

    private fun logout() {

        lifecycleScope.launch(
            Dispatchers.IO
        ) {

            try {

                /*
                 * Avisar al backend que el usuario
                 * cerró su sesión.
                 */
                ApiClient.authService.logout()

            } catch (e: Exception) {

                /*
                 * Si falla la red no impedimos
                 * el cierre local de la sesión.
                 */
            }


            withContext(
                Dispatchers.Main
            ) {

                // Borrar token local y cerrar WebSocket
                TokenManager.clearToken()
                com.example.animoon.data.network.WebSocketManager.disconnect()


                Toast.makeText(
                    this@MainActivity,
                    "Sesión cerrada",
                    Toast.LENGTH_SHORT
                ).show()


                /*
                 * Regresar al Splash.
                 */
                val intent = Intent(
                    this@MainActivity,
                    SplashActivity::class.java
                )


                /*
                 * Eliminamos las Activities anteriores
                 * para evitar volver al Lobby usando atrás.
                 */
                intent.flags =
                    Intent.FLAG_ACTIVITY_NEW_TASK or
                            Intent.FLAG_ACTIVITY_CLEAR_TASK


                startActivity(intent)

                finish()
            }
        }
    }


    // =========================================================
    // CONSULTAR USUARIOS ACTIVOS
    // =========================================================

    private fun checkActiveUsers() {

        lifecycleScope.launch(
            Dispatchers.IO
        ) {

            try {

                /*
                 * Consultar usuarios conectados
                 * actualmente en el backend.
                 */
                val response =
                    ApiClient.envService.getActiveUsers()


                withContext(
                    Dispatchers.Main
                ) {

                    if (
                        response.isSuccessful
                    ) {

                        val body =
                            response.body()


                        var message = ""


                        /*
                         * Temporalmente mostramos la
                         * información mediante un diálogo.
                         *
                         * Posteriormente estos usuarios
                         * aparecerán directamente como
                         * avatares dentro del worldLayer.
                         */
                        body?.zonas?.forEach {
                                (zona, usuarios) ->


                            message +=
                                "[$zona]: " +
                                        "${usuarios.size} usuarios\n"


                            usuarios.forEach {
                                    user ->


                                message +=
                                    "  - ${user.nickname} " +
                                            "(x:${user.x}, " +
                                            "y:${user.y})\n"
                            }
                        }


                        /*
                         * En caso de que no exista
                         * ningún usuario conectado.
                         */
                        if (
                            message.isBlank()
                        ) {

                            message =
                                "No hay usuarios conectados."
                        }


                        AlertDialog.Builder(
                            this@MainActivity
                        )
                            .setTitle(
                                "Usuarios activos"
                            )
                            .setMessage(
                                message
                            )
                            .setPositiveButton(
                                "Cerrar",
                                null
                            )
                            .show()

                    } else {

                        Toast.makeText(
                            this@MainActivity,

                            "Error al consultar usuarios: " +
                                    "${response.code()}",

                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }

            } catch (e: Exception) {

                withContext(
                    Dispatchers.Main
                ) {

                    Toast.makeText(
                        this@MainActivity,

                        "Error de red: ${e.message}",

                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }

    

    private fun openWorldMap() {
        val manager = supportFragmentManager

        if (manager.isStateSaved) return

        if (
            manager.findFragmentByTag(
                WorldMapDialogFragment.TAG
            ) != null
        ) {
            return
        }

        WorldMapDialogFragment
            .newInstance(currentZone)
            .showNow(manager, WorldMapDialogFragment.TAG)
    }

    private fun renderZone(zone: WorldZone) {
        currentZone = zone

        val background = findViewById<ImageView>(
            R.id.ivLobbyBackground
        )

        findViewById<MaterialButton>(
            R.id.btnZoneName
        ).text = zone.title

        val backgroundResource = when (zone) {
            WorldZone.BASE ->
                R.drawable.lobby_base_principal

            WorldZone.CRATERS ->
                R.drawable.world_crateres

            WorldZone.VILLAGE ->
                R.drawable.world_aldea

            WorldZone.DARK_SIDE ->
                R.drawable.world_lado_oscuro
        }

        background.setImageResource(backgroundResource)
    }
}




