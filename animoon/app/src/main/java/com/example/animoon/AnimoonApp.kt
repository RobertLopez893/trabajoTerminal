package com.example.animoon

import android.app.Application
import com.example.animoon.data.network.TokenManager

class AnimoonApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Inicializamos el TokenManager con el contexto global
        TokenManager.init(this)
    }
}
