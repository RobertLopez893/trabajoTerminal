import re

with open('backend/chat/chat_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def save_message_to_db(chat_id: str, sender_id: str, enc_data: dict, orden: int = 1):',
    'def save_message_to_db(chat_id: str, sender_id: str, enc_data: dict, orden: int = 1, target_id: str = None):'
)

old_logic = """        # Verificar si el chat existe
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
                db.commit()"""

new_logic = """        # Verificar si el chat existe
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat and target_id:
            nuevo_chat = Chat(
                id=chat_id,
                usuario_a_id=sender_id,
                usuario_b_id=target_id
            )
            db.add(nuevo_chat)
            db.commit()"""

content = content.replace(old_logic, new_logic)

content = content.replace(
    'target_id = data.get("target_id")',
    '' # We will extract it cleanly
)

content = content.replace(
    'sender_id = data.get("sender_id", "Usuario_Desconocido")',
    'sender_id = data.get("sender_id", "Usuario_Desconocido")\n                target_id = data.get("target_id")'
)

content = content.replace(
    'await asyncio.to_thread(save_message_to_db, chat_id, sender_id, enc_data)',
    'await asyncio.to_thread(save_message_to_db, chat_id, sender_id, enc_data, 1, target_id)'
)

with open('backend/chat/chat_server.py', 'w', encoding='utf-8') as f:
    f.write(content)
