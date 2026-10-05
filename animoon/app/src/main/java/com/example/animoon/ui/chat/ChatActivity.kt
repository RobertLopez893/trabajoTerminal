package com.example.animoon.ui.chat

import android.os.Bundle
import android.view.inputmethod.EditorInfo
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class ChatActivity : BaseActivity() {

    private val adapter = ChatAdapter()
    private lateinit var rvMessages: RecyclerView
    private lateinit var etMessage: TextInputEditText

    // TODO: reemplazar por el avatar real del jugador (AvatarDrawableResolver)
    private val avatarPropio = R.drawable.avatar_cat_blue
    private val avatarOtro = R.drawable.avatar_fox_orange

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

        // Con modo inmersivo el teclado no redimensiona solo: subimos el contenido
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.chatContent)) { v, insets ->
            val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
            v.setPadding(v.paddingLeft, v.paddingTop, v.paddingRight, ime.bottom)
            insets
        }

        cargarMensajesDemo()
    }

    private fun enviarMensaje() {
        val texto = etMessage.text?.toString()?.trim().orEmpty()
        if (texto.isEmpty()) return

        agregarMensaje(ChatItem(texto, esMio = true, avatarRes = avatarPropio))
        etMessage.text?.clear()

        // TODO(backend): enviar por el WebSocket del chat (/ws/chat/) cuando
        // el backend defina el formato de los mensajes (AES-GCM pendiente)
    }

    /** Se llamará cuando llegue un mensaje de otro jugador. */
    private fun recibirMensaje(texto: String) {
        agregarMensaje(ChatItem(texto, esMio = false, avatarRes = avatarOtro))
    }

    private fun agregarMensaje(item: ChatItem) {
        adapter.agregar(item)
        rvMessages.scrollToPosition(adapter.itemCount - 1)
    }

    // TODO: borrar cuando el chat esté conectado al backend
    private fun cargarMensajesDemo() {
        recibirMensaje("¡Hola! ¿Jugamos un rato?")
        agregarMensaje(ChatItem("¡Sí! ¿A qué minijuego?", esMio = true, avatarRes = avatarPropio))
    }
}