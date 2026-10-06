import re

with open('backend/chat/chat_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """    db = SessionLocal()
    try:
        # Verificar si el chat existe (opcional, pero recomendado para evitar errores de FK)
        # chat = db.query(Chat).filter(Chat.id == chat_id).first()
        # Si no existe, podría lanzar error de llave foránea según la BD.

        nuevo_mensaje = Mensaje("""

new_logic = """    db = SessionLocal()
    try:
        # Verificar si el chat existe
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            partes = chat_id.split('_')
            if len(partes) == 3:
                nuevo_chat = Chat(
                    id=chat_id,
                    usuario_a_id=partes[1],
                    usuario_b_id=partes[2]
                )
                db.add(nuevo_chat)
                db.commit()

        nuevo_mensaje = Mensaje("""

# Also handles \r\n vs \n issues
import sys
content_normalized = content.replace('\r\n', '\n')
old_logic_normalized = old_logic.replace('\r\n', '\n')
new_logic_normalized = new_logic.replace('\r\n', '\n')

content_normalized = content_normalized.replace(old_logic_normalized, new_logic_normalized)

# Import Chat if not imported
if "from database.models import" not in content_normalized and "from backend.database.models import" not in content_normalized:
    content_normalized = content_normalized.replace("from backend.database.database import SessionLocal", "from backend.database.database import SessionLocal\nfrom backend.database.models import Chat, Mensaje")
    content_normalized = content_normalized.replace("from database.database import SessionLocal", "from database.database import SessionLocal\nfrom backend.database.models import Chat, Mensaje")

with open('backend/chat/chat_server.py', 'w', encoding='utf-8') as f:
    f.write(content_normalized)
