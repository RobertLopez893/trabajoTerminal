with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("estn cifrados. Adems,", "están cifrados. Además,")

with open('animoon/app/src/main/java/com/example/animoon/ui/chat/ChatActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
