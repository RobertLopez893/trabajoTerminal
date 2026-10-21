"""
Consola Interactiva de Chat Seguro TLS 1.3 para Animoon (Backend / Developer CLI)
Permite enviar y recibir mensajes cifrados en tiempo real a través del Chat Server.

Modos de uso:
1. Modo interactivo local (Dual: Alice vs Bob en una sola consola):
   python console_chat.py --interactive

2. Modo cliente individual (para dos terminales independientes):
   Terminal 1: python console_chat.py --user Alice --target Bob --chat-id demo_room
   Terminal 2: python console_chat.py --user Bob --target Alice --chat-id demo_room
"""

import os
import sys
import ssl
import json
import time
import uuid
import asyncio
import argparse
import websockets
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal
from backend.database.models import Usuario, Chat

WS_URL = os.getenv("WS_URL", "wss://127.0.0.1:8765")
aes = AESGCMCipher()


def configurar_ssl():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def asegurar_usuario_y_chat(chat_id: str, u1: str, u2: str):
    db = SessionLocal()
    try:
        for uid in [u1, u2]:
            u = db.query(Usuario).filter(Usuario.id == uid).first()
            if not u:
                enc = aes.encrypt("+525511223344")
                db.add(Usuario(
                    id=uid,
                    nickname=f"cli_{uid[:10]}",
                    telefono_cifrado=enc["ciphertext_b64"],
                    telefono_iv_nonce=enc["nonce_b64"],
                    telefono_tag=enc["tag_b64"],
                    argon2id_hash="dummy_hash",
                    salt="dummy_salt",
                    is_verified=True,
                    is_active=True,
                    is_banned=False
                ))
            else:
                u.is_banned = False
        db.commit()

        c = db.query(Chat).filter(Chat.id == chat_id).first()
        if not c:
            db.add(Chat(id=chat_id, usuario_a_id=u1, usuario_b_id=u2))
            db.commit()
    finally:
        db.close()


async def modo_cliente_individual(chat_id: str, mi_id: str, receptor_id: str):
    """Ejecuta un cliente WebSocket interactivo en la terminal."""
    asegurar_usuario_y_chat(chat_id, mi_id, receptor_id)
    ssl_ctx = configurar_ssl()

    print("=" * 75)
    print(f"💬 CLIENTE DE CHAT ANIMOON — Usuario: [{mi_id}] ➡️ Receptor: [{receptor_id}]")
    print(f"   Sala: {chat_id} | Servidor: {WS_URL} (TLS 1.3 / AES-256-GCM)")
    print("   Escribe tu mensaje y presiona Enter (o 'exit' para salir):")
    print("=" * 75)

    async with websockets.connect(WS_URL, ssl=ssl_ctx) as ws:

        # Escucha en segundo plano
        async def listener():
            try:
                async for raw in ws:
                    data = json.loads(raw)
                    emisor = data.get("sender_id")

                    # Alerta de seguridad preventiva
                    if data.get("action") == "SAFE_EXIT":
                        print("\n" + "🚨" * 35)
                        print(" [SISTEMA] 🛡️ PROTOCOLO DE SALIDA SEGURA (SAFE_EXIT)")
                        print(f" Motivo: {data.get('motivo')}")
                        print(" La sala ha sido cerrada preventivamente por el servidor.")
                        print("🚨" * 35 + "\n> ", end="", flush=True)
                        continue

                    # Mensaje regular de chat
                    enc_data = data.get("encrypted_message", {})
                    c_b64 = enc_data.get("ciphertext_b64") or enc_data.get("ciphertext")
                    n_b64 = enc_data.get("nonce_b64") or enc_data.get("nonce")
                    t_b64 = enc_data.get("tag_b64") or enc_data.get("tag")

                    if c_b64 and n_b64 and t_b64 and emisor != mi_id:
                        try:
                            texto_descifrado = aes.decrypt(c_b64, n_b64, t_b64)
                            hora = time.strftime("%H:%M:%S")
                            print(f"\r[{hora}] 💬 {emisor}: {texto_descifrado}\n> ", end="", flush=True)
                        except Exception as dec_err:
                            print(f"\r[!] Error descifrando mensaje de {emisor}: {dec_err}\n> ", end="", flush=True)

            except websockets.exceptions.ConnectionClosed as e:
                if e.code == 4003:
                    print("\n\n⚡ [EXPULSIÓN] Tu cuenta ha sido suspendida y expulsada por el servidor (Código 4003).")
                else:
                    print(f"\n\n[!] Conexión cerrada por el servidor: code={e.code}, reason={e.reason}")

        listen_task = asyncio.create_task(listener())

        # Bucle de envío
        loop = asyncio.get_event_loop()
        while True:
            try:
                msg_texto = await loop.run_in_executor(None, input, "> ")
                if not msg_texto or msg_texto.strip().lower() == "exit":
                    break

                enc = aes.encrypt(msg_texto.strip())
                payload = {
                    "chat_id": chat_id,
                    "sender_id": mi_id,
                    "target_id": receptor_id,
                    "encrypted_message": enc,
                    "timestamp": str(time.time()),
                    "is_file": False
                }
                await ws.send(json.dumps(payload))
            except Exception as send_err:
                print(f"[!] Error enviando mensaje: {send_err}")
                break

        listen_task.cancel()


async def modo_interactivo_dual(chat_id: str = "demo_interactive"):
    """Permite alternar entre dos usuarios desde la misma consola."""
    u1, u2 = "Alice", "Bob"
    asegurar_usuario_y_chat(chat_id, u1, u2)
    ssl_ctx = configurar_ssl()

    print("=" * 80)
    print("🎮 CONSOLA DUAL INTERACTIVA (Alice vs Bob en vivo)")
    print(f"   Sala: {chat_id} | Servidor: {WS_URL}")
    print("   Instrucciones:")
    print("   - Escribe 'a: tu mensaje' para hablar como Alice")
    print("   - Escribe 'b: tu mensaje' para hablar como Bob")
    print("   - Si no pones prefijo, alternará automáticamente")
    print("   - Escribe 'exit' para terminar")
    print("=" * 80)

    async with websockets.connect(WS_URL, ssl=ssl_ctx) as ws_a, \
               websockets.connect(WS_URL, ssl=ssl_ctx) as ws_b:

        # Escuchadores de fondo
        async def listen(ws, name):
            try:
                async for raw in ws:
                    data = json.loads(raw)
                    if data.get("action") == "SAFE_EXIT":
                        print(f"\n🚨 [{name.upper()}] RECIBIÓ EVENTO 'SAFE_EXIT': {data.get('motivo')}\n> ", end="", flush=True)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"\n⚡ [{name.upper()}] SOCKET CERRADO: Código {e.code} ({e.reason})\n> ", end="", flush=True)

        t_a = asyncio.create_task(listen(ws_a, u1))
        t_b = asyncio.create_task(listen(ws_b, u2))

        turno = "a"
        loop = asyncio.get_event_loop()
        while True:
            try:
                linea = await loop.run_in_executor(None, input, f"[{turno.upper()}] > ")
                if not linea or linea.strip().lower() == "exit":
                    break

                emisor_actual = turno
                texto = linea.strip()
                if texto.startswith("a:") or texto.startswith("A:"):
                    emisor_actual = "a"
                    texto = texto[2:].strip()
                elif texto.startswith("b:") or texto.startswith("B:"):
                    emisor_actual = "b"
                    texto = texto[2:].strip()

                if emisor_actual == "a":
                    sender, target, ws = u1, u2, ws_a
                    color = "🟢"
                else:
                    sender, target, ws = u2, u1, ws_b
                    color = "🔵"

                enc = aes.encrypt(texto)
                payload = {
                    "chat_id": chat_id,
                    "sender_id": sender,
                    "target_id": target,
                    "encrypted_message": enc,
                    "timestamp": str(time.time()),
                    "is_file": False
                }
                await ws.send(json.dumps(payload))
                print(f"  {color} Enviado [{sender} ➡️ {target}] (AES-GCM): {texto}")

                # Alternar turno para la siguiente entrada
                turno = "b" if emisor_actual == "a" else "a"
            except Exception as e:
                print(f"[!] Error: {e}")
                break

        t_a.cancel()
        t_b.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente interactivo de Chat TLS 1.3")
    parser.add_argument("--interactive", action="store_true", help="Modo dual interactivo en una sola consola")
    parser.add_argument("--user", type=str, default="Alice", help="ID del usuario emisor")
    parser.add_argument("--target", type=str, default="Bob", help="ID del usuario receptor")
    parser.add_argument("--chat-id", type=str, default="sala_demo", help="ID de la sala")
    args = parser.parse_args()

    if args.interactive:
        asyncio.run(modo_interactivo_dual(chat_id=args.chat_id))
    else:
        asyncio.run(modo_cliente_individual(args.chat_id, args.user, args.target))
