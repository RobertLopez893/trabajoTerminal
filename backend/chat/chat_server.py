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
from datetime import datetime, timezone
from sqlalchemy import func
import redis.asyncio as aioredis

# Agregar la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal
from backend.database.models import Mensaje, Chat, BloqueAnalisis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client: aioredis.Redis = None

# Diccionario para agrupar conexiones por chat_id: { "chat_id": set(websocket1, websocket2) }
chat_rooms = {}
# Mapeo por usuario para expulsión selectiva: { "chat_id": { "user_id": websocket } }
chat_user_sockets = {}

aes_cipher = AESGCMCipher()

def save_message_to_db(chat_id: str, sender_id: str, enc_data: dict, target_id: str = None) -> int:
    """
    Guarda el mensaje cifrado en la base de datos de forma síncrona calculando orden_global.
    Será ejecutado dentro de asyncio.to_thread para no bloquear el servidor.
    """
    db = SessionLocal()
    try:
        # Verificar si el chat existe
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat and target_id:
            nuevo_chat = Chat(
                id=chat_id,
                usuario_a_id=sender_id,
                usuario_b_id=target_id
            )
            db.add(nuevo_chat)
            db.commit()

        # Calcular el siguiente orden_global de forma incremental
        ultimo_orden = db.query(func.coalesce(func.max(Mensaje.orden_global), 0))\
                         .filter(Mensaje.chat_id == chat_id).scalar()
        nuevo_orden = (ultimo_orden or 0) + 1

        nuevo_mensaje = Mensaje(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            emisor_usuario_id=sender_id,
            contenido_cifrado_aes_gcm=enc_data.get('ciphertext_b64'),
            iv_nonce=enc_data.get('nonce_b64'),
            aes_gcm_tag=enc_data.get('tag_b64'),
            orden_global=nuevo_orden
        )
        db.add(nuevo_mensaje)
        db.commit()
        logger.info(f"[DB] Mensaje guardado en base de datos. ID: {nuevo_mensaje.id} (Orden: {nuevo_orden})")
        return nuevo_orden
    except Exception as e:
        db.rollback()
        logger.error(f"[DB ERROR] Error al guardar mensaje: {e}")
        return 1
    finally:
        db.close()


def crear_bloque_en_db(chat_id: str, total_mensajes: int = 20) -> dict:
    """
    Registra el BloqueAnalisis en PostgreSQL con estado 'PENDIENTE'.
    """
    db = SessionLocal()
    try:
        max_num = db.query(func.coalesce(func.max(BloqueAnalisis.numero_bloque), 0))\
                    .filter(BloqueAnalisis.chat_id == chat_id).scalar()
        siguiente_num = (max_num or 0) + 1

        bloque_id = str(uuid.uuid4())
        nuevo_bloque = BloqueAnalisis(
            id=bloque_id,
            chat_id=chat_id,
            numero_bloque=siguiente_num,
            total_mensajes=total_mensajes,
            estado="PENDIENTE",
            modelo_version="BETO_ONNX_INT8"
        )
        db.add(nuevo_bloque)
        db.commit()

        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        usuario_a_id = chat.usuario_a_id if chat else None
        usuario_b_id = chat.usuario_b_id if chat else None

        logger.info(f"[DB] BloqueAnalisis creado. ID: {bloque_id} | Bloque #{siguiente_num} ({total_mensajes} msgs)")
        return {
            "bloque_id": bloque_id,
            "numero_bloque": siguiente_num,
            "usuario_a_id": usuario_a_id,
            "usuario_b_id": usuario_b_id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"[DB ERROR] Error al crear BloqueAnalisis: {e}")
        return None
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

LUA_PUSH_AND_CUT = """
local len = redis.call('RPUSH', KEYS[1], ARGV[1])
redis.call('EXPIRE', KEYS[1], 900)
if len >= 20 then
    local msgs = redis.call('LRANGE', KEYS[1], 0, 19)
    redis.call('LTRIM', KEYS[1], 20, -1)
    return {len, msgs}
else
    return {len, {}}
end
"""


async def procesar_buffer_redis(chat_id: str, sender_id: str, plaintext: str, orden: int):
    """
    Agrega el mensaje en texto plano al buffer de Redis con TTL 900s.
    Si alcanza 20 mensajes, corta el bloque atómicamente, crea registro en DB y encola en queue:beto_jobs.
    """
    if not redis_client:
        return

    try:
        buffer_key = f"chat:{chat_id}:buffer"
        msg_payload = {
            "orden": orden,
            "emisor_id": sender_id,
            "texto": plaintext,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Ejecución atómica en Redis: RPUSH + EXPIRE + corte de 20 mensajes en 1 sola operación
        resultado = await redis_client.eval(LUA_PUSH_AND_CUT, 1, buffer_key, json.dumps(msg_payload))
        longitud = resultado[0]
        mensajes_raw = resultado[1]

        logger.info(f"[REDIS BUFFER] Sala: {chat_id} | Mensajes acumulados: {longitud}/20")

        # Si se extrajo un bloque completo de 20 mensajes
        if mensajes_raw:
            logger.info(f"[REDIS BUFFER] ¡Umbral de 20 mensajes alcanzado en sala '{chat_id}'! Extrayendo bloque...")
            mensajes_bloque = [json.loads(m) for m in mensajes_raw]

            # Crear registro en PostgreSQL en estado PENDIENTE
            bloque_info = await asyncio.to_thread(crear_bloque_en_db, chat_id, len(mensajes_bloque))

            if bloque_info:
                # Encolar trabajo en queue:beto_jobs
                job_payload = {
                    "bloque_id": bloque_info["bloque_id"],
                    "chat_id": chat_id,
                    "numero_bloque": bloque_info["numero_bloque"],
                    "usuario_a_id": bloque_info["usuario_a_id"],
                    "usuario_b_id": bloque_info["usuario_b_id"],
                    "total_mensajes": len(mensajes_bloque),
                    "mensajes": mensajes_bloque,
                    "enqueued_at": datetime.now(timezone.utc).isoformat()
                }

                await redis_client.lpush("queue:beto_jobs", json.dumps(job_payload))
                logger.info(f"[REDIS QUEUE] Tarea encolada con éxito en 'queue:beto_jobs' (Bloque: {bloque_info['bloque_id']})")
    except Exception as e:
        logger.error(f"[REDIS ERROR] Error procesando buffer de chat: {e}")


async def listen_grooming_alerts():
    """
    Tarea en segundo plano suscrita al canal channel:grooming_alerts de Redis.
    Al recibir alerta de grooming:
    - Notifica a la víctima con pantalla de salida segura (SAFE_EXIT).
    - Cierra inmediatamente el WebSocket del agresor.
    """
    logger.info("[REDIS PUB/SUB] Iniciando listener en canal 'channel:grooming_alerts'...")
    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("channel:grooming_alerts")

        async for raw_event in pubsub.listen():
            if raw_event["type"] == "message":
                try:
                    data = json.loads(raw_event["data"])
                    chat_id = data.get("chat_id")
                    agresor_id = data.get("agresor_id")
                    victima_id = data.get("victima_id")
                    motivo = data.get("motivo", "Comportamiento inapropiado detectado.")

                    logger.warning(f"🚨 [ALERTA RECIBIDA EN CHAT] Grooming detectado en sala '{chat_id}'. Agresor: {agresor_id}")

                    if chat_id in chat_user_sockets:
                        sockets_sala = chat_user_sockets[chat_id]

                        # 1. Notificar a la víctima para salida segura
                        victima_ws = sockets_sala.get(victima_id)
                        if victima_ws:
                            try:
                                enc_alerta = aes_cipher.encrypt("El chat ha sido suspendido por razones de seguridad preventiva.")
                                notif_victima = {
                                    "chat_id": chat_id,
                                    "sender_id": "SISTEMA",
                                    "encrypted_message": enc_alerta,
                                    "system": True,
                                    "action": "SAFE_EXIT",
                                    "motivo": motivo
                                }
                                await victima_ws.send(json.dumps(notif_victima))
                                logger.info(f"[SEGURIDAD] Evento SAFE_EXIT enviado a la victima {victima_id}")
                            except Exception as ws_err:
                                logger.warning(f"[SEGURIDAD] Error enviando a victima: {ws_err}")

                        # 2. Expulsar y matar la conexión del agresor
                        agresor_ws = sockets_sala.get(agresor_id)
                        if agresor_ws:
                            try:
                                logger.warning(f"[SEGURIDAD] Desconectando y matando WebSocket del agresor {agresor_id}")
                                await agresor_ws.close(code=4003, reason="Cuenta suspendida por seguridad")
                            except Exception as ws_err:
                                logger.warning(f"[SEGURIDAD] Error cerrando socket agresor: {ws_err}")
                except Exception as err:
                    logger.error(f"[PUB/SUB ERROR] Error procesando evento de alerta: {err}")

    except asyncio.CancelledError:
        logger.info("[REDIS PUB/SUB] Listener cancelado.")
    except Exception as e:
        logger.error(f"[REDIS PUB/SUB ERROR] Excepción en listener de alertas: {e}")


async def handle_client(websocket):
    """
    Maneja el ciclo de vida de la conexión de un cliente en el chat.
    """
    client_address = websocket.remote_address
    logger.info(f"\n[+] Nueva conexión establecida desde {client_address[0]}:{client_address[1]}")
    
    current_chat_id = None
    current_user_id = None

    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                
                chat_id = data.get("chat_id")
                sender_id = data.get("sender_id", "Usuario_Desconocido")
                target_id = data.get("target_id")
                enc_data = data.get("encrypted_message")
                
                if not chat_id or not sender_id or not enc_data:
                    logger.warning(f"[-] Mensaje rechazado: Falta chat_id, sender_id o encrypted_message.")
                    continue
                
                # Validar inmediatamente si el usuario está suspendido
                if redis_client and await redis_client.sismember("banned_users", sender_id):
                    logger.warning(f"🚫 [SEGURIDAD] Usuario suspendido '{sender_id}' intentó enviar mensaje. Cerrando socket.")
                    await websocket.close(code=4003, reason="Cuenta suspendida por seguridad")
                    return

                current_user_id = sender_id

                # Registrar el socket en la sala si no estaba
                if current_chat_id != chat_id:
                    if current_chat_id and current_chat_id in chat_rooms:
                        chat_rooms[current_chat_id].discard(websocket)
                    
                    current_chat_id = chat_id
                    if chat_id not in chat_rooms:
                        chat_rooms[chat_id] = set()
                    chat_rooms[chat_id].add(websocket)

                # Registrar también en el diccionario de usuarios
                if chat_id not in chat_user_sockets:
                    chat_user_sockets[chat_id] = {}
                chat_user_sockets[chat_id][sender_id] = websocket

                logger.info(f"\n--- MENSAJE RECIBIDO (Sala: {chat_id} | Emisor: {sender_id}) ---")
                
                # Descifrar en memoria para verificar integridad
                try:
                    plaintext = aes_cipher.decrypt(
                        enc_data.get('ciphertext_b64'),
                        enc_data.get('nonce_b64'),
                        enc_data.get('tag_b64')
                    )
                    logger.info(f"[Crypto] Integridad verificada y descifrado en memoria correcto (Longitud: {len(plaintext)} caracteres)")
                except ValueError as crypto_err:
                    logger.error(f"[ERROR Criptográfico]: {crypto_err}")
                    continue

                # 1. Retransmitir inmediatamente a la sala (CERO LATENCIA para los usuarios)
                broadcast_msg = {
                    "chat_id": chat_id,
                    "sender_id": sender_id,
                    "encrypted_message": enc_data,
                    "system": False
                }
                await broadcast_to_room(chat_id, broadcast_msg, websocket)

                # 2. Guardar en PostgreSQL de forma asíncrona
                nuevo_orden = await asyncio.to_thread(save_message_to_db, chat_id, sender_id, enc_data, target_id)

                # 3. Empujar al buffer de Redis (Out-of-Band, no afecta velocidad de chat)
                await procesar_buffer_redis(chat_id, sender_id, plaintext, nuevo_orden)
                
            except json.JSONDecodeError:
                logger.error(f"[-] Error decodificando JSON del cliente {client_address}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if current_chat_id and current_chat_id in chat_rooms:
            chat_rooms[current_chat_id].discard(websocket)
            if not chat_rooms[current_chat_id]:
                del chat_rooms[current_chat_id]
        if current_chat_id and current_chat_id in chat_user_sockets:
            if current_user_id and current_user_id in chat_user_sockets[current_chat_id]:
                del chat_user_sockets[current_chat_id][current_user_id]
            if not chat_user_sockets[current_chat_id]:
                del chat_user_sockets[current_chat_id]
        logger.info(f"[-] Conexión finalizada para {client_address[0]}:{client_address[1]}")


async def main():
    global redis_client
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
    
    # Inicializar conexión asíncrona con Redis (pool de hasta 1000 conexiones concurrentes)
    try:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True, max_connections=1000)
        await redis_client.ping()
        logger.info(f"[REDIS] Conectado exitosamente a {REDIS_URL}")
    except Exception as e:
        logger.error(f"[REDIS ERROR] No se pudo conectar a Redis: {e}")
        return

    # Precargar usuarios baneados en Redis desde la base de datos
    db_init = SessionLocal()
    try:
        from backend.database.models import Usuario
        banned_users = db_init.query(Usuario.id).filter(Usuario.is_banned == True).all()
        if banned_users and redis_client:
            banned_ids = [u.id for u in banned_users]
            await redis_client.sadd("banned_users", *banned_ids)
            logger.info(f"🚫 [SEGURIDAD] Se precargaron {len(banned_ids)} usuarios baneados en Redis.")
    except Exception as e:
        logger.error(f"[ERROR] Error precargando usuarios baneados en Redis: {e}")
    finally:
        db_init.close()

    # Iniciar listener de alertas Pub/Sub en segundo plano
    alert_listener_task = asyncio.create_task(listen_grooming_alerts())

    logger.info("=== INICIANDO SERVIDOR DE CHAT SEGURO DE ANIMOON ===")
    logger.info("Características: TLS 1.3, AES-GCM, Persistencia PostgreSQL y Buffer Redis")
    logger.info(f"Puerto de escucha: 8765")
    
    async with websockets.serve(handle_client, "0.0.0.0", 8765, ssl=ssl_context):
        try:
            await asyncio.Future() # Mantener corriendo indefinidamente
        finally:
            alert_listener_task.cancel()
            await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())
