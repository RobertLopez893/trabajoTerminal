package com.example.animoon.ui.splash

import android.content.Intent
import android.os.Bundle
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.R
import com.example.animoon.ui.auth.LoginActivity

class SplashActivity : BaseActivity() {
    override val observarSesionExpirada: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_splash)

        val btnStart = findViewById<android.widget.Button>(R.id.btnStart)

        com.example.animoon.data.network.TokenManager.init(applicationContext)

        btnStart.setOnClickListener {
            val token = com.example.animoon.data.network.TokenManager.getToken()
            if (token.isNullOrEmpty()) {
                val intent = Intent(this, LoginActivity::class.java)
                startActivity(intent)
                finish()
            } else {
                val intent = Intent(this, com.example.animoon.MainActivity::class.java)
                startActivity(intent)
                finish()
            }
        }
    }
}