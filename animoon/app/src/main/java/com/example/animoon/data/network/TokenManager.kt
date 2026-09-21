package com.example.animoon.data.network

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.flow.MutableSharedFlow

object TokenManager {
    private const val PREFS_NAME = "animoon_prefs"
    private const val KEY_TOKEN = "jwt_token"
    private lateinit var prefs: SharedPreferences
    private var appContext: Context? = null

    // Flujo reactivo moderno para reemplazar LocalBroadcastManager
    val sessionExpiredFlow = MutableSharedFlow<Unit>(extraBufferCapacity = 1)

    fun init(context: Context) {
        appContext = context.applicationContext
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }
    
    fun getContext(): Context? {
        return appContext
    }

    fun saveToken(token: String) {
        prefs.edit().putString(KEY_TOKEN, token).apply()
    }

    fun getToken(): String? {
        return prefs.getString(KEY_TOKEN, null)
    }

    fun saveSessionSecret(secretB64: String) {
        prefs.edit().putString("aes_session_secret", secretB64).apply()
    }

    fun getSessionSecret(): String? {
        return prefs.getString("aes_session_secret", null)
    }

    fun clearToken() {
        prefs.edit().remove(KEY_TOKEN).remove("aes_session_secret").apply()
    }
}
