import re

with open('backend/chat/chat_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s*# Mensaje de bienvenida.*?\}\)\)', '', content, flags=re.DOTALL)

with open('backend/chat/chat_server.py', 'w', encoding='utf-8') as f:
    f.write(content)
