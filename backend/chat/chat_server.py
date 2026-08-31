import asyncio
import json
import os
import ssl
import sys
import websockets

# Agregar la raíz del proyecto al sys.path para importar correctamente el motor criptográfico
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from security.aes.aes_gcm import AESGCMCipher

# Conjunto de clientes conectados
clients = set()
# Inicializar el cifrador AES-GCM
aes_cipher = AESGCMCipher()

async def broadcast(message_dict, sender_ws):
    """
    Envía un mensaje a todos los clientes conectados excepto al remitente.
    El mensaje ya viene cifrado a nivel de aplicación.
    """
    if clients:
        payload = json.dumps(message_dict)
        await asyncio.gather(
            *[client.send(payload) for client in clients if client != sender_ws],
            return_exceptions=True
        )

async def handle_client(websocket):
    """
    Maneja el ciclo de vida de la conexión de un cliente en el chat.
    """
    clients.add(websocket)
    
    # Obtener información de la capa SSL/TLS para verificación
    ssl_object = websocket.transport.get_extra_info('ssl_object')
    client_address = websocket.remote_address
    
    print(f"\n[+] Nueva conexión establecida desde {client_address[0]}:{client_address[1]}")
    if ssl_object:
        version = ssl_object.version()
        cipher = ssl_object.cipher()
        print(f"    [TLS 1.3] Protocolo: {version}")
        print(f"    [TLS 1.3] Suite de cifrado: {cipher[0]} ({cipher[2]} bits)")
    else:
        print("    [ALERTA] Conexión no segura (Sin SSL/TLS)")

    try:
        # Cifrar el mensaje de bienvenida a nivel de aplicación
        welcome_text = "Bienvenido al chat seguro de Animoon (Doble Cifrado: TLS 1.3 + AES-GCM activo)."
        encrypted_welcome = aes_cipher.encrypt(welcome_text)
        
        welcome_msg = {
            "sender": "System",
            "encrypted_message": encrypted_welcome,
            "system": True
        }
        await websocket.send(json.dumps(welcome_msg))

        # Escuchar mensajes del cliente
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                sender = data.get("sender", "Usuario Anónimo")
                enc_data = data.get("encrypted_message")
                
                if not enc_data:
                    print(f"[-] Mensaje rechazado de {sender}: no contiene cifrado de aplicación.")
                    continue
                
                print(f"\n--- MENSAJE RECIBIDO DE {sender} ---")
                print("[Capa 1: TLS 1.3] Mensaje recibido a través del túnel seguro de transporte.")
                print("[Capa 2: Aplicación] Datos cifrados recibidos:")
                print(f"    Ciphertext B64: {enc_data.get('ciphertext_b64')}")
                print(f"    Nonce B64:      {enc_data.get('nonce_b64')}")
                print(f"    Tag B64:        {enc_data.get('tag_b64')}")
                
                # Descifrar en memoria para simular el análisis del modelo de moderación BERT
                try:
                    plaintext = aes_cipher.decrypt(
                        enc_data.get('ciphertext_b64'),
                        enc_data.get('nonce_b64'),
                        enc_data.get('tag_b64')
                    )
                    print(f"[Capa 2: Memoria del Servidor] Descifrado exitoso: '{plaintext}'")
                except ValueError as crypto_err:
                    print(f"[ERROR Criptográfico] Fallo de integridad o manipulación detectada: {crypto_err}")
                    continue

                # Retransmitir el mensaje cifrado tal cual a los demás participantes (Zero-Trust)
                broadcast_msg = {
                    "sender": sender,
                    "encrypted_message": enc_data,
                    "system": False
                }
                await broadcast(broadcast_msg, websocket)
                
            except json.JSONDecodeError:
                print(f"[-] Error decodificando JSON del cliente {client_address}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"[-] Conexión cerrada con {client_address}: {e}")
    finally:
        clients.remove(websocket)
        print(f"[-] Conexión finalizada para {client_address[0]}:{client_address[1]}")

async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(base_dir, "server.crt")
    key_path = os.path.join(base_dir, "server.key")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("[ERROR] No se encontraron los archivos de certificado o llave.")
        print("Por favor ejecuta 'generate_certs.py' antes de iniciar el servidor.")
        return

    # Configuración estricta del contexto SSL para TLS 1.3
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    
    print("=== INICIANDO SERVIDOR DE CHAT SEGURO DE ANIMOON (DOBLE CIFRADO) ===")
    print("Transporte: TLS 1.3 strictly enforced")
    print("Aplicación: AES-256-GCM (Motor del proyecto)")
    print("Puerto de escucha: 8765")
    
    async with websockets.serve(
        handle_client,
        "localhost",
        8765,
        ssl=ssl_context
    ):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[+] Servidor detenido por el usuario.")
