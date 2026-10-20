import asyncio
import httpx
import websockets
import ssl
import json
import uuid
import sys
import os
import time
import jwt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal
from backend.database.models import Chat

API_URL = "http://localhost:8000/api/auth"
WS_URL = "wss://127.0.0.1:8765"
aes = AESGCMCipher()

def create_chat_in_db(user_a_id: str, user_b_id: str) -> str:
    db = SessionLocal()
    chat_id = str(uuid.uuid4())
    new_chat = Chat(id=chat_id, usuario_a_id=user_a_id, usuario_b_id=user_b_id)
    db.add(new_chat)
    db.commit()
    db.close()
    return chat_id

async def simulate():
    print("=== INICIANDO SIMULACIÓN END-TO-END DE ANIMOON ===")
    
    timestamp = str(int(time.time()))
    alice_nick = f"Alice_{timestamp[-4:]}"
    bob_nick = f"Bob_{timestamp[-4:]}"
    password = "Password123!"

    async with httpx.AsyncClient() as client:
        # 1. Registro de Alice
        print(f"\n[1] Registrando a {alice_nick}...")
        res_a = await client.post(f"{API_URL}/registro-final", json={
            "nickname": alice_nick,
            "password": password,
            "telefono": "0000000000",
            "codigo_verificacion": "000000",
            "avatar_especie": "conejo",
            "avatar_color": "rojo"
        })
        print(f"  Respuesta: {res_a.json()}")

        # 2. Registro de Bob
        print(f"\n[2] Registrando a {bob_nick}...")
        res_b = await client.post(f"{API_URL}/registro-final", json={
            "nickname": bob_nick,
            "password": password,
            "telefono": "0000000000",
            "codigo_verificacion": "000000",
            "avatar_especie": "zorro",
            "avatar_color": "azul"
        })
        print(f"  Respuesta: {res_b.json()}")

        # 3. Logins
        print("\n[3] Iniciando sesión...")
        login_a = await client.post(f"{API_URL}/login", json={
            "nickname": alice_nick,
            "password": password,
            "client_ecdhe_public_key": "MOCK_KEY_ANDROID"
        })
        token_a = login_a.json()["access_token"]
        payload_a = jwt.decode(token_a, options={"verify_signature": False})
        alice_id = payload_a["sub"]

        login_b = await client.post(f"{API_URL}/login", json={
            "nickname": bob_nick,
            "password": password,
            "client_ecdhe_public_key": "MOCK_KEY_ANDROID"
        })
        token_b = login_b.json()["access_token"]
        payload_b = jwt.decode(token_b, options={"verify_signature": False})
        bob_id = payload_b["sub"]

        print(f"  Alice ID: {alice_id}")
        print(f"  Bob ID:   {bob_id}")

    # 4. Crear el Chat en la BD
    print("\n[4] Creando sala de chat en la base de datos...")
    chat_id = create_chat_in_db(alice_id, bob_id)
    print(f"  Chat ID generado: {chat_id}")

    # 5. Conexión WebSocket
    print("\n[5] Conectando a WebSockets (TLS 1.3)...")
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Ignorar cert autofirmado para desarrollo

    async def chat_participant(name, user_id, message_to_send=None, wait_for_reply=False):
        async with websockets.connect(WS_URL, ssl=ssl_context) as ws:
            # Recibir bienvenida del servidor
            welcome = await ws.recv()
            print(f"  [{name} WS] Conectado. Bienvenida recibida.")

            if message_to_send:
                print(f"\n  [{name} WS] Encriptando mensaje: '{message_to_send}'")
                enc_msg = aes.encrypt(message_to_send)
                payload = {
                    "chat_id": chat_id,
                    "sender_id": user_id,
                    "encrypted_message": enc_msg
                }
                await ws.send(json.dumps(payload))
                print(f"  [{name} WS] Mensaje enviado al servidor.")

            if wait_for_reply:
                print(f"  [{name} WS] Esperando mensaje entrante de otro usuario...")
                reply_raw = await ws.recv()
                reply_data = json.loads(reply_raw)
                if not reply_data.get('system'):
                    enc = reply_data["encrypted_message"]
                    decrypted = aes.decrypt(enc['ciphertext_b64'], enc['nonce_b64'], enc['tag_b64'])
                    print(f"  [{name} WS] 📩 Mensaje recibido y descifrado exitosamente: '{decrypted}'")
                
            await asyncio.sleep(1)

    # Lanzamos ambos clientes (Alice envía, Bob espera recibir)
    print("\n[6] Simulando conversación...")
    task_bob = asyncio.create_task(chat_participant("Bob", bob_id, wait_for_reply=True))
    
    # Damos un pequeño margen para que Bob se conecte primero y escuche
    await asyncio.sleep(1) 
    
    task_alice = asyncio.create_task(chat_participant("Alice", alice_id, message_to_send="¡Hola Bob! ¿Quieres explorar la Aldea Lunática?"))

    await asyncio.gather(task_bob, task_alice)

    print("\n=== SIMULACIÓN FINALIZADA CON ÉXITO ===")
    print("Revisa la consola del docker (animoon_chat) o tu base de datos (tabla MENSAJE) para confirmar la persistencia.")

if __name__ == "__main__":
    asyncio.run(simulate())
