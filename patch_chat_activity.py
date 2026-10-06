import re

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
imports = """import android.widget.TextView
import android.util.Base64
import org.json.JSONObject
import com.example.animoon.data.network.TokenManager
import com.example.animoon.ui.profile.AvatarDrawableResolver
import com.example.animoon.data.network.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
"""
if "import android.widget.TextView" not in content:
    content = content.replace("import android.os.Bundle", "import android.os.Bundle\n" + imports)

# We will completely replace ChatActivity's logic
new_class = """class ChatActivity : BaseActivity() {

    private val adapter = ChatAdapter()
    private lateinit var rvMessages: RecyclerView
    private lateinit var etMessage: TextInputEditText
    private lateinit var txtTitle: TextView

    private var avatarPropio = R.drawable.avatar_cat_blue
    private var avatarOtro = R.drawable.avatar_fox_orange

    private var myUserId = ""
    private var targetUserId = ""
    private var currentChatId = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        rvMessages = findViewById(R.id.rvChatMessages)
        etMessage = findViewById(R.id.etChatMessage)
        txtTitle = findViewById(R.id.txtChatTitle)

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

        targetUserId = intent.getStringExtra("EXTRA_TARGET_ID") ?: ""
        val targetNickname = intent.getStringExtra("EXTRA_TARGET_NICKNAME") ?: "Usuario"
        val targetSpecies = intent.getStringExtra("EXTRA_TARGET_SPECIES") ?: "gato"
        val targetColor = intent.getStringExtra("EXTRA_TARGET_COLOR") ?: "azul"
        
        txtTitle.text = "Chat con $targetNickname"
        avatarOtro = AvatarDrawableResolver.resolve(targetSpecies, targetColor) ?: R.drawable.avatar_fox_orange

        // Decodificar JWT para sacar myUserId
        val token = TokenManager.getToken()
        if (token != null) {
            try {
                val split = token.split(".")
                if (split.size > 1) {
                    val payload = String(Base64.decode(split[1], Base64.URL_SAFE))
                    val json = JSONObject(payload)
                    myUserId = json.getString("sub")
                }
            } catch (e: Exception) {
                myUserId = UUID.randomUUID().toString()
            }
        }

        // Crear un chat_id unívoco ordenando los IDs
        val ids = listOf(myUserId, targetUserId).sorted()
        currentChatId = "chat_${ids[0]}_${ids[1]}"

        // Fetch mi perfil para mi avatar
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val res = ApiClient.authService.getProfile("me")
                if (res.isSuccessful && res.body() != null) {
                    val p = res.body()!!
                    val myDrawable = AvatarDrawableResolver.resolve(p.species, p.color)
                    if (myDrawable != null) {
                        avatarPropio = myDrawable
                    }
                }
            } catch (e: Exception) {}
            
            withContext(Dispatchers.Main) {
                // Conectar WebSocket después de configurar
                ChatWebSocketManager.connect(currentChatId, myUserId)
            }
        }

        // Escuchar mensajes entrantes
        lifecycleScope.launch {
            ChatWebSocketManager.messages.collectLatest { msg ->
                runOnUiThread {
                    if (msg.isSystem) {
                        agregarMensaje(ChatItem(msg.text, esMio = false, avatarRes = R.drawable.ic_hud_settings))
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
"""

content = re.sub(r'class ChatActivity : BaseActivity\(\) \{.*\}', new_class, content, flags=re.DOTALL)

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
