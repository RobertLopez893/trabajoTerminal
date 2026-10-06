import re

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'Bienvenido al chat seguro de Animoon\. [^"]*', 'Bienvenido al chat seguro de Animoon. Diviertete con cuidado.', content)

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
