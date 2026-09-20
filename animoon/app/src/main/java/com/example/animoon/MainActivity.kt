package com.example.animoon

import android.app.Dialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.Toast
import android.widget.Button
import androidx.appcompat.app.AlertDialog
import androidx.lifecycle.lifecycleScope
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.Game1CinematicActivity
import com.example.animoon.ui.splash.SplashActivity
import com.example.animoon.ui.minigame.MinigamesActivity
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext


class MainActivity : BaseActivity() {


    // =========================================================
    // ON CREATE
    // =========================================================

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)


        // =====================================================
        // REFERENCIAS DEL HUD
        // =====================================================

        val btnCheckUsers =
            findViewById<MaterialButton>(R.id.btnCheckUsers)

        val btnLogout =
            findViewById<MaterialButton>(R.id.btnLogout)

        val btnMinigames =
            findViewById<MaterialButton>(R.id.btnMinigames)


        // =====================================================
        // ELEMENTOS DEL ESCENARIO
        // =====================================================

        val hotspotMinigames =
            findViewById<View>(R.id.hotspotMinigames)


        // =====================================================
        // USUARIOS ACTIVOS
        // =====================================================

        btnCheckUsers.setOnClickListener {

            checkActiveUsers()
        }


        // =====================================================
        // CERRAR SESIÓN
        // =====================================================

        btnLogout.setOnClickListener {

            logout()
        }


        // =====================================================
        // BOTÓN GENERAL DE MINIJUEGOS
        // =====================================================
        //
        // Este botón se conservará para posteriormente abrir
        // una nueva Activity con todos los minijuegos.
        //
        // Por ahora NO tendrá ninguna acción.
        //

        btnMinigames.setOnClickListener {

            val intent =
                Intent(
                    this,
                    MinigamesActivity::class.java
                )

            startActivity(intent)
        }


        // =====================================================
        // PORTAL DEL CENTRO DE ENTRENAMIENTO
        // =====================================================
        //
        // El portal central sí pertenece directamente
        // al Minijuego 1.
        //
        // Primero mostramos una confirmación.
        //

        hotspotMinigames.setOnClickListener {

            showMinigameDialog()
        }
    }


    // =========================================================
    // DIÁLOGO DE ENTRADA AL CENTRO DE ENTRENAMIENTO
    // =========================================================

    private fun showMinigameDialog() {

        val dialog = Dialog(this)

        dialog.requestWindowFeature(
            Window.FEATURE_NO_TITLE
        )

        dialog.setContentView(
            R.layout.dialog_enter_minigame
        )


        /*
         * Queremos que el niño tome una decisión explícita
         * usando uno de los dos botones.
         */
        dialog.setCancelable(true)

        /*
         * Evitamos que un toque accidental fuera del cuadro
         * cierre el diálogo.
         */
        dialog.setCanceledOnTouchOutside(false)


        /*
         * Fondo transparente para dejar visible únicamente
         * nuestra tarjeta personalizada.
         */
        dialog.window?.setBackgroundDrawable(
            ColorDrawable(Color.TRANSPARENT)
        )


        val btnStay =
            dialog.findViewById<MaterialButton>(
                R.id.btnStay
            )

        val btnEnter =
            dialog.findViewById<Button>(
                R.id.btnEnter
            )


        // ---------------------------------------------------------
        // QUEDARME EN LA BASE PRINCIPAL
        // ---------------------------------------------------------

        btnStay.setOnClickListener {

            dialog.dismiss()
        }


        // ---------------------------------------------------------
        // ENTRAR AL CENTRO DE ENTRENAMIENTO
        // ---------------------------------------------------------

        btnEnter.setOnClickListener {

            dialog.dismiss()

            openGame1()
        }


        // ---------------------------------------------------------
        // MOSTRAR
        // ---------------------------------------------------------

        dialog.show()

        // ---------------------------------------------------------
        // OSCURECER SUAVEMENTE EL LOBBY
        // ---------------------------------------------------------
        //
        // Ayuda a que el usuario concentre su atención
        // en la confirmación sin ocultar completamente
        // el escenario.
        //

        dialog.window?.let { window ->

            window.addFlags(
                android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND
            )

            val params = window.attributes

            params.dimAmount = 0.35f

            window.attributes = params
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

                // Borrar token local
                TokenManager.clearToken()


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
}