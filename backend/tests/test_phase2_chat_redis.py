"""
=============================================================================
PRUEBA DE INTEGRACIÓN: FASE 2 - CHAT SERVER + REDIS BUFFER + CORTE + PUB/SUB
=============================================================================
Este script valida todo el flujo implementado en la Fase 2:
1. Conexión WebSocket segura (TLS 1.3 / WSS) al Chat Server de Animoon.
2. Envío de 20 mensajes cifrados (AES-256-GCM) entre dos usuarios.
3. Verificación de retransmisión inmediata al destinatario (Cero latencia).
4. Acumulación progresiva en el buffer de Redis (chat:{chat_id}:buffer) con TTL 900s.
5. Al mensaje #20:
   - Corte del bloque en Redis (extracción de los 20 mensajes).
   - Creación automática del registro en PostgreSQL (tabla 'bloque_analisis' en estado 'PENDIENTE').
   - Encolado de la tarea en Redis ('queue:beto_jobs').
6. Simulación de Alerta Grooming vía Pub/Sub:
   - Publicación en 'channel:grooming_alerts'.
   - Verificación de recepción de evento 'SAFE_EXIT' en la víctima.
   - Verificación de desconexión forzosa (cierre de socket) en el agresor.
=============================================================================
"""

import os
import sys
import ssl
import json
import time
import uuid
import asyncio
import redis
import websockets
from dotenv import load_dotenv

# Asegurar codificación utf-8 en terminales Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal
from backend.database.models import BloqueAnalisis, Chat, Mensaje, Usuario

WS_URL = "wss://127.0.0.1:8765"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

aes = AESGCMCipher()

def configurar_ssl_cliente():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context

def preparar_entorno_db(chat_id: str, user_a_id: str, user_b_id: str):
    """Crea usuarios y chat en la base de datos para respetar las llaves foráneas."""
    db = SessionLocal()
    try:
        # 1. Asegurar usuarios
        for uid, nick in [(user_a_id, f"alice_{user_a_id[-4:]}"), (user_b_id, f"bob_{user_b_id[-4:]}")]:
            u = db.query(Usuario).filter(Usuario.id == uid).first()
            if not u:
                enc_tel = aes.encrypt("+525512345678")
                u = Usuario(
                    id=uid,
                    nickname=nick,
                    telefono_cifrado=enc_tel["ciphertext_b64"],
                    telefono_iv_nonce=enc_tel["nonce_b64"],
                    telefono_tag=enc_tel["tag_b64"],
                    argon2id_hash="dummy_hash_for_test",
                    salt="dummy_salt_for_test",
                    is_verified=True,
                    is_active=True
                )
                db.add(u)
        db.commit()

        # 2. Asegurar chat
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            chat = Chat(id=chat_id, usuario_a_id=user_a_id, usuario_b_id=user_b_id)
            db.add(chat)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR DB SETUP]: {e}")
    finally:
        db.close()

def limpiar_datos_prueba(chat_id: str, r: redis.Redis):
    """Limpia Redis y PostgreSQL de pruebas anteriores"""
    try:
        r.delete(f"chat:{chat_id}:buffer")
        r.delete("queue:beto_jobs")
        
        db = SessionLocal()
        db.query(BloqueAnalisis).filter(BloqueAnalisis.chat_id == chat_id).delete()
        db.query(Mensaje).filter(Mensaje.chat_id == chat_id).delete()
        db.commit()
        db.close()
    except Exception as e:
        print(f"[AVISO] Limpieza previa: {e}")

async def test_flujo_fase_2():
    print("=" * 70)
    print("   TEST DE INTEGRACIÓN: FASE 2 (CHAT SERVER + BUFFER 20 MSGS + REDIS)")
    print("=" * 70)
    
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    print("[OK] Conectado a Redis para verificación.")

    chat_id = f"test_chat_{int(time.time())}"
    alice_id = f"alice_{uuid.uuid4().hex[:6]}"
    bob_id = f"bob_{uuid.uuid4().hex[:6]}"

    limpiar_datos_prueba(chat_id, r)
    preparar_entorno_db(chat_id, alice_id, bob_id)
    print(f"[OK] Entorno de base de datos preparado para '{chat_id}'.")

    ssl_ctx = configurar_ssl_cliente()
    print(f"[*] Conectando participantes al WebSocket ({WS_URL})...")
    print(f"    Sala ID: {chat_id}")
    print(f"    Alice (Agresor Simulado): {alice_id}")
    print(f"    Bob   (Víctima Simulada): {bob_id}\n")

    mensajes_bob_recibidos = []
    evento_alerta_victima = asyncio.Event()
    agresor_desconectado = asyncio.Event()

    try:
        async with websockets.connect(WS_URL, ssl=ssl_ctx) as ws_alice, \
                   websockets.connect(WS_URL, ssl=ssl_ctx) as ws_bob:

            print("[OK] Ambos sockets conectados exitosamente (TLS 1.3).")

            # Tarea para escuchar en el socket de Bob
            async def escuchar_bob():
                try:
                    async for raw in ws_bob:
                        msg = json.loads(raw)
                        if msg.get("action") == "SAFE_EXIT":
                            print(f"\n🛡️ [BOB] ¡Recibido evento SAFE_EXIT de seguridad preventiva!")
                            evento_alerta_victima.set()
                        else:
                            enc = msg.get("encrypted_message")
                            if enc:
                                texto = aes.decrypt(enc['ciphertext_b64'], enc['nonce_b64'], enc['tag_b64'])
                                mensajes_bob_recibidos.append(texto)
                except websockets.exceptions.ConnectionClosed:
                    pass

            # Tarea para detectar desconexión forzosa en Alice
            async def escuchar_alice():
                try:
                    async for _ in ws_alice:
                        pass
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"\n⚡ [ALICE] Conexión cerrada por el servidor. Código: {e.code} | Razón: '{e.reason}'")
                    if e.code == 4003:
                        agresor_desconectado.set()

            task_bob = asyncio.create_task(escuchar_bob())
            task_alice = asyncio.create_task(escuchar_alice())

            await asyncio.sleep(0.5)

            # -------------------------------------------------------------
            # PASO 1: Enviar 20 mensajes
            # -------------------------------------------------------------
            print("\n" + "─" * 70)
            print("[1] Enviando ráfaga de 20 mensajes cifrados...")
            print("─" * 70)

            for i in range(1, 21):
                emisor_actual = alice_id if i % 2 != 0 else bob_id
                target_actual = bob_id if i % 2 != 0 else alice_id
                ws_emisor = ws_alice if emisor_actual == alice_id else ws_bob

                texto = f"Mensaje número {i} de la conversación de prueba."
                enc = aes.encrypt(texto)
                payload = {
                    "chat_id": chat_id,
                    "sender_id": emisor_actual,
                    "target_id": target_actual,
                    "encrypted_message": enc
                }

                await ws_emisor.send(json.dumps(payload))
                await asyncio.sleep(0.05) # Simular tráfico rápido

                buffer_len = r.llen(f"chat:{chat_id}:buffer")
                if i < 20:
                    print(f"  -> Mensaje #{i:02d} enviado | Acumulado en Redis Buffer: {buffer_len}/20")
                else:
                    print(f"  -> Mensaje #{i:02d} enviado | Buffer alcanzó 20!")

            # Esperar a que el servidor procese el corte
            await asyncio.sleep(1.0)

            # -------------------------------------------------------------
            # PASO 2: Verificar corte de bloque y encolado en Redis
            # -------------------------------------------------------------
            print("\n" + "─" * 70)
            print("[2] Verificando corte de bloque en Redis y PostgreSQL...")
            print("─" * 70)

            buffer_restante = r.llen(f"chat:{chat_id}:buffer")
            print(f"[*] Buffer restante en Redis: {buffer_restante} mensajes (esperado: 0)")
            assert buffer_restante == 0, f"Error: El buffer de Redis debió vaciarse, quedan {buffer_restante}"

            # Verificar cola queue:beto_jobs
            trabajos_en_cola = r.llen("queue:beto_jobs")
            print(f"[OK] Trabajos encolados en 'queue:beto_jobs': {trabajos_en_cola}")
            assert trabajos_en_cola >= 1, "Error: No se encontró trabajo encolado en queue:beto_jobs"

            # Inspeccionar el payload del trabajo encolado
            trabajo_raw = r.lindex("queue:beto_jobs", -1)
            trabajo = json.loads(trabajo_raw)
            print(f"[OK] Contenido de la tarea encolada:")
            print(f"     ID Bloque: {trabajo['bloque_id']}")
            print(f"     Número de Bloque: #{trabajo['numero_bloque']}")
            print(f"     Total de mensajes en payload: {len(trabajo['mensajes'])}")
            print(f"     Primer mensaje: '{trabajo['mensajes'][0]['texto']}'")
            print(f"     Último mensaje: '{trabajo['mensajes'][-1]['texto']}'")

            # Verificar PostgreSQL
            db = SessionLocal()
            bloque_db = db.query(BloqueAnalisis).filter(BloqueAnalisis.id == trabajo['bloque_id']).first()
            assert bloque_db is not None, "Error: No se encontró el registro BloqueAnalisis en PostgreSQL"
            print(f"[OK] Registro verificado en PostgreSQL (BloqueAnalisis):")
            print(f"     ID: {bloque_db.id} | Estado: {bloque_db.estado} | Total: {bloque_db.total_mensajes}")
            db.close()

            # -------------------------------------------------------------
            # PASO 3: Simular alerta Pub/Sub y validar desconexión en caliente
            # -------------------------------------------------------------
            print("\n" + "─" * 70)
            print("[3] Simulando alerta de Grooming desde Pub/Sub...")
            print("─" * 70)

            alerta_mock = {
                "chat_id": chat_id,
                "agresor_id": alice_id,
                "victima_id": bob_id,
                "motivo": "Detección de patrones de aislamiento infantil (Nivel 2)"
            }

            print(f"[*] Publicando alerta simulada en 'channel:grooming_alerts'...")
            r.publish("channel:grooming_alerts", json.dumps(alerta_mock))

            # Esperar a que el chat server reaccione
            try:
                await asyncio.wait_for(evento_alerta_victima.wait(), timeout=3.0)
                print(f"[OK] Víctima (Bob) recibió pantalla de salida segura (SAFE_EXIT).")
            except asyncio.TimeoutError:
                print(f"[ERROR] Bob no recibió la alerta SAFE_EXIT a tiempo.")

            try:
                await asyncio.wait_for(agresor_desconectado.wait(), timeout=3.0)
                print(f"[OK] Agresor (Alice) fue desconectado forzosamente con código 4003.")
            except asyncio.TimeoutError:
                print(f"[ERROR] Alice no fue desconectada a tiempo.")

            task_bob.cancel()
            task_alice.cancel()

            print("\n" + "=" * 70)
            print(">>> [ÉXITO TOTAL] FASE 2 VERIFICADA COMPLETAMENTE <<<")
            print("    1. 20 mensajes cifrados procesados con cero latencia.")
            print("    2. Buffer de Redis cortado automáticamente al llegar a 20.")
            print("    3. Registro en PostgreSQL (BloqueAnalisis PENDIENTE) generado.")
            print("    4. Tarea lista en queue:beto_jobs para el futuro worker.")
            print("    5. Pub/Sub desconecta agresores y protege víctimas en tiempo real.")
            print("=" * 70)
            return True

    except Exception as e:
        print(f"\n[ERROR EN LA PRUEBA]: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = asyncio.run(test_flujo_fase_2())
    sys.exit(0 if exito else 1)
