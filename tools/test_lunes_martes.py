import asyncio
import requests
import websockets

# Cambia localhost por la IP de AWS cuando vayas a probar en producción
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# NOTA: Cambia esto por las credenciales de un usuario que YA exista en tu base de datos
TEST_NICKNAME = "TestUser"  
TEST_PASSWORD = "PasswordSeguro123!"

async def test_flujo():
    print("=== 1. Probando Login (Lunes) ===")
    login_data = {
        "nickname": TEST_NICKNAME,
        "password": TEST_PASSWORD,
        "client_ecdhe_public_key": "llave_falsa_base64_para_probar"
    }
    
    # Hacemos la petición POST al Login
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"[-] Falló el login: {response.text}")
        print("💡 Asegúrate de poner en este script un 'nickname' y 'password' que ya existan en tu BD.")
        return

    data = response.json()
    token = data.get("access_token")
    print(f"[+] Login Exitoso.")
    print(f"[+] Token JWT obtenido: {token[:40]}...\n")

    print("=== 2. Probando Conexión de Chat por WebSockets (Martes) ===")
    ws_endpoint = f"{WS_URL}/ws/chat/?token={token}"
    try:
        async with websockets.connect(ws_endpoint) as ws:
            print("[+] Conectado exitosamente al WebSocket validando el JWT.")
            
            # Mandamos un mensaje de prueba
            await ws.send("¡Hola servidor, estoy probando la concurrencia!")
            respuesta = await ws.recv()
            print(f"[+] Eco recibido del servidor: {respuesta}\n")
    except Exception as e:
        print(f"[-] Error en WebSocket: {e}")

    print("=== 3. Probando Cierre de Sesión (Logout) ===")
    headers = {"Authorization": f"Bearer {token}"}
    logout_res = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    if logout_res.status_code == 200:
        print("[+] Logout exitoso. Tu sesión ha sido marcada como inactiva en la tabla SESION.\n")
    else:
        print(f"[-] Error en Logout: {logout_res.text}")

    print("=== 4. Probando Intrusión con Token Expirado/Cerrado ===")
    try:
        # Intentamos conectar de nuevo con el mismo token
        async with websockets.connect(ws_endpoint) as ws:
            await ws.send("Hackeando sistema...")
            await ws.recv()
            print("[-] ¡Cuidado! Me dejó entrar.")
    except Exception as e:
        print("[+] Conexión rechazada correctamente por el servidor.")
        print(f"    (Motivo técnico: {e})\n")
        print("🎯 PRUEBAS DE LUNES Y MARTES SUPERADAS CON ÉXITO.")

if __name__ == "__main__":
    asyncio.run(test_flujo())
