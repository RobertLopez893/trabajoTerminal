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

    protected open val observarSesionExpirada: Boolean = true

    private var loadingDialog: AlertDialog? = null

    fun showLoading(message: String) {
        if (isFinishing || isDestroyed) return
        if (loadingDialog?.isShowing == true) return

        val view = LayoutInflater.from(this).inflate(R.layout.dialog_loading, null)
        view.findViewById<android.widget.TextView>(R.id.txtLoadingMessage).text = message
        
        val builder = AlertDialog.Builder(this)
        builder.setView(view)
        builder.setCancelable(false)
        
        loadingDialog = builder.create()
        loadingDialog?.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        loadingDialog?.show()
    }

    fun hideLoading() {
        loadingDialog?.dismiss()
        loadingDialog = null
    }



    // =========================================================
    // ON CREATE
    // =========================================================

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        TokenManager.init(applicationContext)

        // -----------------------------------------------------
        // ORIENTACIÓN HORIZONTAL
        // -----------------------------------------------------

        requestedOrientation =
            ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE


        // -----------------------------------------------------
        // MODO INMERSIVO
        // -----------------------------------------------------

        activarModoInmersivo()


        // -----------------------------------------------------
        // SESIÓN EXPIRADA
        // -----------------------------------------------------

        if (observarSesionExpirada) {
            lifecycleScope.launch {
                TokenManager.sessionExpiredFlow.collect {
                    showSessionExpiredDialog()
                }
            }
        }
    }


    // =========================================================
    // MODO INMERSIVO
    // =========================================================
    private fun activarModoInmersivo() {


        WindowCompat.setDecorFitsSystemWindows(
            window,
            false
        )


        val controller =
            WindowInsetsControllerCompat(
                window,
                window.decorView
            )

        controller.hide(
            WindowInsetsCompat.Type.systemBars()
        )


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

    protected fun ajustarTamanoDialogo(dialog: android.app.Dialog) {
        val metrics = resources.displayMetrics
        val density = metrics.density

        val margen = (24 * density).toInt()
        val anchoMaximo = resources.getDimensionPixelSize(
            com.example.animoon.R.dimen.animoon_dialog_max_width
        )

        val anchoDisponible = (metrics.widthPixels - margen * 2)
            .coerceAtLeast(1)

        val ancho = minOf(anchoMaximo, anchoDisponible)
        val alturaMaxima = (metrics.heightPixels - margen * 2)
            .coerceAtLeast(1)

        dialog.window?.setLayout(
            ancho,
            android.view.ViewGroup.LayoutParams.WRAP_CONTENT
        )

        dialog.window?.decorView?.post {
            val contenido = dialog.window?.decorView ?: return@post

            if (contenido.height > alturaMaxima) {
                dialog.window?.setLayout(ancho, alturaMaxima)
            }
        }
    }


    // =========================================================
    // ON DESTROY
    // =========================================================

    override fun onDestroy() {

        super.onDestroy()
    }
}