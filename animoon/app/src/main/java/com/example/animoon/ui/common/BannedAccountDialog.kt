package com.example.animoon.ui.common

import android.app.Activity
import android.app.Dialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.TextView
import android.widget.Toast
import com.example.animoon.R
import com.example.animoon.data.network.TokenManager
import com.example.animoon.network.ChatWebSocketManager
import com.example.animoon.ui.splash.SplashActivity
import com.google.android.material.button.MaterialButton

object BannedAccountDialog {

    /**
     * Muestra el pop-up de cuenta suspendida con el estilo visual de Animoon.
     *
     * @param activity Actividad que invoca el diálogo (ChatActivity o LoginActivity)
     * @param motivo Detalle o razón de la suspensión (opcional)
     * @param isChatBan true si la expulsión ocurre en tiempo real durante una sesión de chat,
     *                  false si ocurre al intentar iniciar sesión en LoginActivity.
     * @param onDismissAction Callback ejecutado al presionar el botón de acción principal.
     */
    fun show(
        activity: Activity,
        motivo: String? = null,
        isChatBan: Boolean = false,
        onDismissAction: (() -> Unit)? = null
    ) {
        if (activity.isFinishing || activity.isDestroyed) return

        val dialog = Dialog(activity)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_account_banned)
        dialog.setCancelable(false)
        dialog.setCanceledOnTouchOutside(false)

        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        val width = (activity.resources.displayMetrics.widthPixels * 0.90).toInt()
        dialog.window?.setLayout(width, ViewGroup.LayoutParams.WRAP_CONTENT)

        val tvTitle = dialog.findViewById<TextView>(R.id.tvBannedTitle)
        val tvMessage = dialog.findViewById<TextView>(R.id.tvBannedMessage)
        val tvDetail = dialog.findViewById<TextView>(R.id.tvBannedDetail)
        val btnAppeal = dialog.findViewById<MaterialButton>(R.id.btnBannedAppeal)
        val btnAction = dialog.findViewById<MaterialButton>(R.id.btnBannedAction)

        tvTitle.text = "⚠️ Cuenta Suspendida"

        if (isChatBan) {
            tvMessage.text = "Tu cuenta ha sido suspendida permanentemente por violar las normas de seguridad y convivencia de Animoon.\n\nTu sesión activa ha sido cerrada."
            btnAction.text = "Volver al inicio"
        } else {
            tvMessage.text = "Tu cuenta ha sido suspendida permanentemente por violar las normas de seguridad y convivencia de Animoon.\n\nNo es posible iniciar sesión."
            btnAction.text = "Entendido"
        }

        if (!motivo.isNullOrBlank()) {
            tvDetail.visibility = View.VISIBLE
            val cleanMotivo = motivo.replace("CUENTA_BANEADA:", "").trim()
            tvDetail.text = "Detalle: $cleanMotivo"
        } else {
            tvDetail.visibility = View.GONE
        }

        // Botón de Apelación
        btnAppeal.setOnClickListener {
            Toast.makeText(
                activity,
                "El sistema de apelaciones se encuentra actualmente en desarrollo y estará disponible próximamente.",
                Toast.LENGTH_LONG
            ).show()
        }

        // Botón de Acción Principal (Volver al inicio o Entendido)
        btnAction.setOnClickListener {
            dialog.dismiss()

            if (isChatBan) {
                // Matar tokens locales y cerrar WebSockets
                TokenManager.clearToken()
                ChatWebSocketManager.disconnect()
                com.example.animoon.data.network.WebSocketManager.disconnect()

                // Redirigir a la pantalla principal / Splash limpiando toda la pila de Activities
                val intent = Intent(activity, SplashActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                }
                activity.startActivity(intent)
                activity.finish()
            } else {
                onDismissAction?.invoke()
            }
        }

        try {
            dialog.show()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
