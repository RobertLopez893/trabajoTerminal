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
import androidx.activity.OnBackPressedCallback
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.repeatOnLifecycle
import com.example.animoon.data.network.WebSocketManager
import com.example.animoon.ui.world.CratersActivity
import com.example.animoon.ui.world.VillageActivity
import com.example.animoon.ui.world.DarkSideActivity

open class MainActivity : BaseActivity() {

    protected open val screenZone: WorldZone = WorldZone.BASE
    protected open val screenLayout: Int = R.layout.activity_main

    private val currentZone: WorldZone
        get() = screenZone

    private var navigatingToZone = false

    // =========================================================
    // ON CREATE
    // =========================================================
    override fun onCreate(savedInstanceState: Bundle?) {
        TokenManager.init(applicationContext)

        super.onCreate(savedInstanceState)
        setContentView(screenLayout)

        findViewById<MaterialButton>(R.id.btnZoneName).text =
            currentZone.title

        configurarRegresoDelMundo()
        // =====================================================
        // CONEXIÓN MULTIJUGADOR
        // =====================================================
        WebSocketManager.connect(currentZone.id)

        val worldLayer = findViewById<ConstraintLayout>(R.id.worldLayer)
        worldLayer?.post {
            val width = worldLayer.width.toFloat()
            val height = worldLayer.height.toFloat()
            if (width > 0 && height > 0) {
                // Posicionar en el centro de la zona caminable (y = 70% de la pantalla)
                val clamped = com.example.animoon.ui.world.WorldBoundsValidator.clampPoint(currentZone, 0.50f, 0.70f)
                val targetX = clamped.x * width
                val targetY = clamped.y * height
                WebSocketManager.sendMessage(
                    com.example.animoon.data.model.MoveMessage(targetX, targetY)
                )
            }
        }

        worldLayer?.setOnTouchListener { _, event ->
            if (event.action == android.view.MotionEvent.ACTION_UP) {
                val width = worldLayer.width.toFloat()
                val height = worldLayer.height.toFloat()
                if (width > 0 && height > 0) {
                    val normX = (event.x / width).coerceIn(0f, 1f)
                    val normY = (event.y / height).coerceIn(0f, 1f)
                    // Validar y sujetar a la zona de colisión transitable
                    val clamped = com.example.animoon.ui.world.WorldBoundsValidator.clampPoint(currentZone, normX, normY)
                    val targetX = clamped.x * width
                    val targetY = clamped.y * height
                    com.example.animoon.data.network.WebSocketManager.sendMessage(
                        com.example.animoon.data.model.MoveMessage(targetX, targetY)
                    )
                }
            }
            true
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                WebSocketManager.playersInZone.collectLatest { players ->
                    renderPlayersInZone(players)
                }
            }
        }

        // Escuchar invitaciones de chat en tiempo real
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                WebSocketManager.chatInvitations.collectLatest { invite ->
                    mostrarAlertaInvitacionChat(invite)
                }
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


        supportFragmentManager.setFragmentResultListener(
            WorldMapDialogFragment.REQUEST_KEY,
            this
        ) { _, result ->

            val selectedZone = WorldZone.fromId(
                result.getString(WorldMapDialogFragment.RESULT_ZONE_ID)
            )

            navigateToZone(selectedZone)
        }

        findViewById<MaterialButton>(
            R.id.btnWorldMap
        ).setOnClickListener {
            openWorldMap()
        }

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

    
    private data class PlayerMovementState(
        var targetX: Float = Float.NaN,
        var targetY: Float = Float.NaN,
        var waddleAnimator: android.animation.Animator? = null
    )

    private val playerViews = mutableMapOf<String, android.view.View>()
    private val playerMoveStates = mutableMapOf<String, PlayerMovementState>()

    private fun renderPlayersInZone(players: List<com.example.animoon.data.model.PlayerState>) {
        val worldLayer = findViewById<androidx.constraintlayout.widget.ConstraintLayout>(R.id.worldLayer)
        if (worldLayer == null) return

        val density = resources.displayMetrics.density
        // Sprites más grandes: ~110dp (escala responsive adaptada a la densidad de pantalla)
        val spriteSize = (110 * density).toInt()
        val halfSpriteWidth = spriteSize / 2f
        val halfSpriteHeight = (spriteSize + (22 * density)) / 2f

        val currentIds = players.map { it.usuarioId }.toSet()
        val toRemove = playerViews.keys.filter { it !in currentIds }
        for (id in toRemove) {
            playerMoveStates[id]?.waddleAnimator?.cancel()
            playerMoveStates.remove(id)
            worldLayer.removeView(playerViews[id])
            playerViews.remove(id)
        }

        for (player in players) {
            // Asegurar que las coordenadas del jugador respeten los límites del escenario
            val rawX = if (player.x <= 0f && worldLayer.width > 0) worldLayer.width / 2f else player.x
            val rawY = if (player.y <= 0f && worldLayer.height > 0) worldLayer.height * 0.70f else player.y

            val normX = if (worldLayer.width > 0) (rawX / worldLayer.width).coerceIn(0f, 1f) else 0.5f
            val normY = if (worldLayer.height > 0) (rawY / worldLayer.height).coerceIn(0f, 1f) else 0.7f
            val clampedNorm = com.example.animoon.ui.world.WorldBoundsValidator.clampPoint(currentZone, normX, normY)
            val px = if (worldLayer.width > 0) clampedNorm.x * worldLayer.width else rawX
            val py = if (worldLayer.height > 0) clampedNorm.y * worldLayer.height else rawY

            val moveState = playerMoveStates.getOrPut(player.usuarioId) { PlayerMovementState() }

            var isNewPlayer = false
            val playerView = playerViews[player.usuarioId] ?: run {
                isNewPlayer = true
                val newView = android.widget.LinearLayout(this)
                newView.orientation = android.widget.LinearLayout.VERTICAL
                newView.gravity = android.view.Gravity.CENTER
                
                val avatarImage = android.widget.ImageView(this)
                avatarImage.layoutParams = android.widget.LinearLayout.LayoutParams(spriteSize, spriteSize)
                
                val species = player.avatar?.get("especie") ?: "gato"
                val color = player.avatar?.get("color") ?: "azul"
                val avatarRes = com.example.animoon.ui.profile.AvatarDrawableResolver.resolve(species, color) ?: R.drawable.avatar_cat_blue
                avatarImage.setImageResource(avatarRes)
                
                val nicknameText = android.widget.TextView(this)
                nicknameText.text = player.nickname
                nicknameText.setTextColor(android.graphics.Color.WHITE)
                nicknameText.typeface = android.graphics.Typeface.DEFAULT_BOLD
                nicknameText.setShadowLayer(6f, 0f, 0f, android.graphics.Color.BLACK)
                nicknameText.textSize = 15f
                
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
                
                // Posición inicial directa (sin animación de caminata al aparecer)
                newView.translationX = px - halfSpriteWidth
                newView.translationY = py - halfSpriteHeight
                moveState.targetX = px
                moveState.targetY = py
                
                newView
            }

            if (isNewPlayer) {
                continue
            }

            // Si el objetivo es el mismo al que ya está caminando, no reiniciar la animación
            if (!moveState.targetX.isNaN() &&
                kotlin.math.abs(moveState.targetX - px) < 3f &&
                kotlin.math.abs(moveState.targetY - py) < 3f
            ) {
                continue
            }

            val currentX = playerView.translationX + halfSpriteWidth
            val currentY = playerView.translationY + halfSpriteHeight
            val dx = px - currentX
            val dy = py - currentY
            val distance = kotlin.math.hypot(dx.toDouble(), dy.toDouble()).toFloat()

            val viewGroup = playerView as? android.view.ViewGroup
            val avatarImg = viewGroup?.getChildAt(0)

            // Si la distancia es mínima, posicionar directamente
            if (distance < 6f * density) {
                moveState.targetX = px
                moveState.targetY = py
                moveState.waddleAnimator?.cancel()
                moveState.waddleAnimator = null
                avatarImg?.rotation = 0f
                avatarImg?.translationY = 0f
                playerView.translationX = px - halfSpriteWidth
                playerView.translationY = py - halfSpriteHeight
                continue
            }

            moveState.targetX = px
            moveState.targetY = py

            // 1. Orientación horizontal: girar sprite según hacia dónde camina
            if (dx < -4f * density) {
                avatarImg?.scaleX = -1f // Mirar a la izquierda
            } else if (dx > 4f * density) {
                avatarImg?.scaleX = 1f  // Mirar a la derecha
            }

            // 2. Velocidad de caminata constante: ~220 dp por segundo
            val speedPxPerSec = 220f * density
            val moveDuration = ((distance / speedPxPerSec) * 1000L).toLong().coerceIn(200L, 5000L)

            // 3. Animación de "pasitos / bamboleo" (Waddle y rebote rítmico)
            moveState.waddleAnimator?.cancel()
            if (avatarImg != null) {
                val rotAnim = android.animation.ObjectAnimator.ofFloat(avatarImg, "rotation", -5f, 5f).apply {
                    duration = 150
                    repeatMode = android.animation.ValueAnimator.REVERSE
                    repeatCount = android.animation.ValueAnimator.INFINITE
                }
                val hopAnim = android.animation.ObjectAnimator.ofFloat(avatarImg, "translationY", 0f, -4f * density).apply {
                    duration = 75
                    repeatMode = android.animation.ValueAnimator.REVERSE
                    repeatCount = android.animation.ValueAnimator.INFINITE
                }
                val animSet = android.animation.AnimatorSet().apply {
                    playTogether(rotAnim, hopAnim)
                    start()
                }
                moveState.waddleAnimator = animSet
            }

            // 4. Traslado suave a velocidad constante
            playerView.animate()
                .translationX(px - halfSpriteWidth)
                .translationY(py - halfSpriteHeight)
                .setDuration(moveDuration)
                .setInterpolator(android.view.animation.LinearInterpolator())
                .withEndAction {
                    moveState.waddleAnimator?.cancel()
                    moveState.waddleAnimator = null
                    avatarImg?.rotation = 0f
                    avatarImg?.translationY = 0f
                }
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

    private fun navigateToZone(zone: WorldZone) {
        if (
            zone == currentZone ||
            navigatingToZone ||
            isFinishing ||
            isDestroyed
        ) {
            return
        }

        val destination: Class<out MainActivity> = when (zone) {
            WorldZone.BASE -> MainActivity::class.java
            WorldZone.CRATERS -> CratersActivity::class.java
            WorldZone.VILLAGE -> VillageActivity::class.java
            WorldZone.DARK_SIDE -> DarkSideActivity::class.java
        }

        navigatingToZone = true

        WebSocketManager.switchZone(zone.id)

        startActivity(Intent(this, destination))
        finish()
    }

    private fun configurarRegresoDelMundo() {
        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(
                currentZone != WorldZone.BASE
            ) {
                override fun handleOnBackPressed() {
                    navigateToZone(WorldZone.BASE)
                }
            }
        )
    }

    private var activeChatInviteDialog: android.app.Dialog? = null

    private fun mostrarAlertaInvitacionChat(invite: com.example.animoon.data.network.ChatInvitation) {
        if (isFinishing || isDestroyed) return
        activeChatInviteDialog?.dismiss()

        activeChatInviteDialog = com.example.animoon.ui.common.ChatInvitationDialog.show(
            activity = this,
            invitation = invite,
            onAccept = {
                val chatIntent = Intent(this, com.example.animoon.ui.chat.ChatActivity::class.java).apply {
                    putExtra("EXTRA_TARGET_ID", invite.fromUserId)
                    putExtra("EXTRA_TARGET_NICKNAME", invite.fromNickname)
                    putExtra("EXTRA_TARGET_SPECIES", invite.fromSpecies)
                    putExtra("EXTRA_TARGET_COLOR", invite.fromColor)
                }
                startActivity(chatIntent)
            },
            onReject = {
                // Rechazado: el jugador sigue en el mundo normalmente
            }
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        activeChatInviteDialog?.dismiss()
        activeChatInviteDialog = null
        for (state in playerMoveStates.values) {
            state.waddleAnimator?.cancel()
        }
        playerMoveStates.clear()
        playerViews.clear()
    }
}




