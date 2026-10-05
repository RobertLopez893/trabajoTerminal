package com.example.animoon.ui.chat

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.animoon.R

class ChatAdapter : RecyclerView.Adapter<ChatAdapter.ChatViewHolder>() {

    private val items = mutableListOf<ChatItem>()

    fun agregar(item: ChatItem) {
        items.add(item)
        notifyItemInserted(items.lastIndex)
    }

    override fun getItemViewType(position: Int): Int =
        if (items[position].esMio) TIPO_ENVIADO else TIPO_RECIBIDO

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChatViewHolder {
        val layout =
            if (viewType == TIPO_ENVIADO) R.layout.item_chat_sent
            else R.layout.item_chat_received

        val view = LayoutInflater.from(parent.context).inflate(layout, parent, false)
        return ChatViewHolder(view)
    }

    override fun onBindViewHolder(holder: ChatViewHolder, position: Int) {
        val item = items[position]
        holder.texto.text = item.texto
        holder.avatar.setImageResource(item.avatarRes)
    }

    override fun getItemCount(): Int = items.size

    class ChatViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val texto: TextView = view.findViewById(R.id.txtChatMessage)
        val avatar: ImageView = view.findViewById(R.id.imgChatAvatar)
    }

    companion object {
        private const val TIPO_RECIBIDO = 0
        private const val TIPO_ENVIADO = 1
    }
}