import re

with open('backend/api/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoint = """
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Mensaje
from pydantic import BaseModel
from typing import List

class MensajeResponse(BaseModel):
    id: str
    chat_id: str
    emisor_usuario_id: str
    contenido_cifrado_aes_gcm: str
    iv_nonce: str
    aes_gcm_tag: str
    orden_global: int

    class Config:
        from_attributes = True

@router.get("/history/{chat_id}", response_model=List[MensajeResponse])
def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    mensajes = db.query(Mensaje).filter(Mensaje.chat_id == chat_id).order_by(Mensaje.sent_at.asc()).all()
    return mensajes
"""

if "@router.get(\"/history/{chat_id}\"" not in content:
    content += new_endpoint

with open('backend/api/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
