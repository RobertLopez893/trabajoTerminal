package com.example.animoon.ui.common

import android.app.Activity
import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.view.ViewGroup
import android.view.Window
import com.example.animoon.R
import com.google.android.material.button.MaterialButton

object VersionNotesDialog {

    fun show(activity: Activity) {
        if (activity.isFinishing || activity.isDestroyed) return

        val dialog = Dialog(activity)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_version_notes)
        dialog.setCancelable(true)
        dialog.setCanceledOnTouchOutside(true)

        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        val metrics = activity.resources.displayMetrics
        val width = (metrics.widthPixels * 0.85).toInt().coerceAtMost((650 * metrics.density).toInt())
        val height = (metrics.heightPixels * 0.88).toInt()
        dialog.window?.setLayout(width, height)

        val btnClose = dialog.findViewById<MaterialButton>(R.id.btnVersionClose)
        btnClose?.setOnClickListener {
            dialog.dismiss()
        }

        dialog.show()
    }
}
