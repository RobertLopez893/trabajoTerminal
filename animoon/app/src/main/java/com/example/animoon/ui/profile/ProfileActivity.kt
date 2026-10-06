package com.example.animoon.ui.profile

import android.content.Context
import android.content.Intent
import android.os.Bundle
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
                    DemoProfileSource.myProfile.id
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

        val userId =
            intent.getStringExtra(EXTRA_USER_ID)

        val profile =
            userId?.let { DemoProfileSource.findProfile(it) }

        if (profile == null) {
            profileCard.visibility = View.GONE
            errorText.visibility = View.VISIBLE
            return
        }

        val isOwnProfile =
            DemoProfileSource.isMyProfile(profile.id)

        titleText.text =
            if (isOwnProfile) {
                "Mi perfil"
            } else {
                "Perfil de jugador"
            }

        nicknameText.text = profile.nickname

        val avatarDrawable =
            AvatarDrawableResolver.resolve(
                species = profile.species,
                color = profile.color
            )

        if (avatarDrawable != null) {
            avatarImage.setImageResource(avatarDrawable)
            avatarImage.contentDescription =
                "Avatar de ${profile.nickname}"

            avatarImage.visibility = View.VISIBLE
            avatarUnavailable.visibility = View.GONE
        } else {
            avatarImage.visibility = View.GONE
            avatarUnavailable.visibility = View.VISIBLE
        }

        chatButton.visibility =
            if (isOwnProfile) View.GONE else View.VISIBLE

        chatButton.setOnClickListener {
            val intent = Intent(this, com.example.animoon.ui.chat.ChatActivity::class.java)
            startActivity(intent)
        }

        errorText.visibility = View.GONE
        profileCard.visibility = View.VISIBLE
    }
}
