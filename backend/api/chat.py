from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
from backend.api.jwt_manager import verify_access_token

router = APIRouter(prefix="/ws/chat", tags=["chat"])

class ConnectionManager:
    def __init__(self):
        # Mapea usuario_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"[+] Usuario {user_id} conectado a los WebSockets.")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"[-] Usuario {user_id} desconectado de los WebSockets.")

    async def send_personal_message(self, message: str, user_id: str):
        """ Envía mensaje a un usuario específico si está en línea """
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        """ Envía mensaje a todos (generalmente no se usará en chats 1 a 1, pero es útil) """
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Endpoint principal para WebSockets. 
    Se espera que el cliente envíe el token JWT como query parameter, ej:
    ws://dominio/ws/chat/?token=eyJhb...
    """
    try:
        # Autenticación basada en el token EdDSA
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008)
            return
            
    except Exception as e:
        print(f"Error de autenticación WebSocket: {e}")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    
    try:
        # Ciclo de vida del WebSocket
        while True:
            # Aquí posteriormente recibiremos los payloads AES-GCM
            data = await websocket.receive_text()
            # Por ahora, un simple eco para pruebas de vida
            await manager.send_personal_message(f"Eco del Servidor: {data}", user_id)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
