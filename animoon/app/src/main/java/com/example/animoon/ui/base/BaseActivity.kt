package com.example.animoon.ui.base

import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.view.LayoutInflater
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.data.network.TokenManager
import com.example.animoon.ui.auth.LoginActivity
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

open class BaseActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        lifecycleScope.launch {
            TokenManager.sessionExpiredFlow.collect {
                showSessionExpiredDialog()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // No need to unregister flow manually, lifecycleScope handles it
    }

    private var sessionDialog: AlertDialog? = null

    private fun showSessionExpiredDialog() {
        if (isFinishing || isDestroyed || (sessionDialog?.isShowing == true)) {
            return
        }

        val view = LayoutInflater.from(this).inflate(R.layout.dialog_session_expired, null)
        val builder = AlertDialog.Builder(this)
        builder.setView(view)
        builder.setCancelable(false)
        
        try {
            sessionDialog = builder.create()
            sessionDialog?.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

            view.findViewById<MaterialButton>(R.id.btnReconnect).setOnClickListener {
                sessionDialog?.dismiss()
                TokenManager.clearToken()
                val loginIntent = Intent(this, LoginActivity::class.java)
                loginIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(loginIntent)
                finish()
            }

            sessionDialog?.show()
        } catch (e: Exception) {
            // Si la Activity se está cerrando y el diálogo truena (BadTokenException),
            // simplemente cerramos la sesión y lo mandamos al Login de forma segura.
            TokenManager.clearToken()
            val loginIntent = Intent(this, LoginActivity::class.java)
            loginIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(loginIntent)
            finish()
        }
    }
}