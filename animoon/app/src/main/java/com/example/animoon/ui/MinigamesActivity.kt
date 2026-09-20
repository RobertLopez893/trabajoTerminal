package com.example.animoon.ui.minigame

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity

class MinigamesActivity : BaseActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_minigames)


        // =====================================================
        // REFERENCIAS
        // =====================================================

        val btnBack =
            findViewById<TextView>(R.id.btnBackMinigames)

        val btnGame1 =
            findViewById<Button>(R.id.btnGame1)


        // =====================================================
        // REGRESAR AL LOBBY
        // =====================================================

        btnBack.setOnClickListener {

            finish()
        }


        // =====================================================
        // MINIJUEGO 1
        // =====================================================

        btnGame1.setOnClickListener {

            val intent =
                Intent(
                    this,
                    Game1CinematicActivity::class.java
                )

            startActivity(intent)
        }
    }
}