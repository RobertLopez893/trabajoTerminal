import asyncio
import json
import os
import ssl
import sys
import websockets

# Agregar la raíz del proyecto al sys.path para importar correctamente el motor criptográfico
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.aes.aes_gcm import AESGCMCipher

# Inicializar el cifrador AES-GCM
aes_cipher = AESGCMCipher()

async def receive_messages(websocket):
    """
    Escucha y muestra continuamente los mensajes recibidos del servidor.
    Los mensajes recibidos vienen cifrados a nivel de aplicación (AES-256-GCM)
    y protegidos por transporte (TLS 1.3).
    """
    try:
        async for message_raw in websocket:
            data = json.loads(message_raw)
            sender = data.get("sender", "System")
            enc_data = data.get("encrypted_message")
            is_system = data.get("system", False)
            
            # Descifrar el mensaje a nivel de aplicación
            message = ""
            if enc_data:
                try:
                    message = aes_cipher.decrypt(
                        enc_data.get("ciphertext_b64"),
                        enc_data.get("nonce_b64"),
                        enc_data.get("tag_b64")
                    )
                except ValueError as err:
                    message = f"[FALLO DE INTEGRIDAD/DESCIFRADO: {err}]"
            else:
                message = "[Mensaje sin cifrar recibido]"

            if is_system:
                print(f"\n[SISTEMA] {message}")
            else:
                print(f"\n[{sender}]: {message}")
            print("> ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\n[-] Conexión cerrada por el servidor.")

async def send_messages(websocket, username):
    """
    Permite al usuario escribir y enviar mensajes de forma interactiva.
    Los mensajes son cifrados a nivel de aplicación antes de ser enviados.
    """
    loop = asyncio.get_event_loop()
    try:
        while True:
            # Leer entrada del teclado de forma no bloqueante
            message = await loop.run_in_executor(None, input, "> ")
            if not message.strip():
                continue
            if message.lower() == "exit":
                break
            
            # 1. Cifrar el mensaje usando AES-256-GCM
            encrypted_data = aes_cipher.encrypt(message)
            
            # 2. Empaquetar y enviar
            payload = {
                "sender": username,
                "encrypted_message": encrypted_data
            }
            await websocket.send(json.dumps(payload))
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass

async def main():
    username = input("Ingresa tu apodo para el chat: ").strip() or "UsuarioPrueba"
    
    # Obtener la ruta del certificado auto-firmado
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(base_dir, "server.crt")
    
    if not os.path.exists(cert_path):
        print(f"[ERROR] No se encuentra el certificado {cert_path}")
        print("Por favor ejecuta 'generate_certs.py' en la carpeta backend primero.")
        return

    # Configurar el contexto SSL para el cliente (TLS 1.3 estricto)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(cafile=cert_path)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

    url = "wss://localhost:8765"
    print(f"\nConectando de forma segura a {url} (TLS 1.3)...")
    
    try:
        async with websockets.connect(url, ssl=ssl_context) as websocket:
            # Obtener detalles del socket SSL para verificar TLS 1.3
            ssl_object = websocket.transport.get_extra_info('ssl_object')
            if ssl_object:
                version = ssl_object.version()
                cipher = ssl_object.cipher()
                print("==================================================")
                print("[CONEXIÓN CRIPTOGRÁFICA DOBLE ESTABLECIDA]")
                print(f" Capa 1 (Transporte): {version} | {cipher[0]}")
                print(" Capa 2 (Aplicación): AES-256-GCM (Motor local)")
                print("==================================================")
            else:
                print("[ADVERTENCIA] Conectado sin cifrado de transporte.")

            print("Escribe tus mensajes a continuación (escribe 'exit' para salir):")
            
            receive_task = asyncio.create_task(receive_messages(websocket))
            send_task = asyncio.create_task(send_messages(websocket, username))
            
            done, pending = await asyncio.wait(
                [receive_task, send_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
                
    except Exception as e:
        print(f"\n[ERROR] No se pudo establecer la conexión segura: {e}")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[+] Cliente cerrado.")
