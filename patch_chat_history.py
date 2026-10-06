import re

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure AESGCMCipher is imported
if "import com.example.animoon.security.AESGCMCipher" not in content:
    content = content.replace("import android.widget.TextView", "import android.widget.TextView\nimport com.example.animoon.security.AESGCMCipher")

old_connect = """            withContext(Dispatchers.Main) {
                // Conectar WebSocket después de configurar
                ChatWebSocketManager.connect(currentChatId, myUserId, targetUserId)
            }"""

new_connect = """            withContext(Dispatchers.Main) {
                // Conectar WebSocket despues de configurar
                ChatWebSocketManager.connect(currentChatId, myUserId, targetUserId)
            }
            
            // Cargar historial
            try {
                val historyRes = ApiClient.chatService.getChatHistory(currentChatId)
                if (historyRes.isSuccessful && historyRes.body() != null) {
                    val history = historyRes.body()!!
                    val items = history.mapNotNull { msg ->
                        try {
                            val text = AESGCMCipher.decrypt(msg.contenido_cifrado_aes_gcm, msg.iv_nonce, msg.aes_gcm_tag)
                            val esMio = (msg.emisor_usuario_id == myUserId)
                            val avatarRes = if (esMio) avatarPropio else avatarOtro
                            ChatItem(text, esMio, avatarRes)
                        } catch (e: Exception) {
                            null
                        }
                    }
                    withContext(Dispatchers.Main) {
                        items.forEach { adapter.agregar(it) }
                        if (items.isNotEmpty()) {
                            rvMessages.scrollToPosition(items.size - 1)
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }"""

# Fallback regex if exact string is broken by line endings
content = re.sub(r'            withContext\(Dispatchers\.Main\) \{\s*// Conectar WebSocket desp.*?ChatWebSocketManager\.connect\(currentChatId, myUserId, targetUserId\)\s*\}', new_connect, content, flags=re.DOTALL)

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
