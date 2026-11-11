package com.example.animoon.ui.common

import android.app.Activity
import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.view.ViewGroup
import android.view.Window
import android.widget.ImageView
import android.widget.TextView
import com.example.animoon.R
import com.example.animoon.data.network.ChatInvitation
import com.example.animoon.ui.profile.AvatarDrawableResolver
import com.google.android.material.button.MaterialButton

object ChatInvitationDialog {

    fun show(
        activity: Activity,
        invitation: ChatInvitation,
        onAccept: () -> Unit,
        onReject: (() -> Unit)? = null
    ): Dialog? {
        if (activity.isFinishing || activity.isDestroyed) return null

        val dialog = Dialog(activity)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_chat_invitation)
        dialog.setCancelable(true)
        dialog.setCanceledOnTouchOutside(false)

        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        val width = (activity.resources.displayMetrics.widthPixels * 0.90).toInt()
        dialog.window?.setLayout(width, ViewGroup.LayoutParams.WRAP_CONTENT)

        val imgAvatar = dialog.findViewById<ImageView>(R.id.imgInviteAvatar)
        val tvTitle = dialog.findViewById<TextView>(R.id.tvInviteTitle)
        val tvMessage = dialog.findViewById<TextView>(R.id.tvInviteMessage)
        val btnReject = dialog.findViewById<MaterialButton>(R.id.btnRejectChat)
        val btnAccept = dialog.findViewById<MaterialButton>(R.id.btnAcceptChat)

        val avatarRes = AvatarDrawableResolver.resolve(invitation.fromSpecies, invitation.fromColor)
            ?: R.drawable.avatar_fox_orange
        imgAvatar.setImageResource(avatarRes)

        tvTitle.text = "💬 ¡Mensaje de ${invitation.fromNickname}!"
        tvMessage.text = "${invitation.fromNickname} te ha enviado un mensaje y te invita a platicar en la sala de chat segura."

        btnReject.setOnClickListener {
            dialog.dismiss()
            onReject?.invoke()
        }

        btnAccept.setOnClickListener {
            dialog.dismiss()
            onAccept()
        }

        dialog.show()
        return dialog
    }
}
