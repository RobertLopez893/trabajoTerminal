import asyncio
import websockets
import json
import sys

# Nota: Este script requiere tener corriendo el backend de FastAPI en el puerto 8000
# y necesitas proveer un token JWT válido (puedes sacarlo de la base de datos o haciendo login primero).

async def run_client(token, nickname, x_start, y_start):
    uri = f"ws://localhost:8000/api/env/ws?token={token}"
    
    try:
        print(f"[{nickname}] Conectando al entorno...")
        async with websockets.connect(uri) as websocket:
            print(f"[{nickname}] Conectado exitosamente.")
            
            # Recibir estado inicial
            initial_state = await websocket.recv()
            print(f"[{nickname}] Estado inicial recibido: {initial_state}")
            
            x = x_start
            y = y_start
            
            # Tarea para recibir mensajes
            async def receive_updates():
                try:
                    while True:
                        msg = await websocket.recv()
                        data = json.loads(msg)
                        if data.get("type") != "player_moved":
                            print(f"[{nickname}] Servidor -> {data}")
                        else:
                            # Imprimir solo si es otro jugador
                            print(f"[{nickname}] <- Movimiento: {data.get('nickname', 'Alguien')} está en ({data['x']:.2f}, {data['y']:.2f})")
                except websockets.exceptions.ConnectionClosed:
                    print(f"[{nickname}] Desconectado del servidor.")

            asyncio.create_task(receive_updates())
            
            # Bucle de envío de movimiento simulado
            try:
                for i in range(10):
                    await asyncio.sleep(1) # Simular 1 actualización por segundo
                    x += 0.5
                    y += 0.5
                    
                    move_cmd = {
                        "type": "move",
                        "x": x,
                        "y": y
                    }
                    print(f"[{nickname}] -> Moviendo a ({x:.2f}, {y:.2f})")
                    await websocket.send(json.dumps(move_cmd))
                    
                # Simular cambio de zona
                print(f"[{nickname}] -> Cambiando a zona: crateres_gigantes")
                await websocket.send(json.dumps({
                    "type": "change_zone",
                    "zona": "crateres_gigantes"
                }))
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                pass
                
    except Exception as e:
        print(f"[{nickname}] Error de conexión: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python env_client_test.py <token_jwt> [nickname_opcional]")
        sys.exit(1)
        
    token = sys.argv[1]
    nickname = sys.argv[2] if len(sys.argv) > 2 else "TestUser"
    
    asyncio.run(run_client(token, nickname, 10.0, 10.0))
