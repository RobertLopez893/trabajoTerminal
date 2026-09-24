package com.example.animoon.ui.minigame

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.minigame.game1.Game1CinematicActivity
import com.example.animoon.ui.minigame.game2.Game2Activity
import com.google.android.material.button.MaterialButton
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

        val btnGame2 =
            findViewById<MaterialButton>(R.id.btnGame2)


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


        // =====================================================
        // MINIJUEGO 2
        // =====================================================

        btnGame2.setOnClickListener {

            val intent =
                Intent(
                    this,
                    Game2Activity::class.java
                )

            startActivity(intent)
        }
    }
}