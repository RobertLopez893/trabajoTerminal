with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

import re
old_history = r'withContext\(Dispatchers\.Main\)\s*\{\s*items\.forEach \{ adapter\.agregar\(it\) \}\s*if \(items\.isNotEmpty\(\)\) \{\s*rvMessages\.scrollToPosition\(items\.size - 1\)\s*\}\s*\}'
new_history = """withContext(Dispatchers.Main) {
                        if (items.isEmpty()) {
                            adapter.agregar(ChatItem("Bienvenido al chat seguro de Animoon. ¡Diviértete con cuidado!", false, com.example.animoon.R.drawable.ic_hud_settings))
                        } else {
                            items.forEach { adapter.agregar(it) }
                            rvMessages.scrollToPosition(items.size - 1)
                        }
                    }"""

content = re.sub(old_history, new_history, content)

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
