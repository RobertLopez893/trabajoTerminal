package com.example.animoon.ui.parents

import android.view.KeyEvent
import android.view.MotionEvent
import android.view.Window
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.dialog.MaterialAlertDialogBuilder

object ParentGuidanceDialog {

    fun create(
        activity: AppCompatActivity,
        title: String,
        message: String,
        onInteraction: () -> Boolean
    ): AlertDialog {

        val dialog = MaterialAlertDialogBuilder(activity)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("Entendido") { _, _ ->
                onInteraction()
            }
            .create()

        dialog.setOnShowListener {
            val dialogWindow = dialog.window
                ?: return@setOnShowListener

            val originalCallback = dialogWindow.callback
                ?: return@setOnShowListener

            dialogWindow.callback =
                object : Window.Callback by originalCallback {

                    override fun dispatchTouchEvent(
                        event: MotionEvent
                    ): Boolean {
                        val isInteraction =
                            event.actionMasked == MotionEvent.ACTION_DOWN ||
                                    event.actionMasked == MotionEvent.ACTION_MOVE

                        if (isInteraction && !onInteraction()) {
                            return true
                        }

                        return originalCallback.dispatchTouchEvent(event)
                    }

                    override fun dispatchKeyEvent(
                        event: KeyEvent
                    ): Boolean {
                        if (
                            event.action == KeyEvent.ACTION_DOWN &&
                            !onInteraction()
                        ) {
                            return true
                        }

                        return originalCallback.dispatchKeyEvent(event)
                    }
                }
        }

        return dialog
    }
}