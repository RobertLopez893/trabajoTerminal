package com.example.animoon.ui.chat

import android.os.Bundle
import android.view.inputmethod.EditorInfo
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.network.ChatWebSocketManager
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.util.UUID

class ChatActivity : BaseActivity() {

    private val adapter = ChatAdapter()
    private lateinit var rvMessages: RecyclerView
    private lateinit var etMessage: TextInputEditText

    private val avatarPropio = R.drawable.avatar_cat_blue
    private val avatarOtro = R.drawable.avatar_fox_orange

    // Generamos un ID de usuario temporal para esta sesin y usamos un chat global
    private val myUserId = UUID.randomUUID().toString()
    private val currentChatId = "sala_global_1"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        rvMessages = findViewById(R.id.rvChatMessages)
        etMessage = findViewById(R.id.etChatMessage)

        findViewById<MaterialButton>(R.id.btnChatBack).setOnClickListener { finish() }
        findViewById<MaterialButton>(R.id.btnChatSend).setOnClickListener { enviarMensaje() }

        rvMessages.layoutManager = LinearLayoutManager(this).apply { stackFromEnd = true }
        rvMessages.adapter = adapter

        etMessage.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEND) {
                enviarMensaje()
                true
            } else {
                false
            }
        }

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.chatContent)) { v, insets ->
            val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
            v.setPadding(v.paddingLeft, v.paddingTop, v.paddingRight, ime.bottom)
            insets
        }

        // Conectar WebSocket
        ChatWebSocketManager.connect(currentChatId, myUserId)

        // Escuchar mensajes entrantes
        lifecycleScope.launch {
            ChatWebSocketManager.messages.collectLatest { msg ->
                runOnUiThread {
                    if (msg.isSystem) {
                        agregarMensaje(ChatItem(msg.text, esMio = false, avatarRes = R.drawable.ic_hud_settings)) // Avatar de sistema
                    } else if (!msg.isMine) {
                        recibirMensaje(msg.text)
                    }
                }
            }
        }
    }

    private fun enviarMensaje() {
        val texto = etMessage.text?.toString()?.trim().orEmpty()
        if (texto.isEmpty()) return

        // Mostramos nuestro mensaje en la UI
        agregarMensaje(ChatItem(texto, esMio = true, avatarRes = avatarPropio))
        etMessage.text?.clear()

        // Enviamos al backend por WebSocket usando AES-GCM
        ChatWebSocketManager.sendMessage(texto)
    }

    private fun recibirMensaje(texto: String) {
        agregarMensaje(ChatItem(texto, esMio = false, avatarRes = avatarOtro))
    }

    private fun agregarMensaje(item: ChatItem) {
        adapter.agregar(item)
        rvMessages.scrollToPosition(adapter.itemCount - 1)
    }

    override fun onDestroy() {
        super.onDestroy()
        ChatWebSocketManager.disconnect()
    }
}