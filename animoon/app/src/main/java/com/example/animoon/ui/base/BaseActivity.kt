package com.example.animoon.ui.base

import android.content.Intent
import android.content.pm.ActivityInfo
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.view.LayoutInflater
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.data.network.TokenManager
import com.example.animoon.ui.auth.LoginActivity
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

open class BaseActivity : AppCompatActivity() {

    private var sessionDialog: AlertDialog? = null


    // =========================================================
    // ON CREATE
    // =========================================================

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)


        // -----------------------------------------------------
        // ORIENTACIÓN HORIZONTAL
        // -----------------------------------------------------

        /*
         * ANIMOON está diseñado exclusivamente
         * para funcionar en orientación horizontal.
         *
         * SENSOR_LANDSCAPE permite utilizar ambas
         * orientaciones horizontales dependiendo
         * de cómo el usuario sostenga el dispositivo,
         * pero impide utilizar la aplicación en vertical.
         */
        requestedOrientation =
            ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE


        // -----------------------------------------------------
        // MODO INMERSIVO
        // -----------------------------------------------------

        activarModoInmersivo()


        // -----------------------------------------------------
        // SESIÓN EXPIRADA
        // -----------------------------------------------------

        lifecycleScope.launch {

            TokenManager.sessionExpiredFlow.collect {

                showSessionExpiredDialog()
            }
        }
    }


    // =========================================================
    // MODO INMERSIVO
    // =========================================================

    /**
     * Oculta las barras del sistema:
     *
     * - barra de estado
     * - barra de navegación
     *
     * El usuario puede mostrarlas temporalmente
     * mediante un gesto desde el borde.
     */
    private fun activarModoInmersivo() {

        /*
         * Permitimos que nuestra aplicación
         * utilice toda la pantalla.
         */
        WindowCompat.setDecorFitsSystemWindows(
            window,
            false
        )


        val controller =
            WindowInsetsControllerCompat(
                window,
                window.decorView
            )


        /*
         * Ocultamos tanto la barra superior
         * como la navegación inferior.
         */
        controller.hide(
            WindowInsetsCompat.Type.systemBars()
        )


        /*
         * Las barras pueden aparecer temporalmente
         * mediante un gesto del usuario.
         *
         * Después Android las vuelve a ocultar.
         */
        controller.systemBarsBehavior =
            WindowInsetsControllerCompat
                .BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
    }


    // =========================================================
    // RECUPERAR MODO INMERSIVO
    // =========================================================

    override fun onResume() {

        super.onResume()

        activarModoInmersivo()
    }


    override fun onWindowFocusChanged(
        hasFocus: Boolean
    ) {

        super.onWindowFocusChanged(hasFocus)

        if (hasFocus) {

            activarModoInmersivo()
        }
    }


    // =========================================================
    // SESIÓN EXPIRADA
    // =========================================================

    private fun showSessionExpiredDialog() {

        if (
            isFinishing ||
            isDestroyed ||
            sessionDialog?.isShowing == true
        ) {

            return
        }


        val view =
            LayoutInflater
                .from(this)
                .inflate(
                    R.layout.dialog_session_expired,
                    null
                )


        val builder =
            AlertDialog.Builder(this)


        builder.setView(view)

        builder.setCancelable(false)


        try {

            sessionDialog =
                builder.create()


            sessionDialog
                ?.window
                ?.setBackgroundDrawable(
                    ColorDrawable(
                        Color.TRANSPARENT
                    )
                )


            view.findViewById<MaterialButton>(
                R.id.btnReconnect
            ).setOnClickListener {

                sessionDialog?.dismiss()

                TokenManager.clearToken()


                val loginIntent =
                    Intent(
                        this,
                        LoginActivity::class.java
                    )


                loginIntent.flags =
                    Intent.FLAG_ACTIVITY_NEW_TASK or
                            Intent.FLAG_ACTIVITY_CLEAR_TASK


                startActivity(loginIntent)

                finish()
            }


            sessionDialog?.show()


        } catch (e: Exception) {

            TokenManager.clearToken()


            val loginIntent =
                Intent(
                    this,
                    LoginActivity::class.java
                )


            loginIntent.flags =
                Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TASK


            startActivity(loginIntent)

            finish()
        }
    }


    // =========================================================
    // ON DESTROY
    // =========================================================

    override fun onDestroy() {

        super.onDestroy()
    }
}