import asyncio
import json
import os
import ssl
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ChatServer")

import uuid
import websockets
from datetime import datetime

# Agregar la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal
from backend.database.models import Mensaje, Chat

# Diccionario para agrupar conexiones por chat_id: { "chat_id": set(websocket1, websocket2) }
chat_rooms = {}
aes_cipher = AESGCMCipher()

def save_message_to_db(chat_id: str, sender_id: str, enc_data: dict, orden: int = 1):
    """
    Guarda el mensaje cifrado en la base de datos de forma síncrona.
    Será ejecutado dentro de asyncio.to_thread para no bloquear el servidor.
    """
    db = SessionLocal()
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

        nuevo_mensaje = Mensaje(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            emisor_usuario_id=sender_id,
            contenido_cifrado_aes_gcm=enc_data.get('ciphertext_b64'),
            iv_nonce=enc_data.get('nonce_b64'),
            aes_gcm_tag=enc_data.get('tag_b64'),
            orden_global=orden  # Ojo: Aquí iría la lógica de acumulación en el futuro
        )
        db.add(nuevo_mensaje)
        db.commit()
        logger.info(f"[DB] Mensaje guardado en base de datos. ID: {nuevo_mensaje.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"[DB ERROR] Error al guardar mensaje: {e}")
    finally:
        db.close()

async def broadcast_to_room(chat_id, message_dict, sender_ws):
    """
    Envía un mensaje a todos los clientes conectados en un chat_id específico.
    """
    if chat_id in chat_rooms:
        room_clients = chat_rooms[chat_id]
        payload = json.dumps(message_dict)
        await asyncio.gather(
            *[client.send(payload) for client in room_clients if client != sender_ws],
            return_exceptions=True
        )

async def handle_client(websocket):
    """
    Maneja el ciclo de vida de la conexión de un cliente en el chat.
    """
    client_address = websocket.remote_address
    logger.info(f"\n[+] Nueva conexión establecida desde {client_address[0]}:{client_address[1]}")
    
    current_chat_id = None

    try:
        # Mensaje de bienvenida
        welcome_text = "Bienvenido al chat seguro de Animoon (Doble Cifrado y Persistencia Activa)."
        encrypted_welcome = aes_cipher.encrypt(welcome_text)
        await websocket.send(json.dumps({
            "sender_id": "System",
            "encrypted_message": encrypted_welcome,
            "system": True
        }))

        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                
                # Ahora requerimos chat_id y sender_id para poder guardar en DB
                chat_id = data.get("chat_id")
                sender_id = data.get("sender_id", "Usuario_Desconocido")
                enc_data = data.get("encrypted_message")
                
                if not chat_id or not sender_id or not enc_data:
                    logger.warning(f"[-] Mensaje rechazado: Falta chat_id, sender_id o encrypted_message.")
                    continue
                
                # Registrar el socket en la sala si no estaba
                if current_chat_id != chat_id:
                    if current_chat_id and current_chat_id in chat_rooms:
                        chat_rooms[current_chat_id].discard(websocket)
                    
                    current_chat_id = chat_id
                    if chat_id not in chat_rooms:
                        chat_rooms[chat_id] = set()
                    chat_rooms[chat_id].add(websocket)

                logger.info(f"\n--- MENSAJE RECIBIDO (Sala: {chat_id} | Emisor: {sender_id}) ---")
                
                # Intentar descifrar en memoria para verificar integridad
                try:
                    plaintext = aes_cipher.decrypt(
                        enc_data.get('ciphertext_b64'),
                        enc_data.get('nonce_b64'),
                        enc_data.get('tag_b64')
                    )
                    logger.info(f"[Memoria] Descifrado exitoso: '{plaintext}'")
                except ValueError as crypto_err:
                    logger.error(f"[ERROR Criptográfico]: {crypto_err}")
                    continue

                # 1. Guardar en Base de Datos de forma asíncrona
                await asyncio.to_thread(save_message_to_db, chat_id, sender_id, enc_data)

                # 2. Retransmitir a la sala
                broadcast_msg = {
                    "chat_id": chat_id,
                    "sender_id": sender_id,
                    "encrypted_message": enc_data,
                    "system": False
                }
                await broadcast_to_room(chat_id, broadcast_msg, websocket)
                
            except json.JSONDecodeError:
                logger.error(f"[-] Error decodificando JSON del cliente {client_address}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if current_chat_id and current_chat_id in chat_rooms:
            chat_rooms[current_chat_id].discard(websocket)
            if not chat_rooms[current_chat_id]:
                del chat_rooms[current_chat_id]
        logger.info(f"[-] Conexión finalizada para {client_address[0]}:{client_address[1]}")

async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(base_dir, "server.crt")
    key_path = os.path.join(base_dir, "server.key")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        logger.error("[ERROR] Faltan los certificados SSL en la carpeta chat.")
        return

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    
    logger.info("=== INICIANDO SERVIDOR DE CHAT SEGURO DE ANIMOON ===")
    logger.info("Características: TLS 1.3, AES-GCM, y Persistencia en PostgreSQL")
    logger.info("Puerto de escucha: 8765")
    
    async with websockets.serve(handle_client, "0.0.0.0", 8765, ssl=ssl_context):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

