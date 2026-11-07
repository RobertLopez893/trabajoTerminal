package com.example.animoon.ui.common

import android.app.Activity
import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.view.ViewGroup
import android.view.Window
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.R
import com.google.android.material.button.MaterialButton

object SafeExitDialog {

    /**
     * Muestra el diálogo de salida segura preventiva para la víctima con el estilo visual
     * de Animoon, la imagen amigable de Moonie y un mensaje adaptado para niños (sin detalles técnicos).
     *
     * @param activity Actividad que invoca el diálogo (ChatActivity).
     * @param title Título amigable opcional (por defecto: 🛡️ ¡Cuidamos de ti!).
     * @param message Mensaje protector opcional adaptado a niños.
     * @param onDismissAction Callback ejecutado al presionar el botón de confirmación para salir.
     */
    fun show(
        activity: Activity,
        title: String? = null,
        message: String? = null,
        onDismissAction: (() -> Unit)? = null
    ) {
        if (activity.isFinishing || activity.isDestroyed) return

        val dialog = Dialog(activity)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_safe_exit)
        dialog.setCancelable(false)
        dialog.setCanceledOnTouchOutside(false)

        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        val width = (activity.resources.displayMetrics.widthPixels * 0.90).toInt()
        dialog.window?.setLayout(width, ViewGroup.LayoutParams.WRAP_CONTENT)

        val tvTitle = dialog.findViewById<TextView>(R.id.tvSafeExitTitle)
        val tvMessage = dialog.findViewById<TextView>(R.id.tvSafeExitMessage)
        val btnAction = dialog.findViewById<MaterialButton>(R.id.btnSafeExitAction)

        if (!title.isNullOrBlank()) {
            tvTitle.text = title
        }

        if (!message.isNullOrBlank()) {
            tvMessage.text = message
        }

        btnAction.setOnClickListener {
            dialog.dismiss()
            onDismissAction?.invoke()
        }

        dialog.show()
    }
}
