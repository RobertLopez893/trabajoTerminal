import re

with open('animoon/app/src/main/java/com/example/animoon/ui/profile/ProfileActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """                        chatButton.setOnClickListener {
                            val chatIntent = Intent(this@ProfileActivity, com.example.animoon.ui.chat.ChatActivity::class.java)
                            startActivity(chatIntent)
                        }"""
new_logic = """                        chatButton.setOnClickListener {
                            val chatIntent = Intent(this@ProfileActivity, com.example.animoon.ui.chat.ChatActivity::class.java).apply {
                                putExtra("EXTRA_TARGET_ID", profile.id)
                                putExtra("EXTRA_TARGET_NICKNAME", profile.nickname)
                                putExtra("EXTRA_TARGET_SPECIES", profile.species)
                                putExtra("EXTRA_TARGET_COLOR", profile.color)
                            }
                            startActivity(chatIntent)
                        }"""

content = content.replace(old_logic, new_logic)

with open('animoon/app/src/main/java/com/example/animoon/ui/profile/ProfileActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
