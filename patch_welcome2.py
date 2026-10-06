import re

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

old_history = r'withContext\(Dispatchers\.Main\)\s*\{\s*if \(items\.isEmpty\(\)\) \{\s*adapter\.agregar\(ChatItem\("Bienvenido al chat seguro de Animoon\. ¡Diviértete con cuidado!", false, com\.example\.animoon\.R\.drawable\.ic_hud_settings\)\)\s*\} else \{\s*items\.forEach \{ adapter\.agregar\(it\) \}\s*rvMessages\.scrollToPosition\(items\.size - 1\)\s*\}\s*\}'
new_history = """withContext(Dispatchers.Main) {
                        adapter.agregar(ChatItem("Bienvenido al chat seguro de Animoon. ¡Diviértete con cuidado!", false, com.example.animoon.R.drawable.ic_hud_settings))
                        items.forEach { adapter.agregar(it) }
                        if (items.isNotEmpty()) {
                            rvMessages.scrollToPosition(items.size)
                        }
                    }"""

content = re.sub(old_history, new_history, content)

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
