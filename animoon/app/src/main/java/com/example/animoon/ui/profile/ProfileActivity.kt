package com.example.animoon.ui.profile

import android.content.Context
import android.content.Intent
import android.os.Bundle
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager

import android.view.View
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class ProfileActivity : BaseActivity() {

    companion object {
        private const val EXTRA_USER_ID = "profile_user_id"

        fun myProfileIntent(context: Context): Intent {
            return Intent(context, ProfileActivity::class.java)
                .putExtra(
                    EXTRA_USER_ID,
                    "me"
                )
        }

        fun playerProfileIntent(
            context: Context,
            userId: String
        ): Intent {
            return Intent(context, ProfileActivity::class.java)
                .putExtra(EXTRA_USER_ID, userId)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        val backButton =
            findViewById<MaterialButton>(R.id.btnProfileBack)

        val titleText =
            findViewById<TextView>(R.id.txtProfileTitle)

        val nicknameText =
            findViewById<TextView>(R.id.txtProfileNickname)

        val avatarImage =
            findViewById<ImageView>(R.id.imgProfileAvatar)

        val avatarUnavailable =
            findViewById<TextView>(
                R.id.txtProfileAvatarUnavailable
            )

        val profileCard =
            findViewById<View>(R.id.cardProfile)

        val errorText =
            findViewById<TextView>(R.id.txtProfileError)

        val chatButton =
            findViewById<MaterialButton>(R.id.btnProfileChat)

        backButton.setOnClickListener {
            finish()
        }

        val userId = intent.getStringExtra(EXTRA_USER_ID) ?: return

        // Hide initially
        profileCard.visibility = View.GONE
        errorText.visibility = View.GONE
        
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = ApiClient.authService.getProfile(userId)
                
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val profile = response.body()!!
                        // Asumimos que si userId es "me", es propio, 
                        // de lo contrario deberiamos tener el ID real guardado en TokenManager.
                        // Para esto usaremos si el EXTRA_USER_ID era "me" (o puedes ajustar luego)
                                                val token = com.example.animoon.data.network.TokenManager.getToken()
                        var myId = "me"
                        if (!token.isNullOrEmpty()) {
                            try {
                                val parts = token.split(".")
                                if (parts.size >= 2) {
                                    val tokenPayload = String(android.util.Base64.decode(parts[1], android.util.Base64.URL_SAFE))
                                    val json = org.json.JSONObject(tokenPayload)
                                    myId = json.getString("sub")
                                }
                            } catch (e: Exception) {}
                        }
                        val isOwnProfile = (userId == "me" || userId == myId)
                        
                        titleText.text = if (isOwnProfile) "Mi perfil" else "Perfil de jugador"
                        nicknameText.text = profile.nickname
                        
                        val avatarDrawable = AvatarDrawableResolver.resolve(profile.species, profile.color)
                        
                        if (avatarDrawable != null) {
                            avatarImage.setImageResource(avatarDrawable)
                            avatarImage.contentDescription = "Avatar de ${profile.nickname}"
                            avatarImage.visibility = View.VISIBLE
                            avatarUnavailable.visibility = View.GONE
                        } else {
                            avatarImage.visibility = View.GONE
                            avatarUnavailable.visibility = View.VISIBLE
                        }
                        
                        chatButton.visibility = if (isOwnProfile) View.GONE else View.VISIBLE
                        
                        chatButton.setOnClickListener {
                            val chatIntent = Intent(this@ProfileActivity, com.example.animoon.ui.chat.ChatActivity::class.java).apply {
                                putExtra("EXTRA_TARGET_ID", profile.id)
                                putExtra("EXTRA_TARGET_NICKNAME", profile.nickname)
                                putExtra("EXTRA_TARGET_SPECIES", profile.species)
                                putExtra("EXTRA_TARGET_COLOR", profile.color)
                            }
                            startActivity(chatIntent)
                        }
                        
                        profileCard.visibility = View.VISIBLE
                    } else {
                        errorText.visibility = View.VISIBLE
                        errorText.text = "Error al cargar perfil"
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    errorText.visibility = View.VISIBLE
                    errorText.text = "Error de conexión"
                }
            }
        }
    }
}

