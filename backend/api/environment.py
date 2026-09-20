import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database import models
from backend.api.jwt_manager import verify_access_token, get_token_hash

router = APIRouter(prefix="/api/env", tags=["environment"])

class ConnectionManager:
    def __init__(self):
        # Estructura: {"nombre_zona": {"usuario_id": {"websocket": ws, "x": 0, "y": 0, "nickname": "...", "avatar": {...}}}}
        self.zonas: Dict[str, Dict[str, Any]] = {
            "base_principal": {},
            "crateres_gigantes": {},
            "aldea_lunatica": {},
            "lado_oscuro_de_la_luna": {}
        }

    async def connect(self, websocket: WebSocket, usuario_id: str, nickname: str, avatar: dict, zona_inicial: str = "base_principal"):
        await websocket.accept()
        if zona_inicial not in self.zonas:
            zona_inicial = "base_principal"
            
        self.zonas[zona_inicial][usuario_id] = {
            "websocket": websocket,
            "x": 0.0,
            "y": 0.0,
            "nickname": nickname,
            "avatar": avatar
        }
        
        # Notificar a los demás en la zona que alguien entró
        await self.broadcast_zone(zona_inicial, {
            "type": "player_joined",
            "usuario_id": usuario_id,
            "nickname": nickname,
            "avatar": avatar,
            "x": 0.0,
            "y": 0.0
        }, exclude_ws=websocket)
        
        # Enviar al jugador la lista de todos los que ya están en la zona
        current_players = []
        for uid, data in self.zonas[zona_inicial].items():
            if uid != usuario_id:
                current_players.append({
                    "usuario_id": uid,
                    "nickname": data["nickname"],
                    "avatar": data["avatar"],
                    "x": data["x"],
                    "y": data["y"]
                })
        
        await websocket.send_json({
            "type": "zone_state",
            "zona": zona_inicial,
            "players": current_players
        })

    def disconnect(self, websocket: WebSocket, usuario_id: str, zona: str):
        if zona in self.zonas and usuario_id in self.zonas[zona]:
            del self.zonas[zona][usuario_id]
            
    async def change_zone(self, websocket: WebSocket, usuario_id: str, old_zona: str, new_zona: str):
        if old_zona in self.zonas and usuario_id in self.zonas[old_zona]:
            # Guardar datos actuales
            player_data = self.zonas[old_zona][usuario_id]
            # Eliminar de zona antigua
            del self.zonas[old_zona][usuario_id]
            # Notificar salida
            await self.broadcast_zone(old_zona, {
                "type": "player_left",
                "usuario_id": usuario_id
            })
            
            # Resetear coordenadas y añadir a nueva zona
            if new_zona not in self.zonas:
                new_zona = "base_principal"
                
            player_data["x"] = 0.0
            player_data["y"] = 0.0
            self.zonas[new_zona][usuario_id] = player_data
            
            # Notificar entrada
            await self.broadcast_zone(new_zona, {
                "type": "player_joined",
                "usuario_id": usuario_id,
                "nickname": player_data["nickname"],
                "avatar": player_data["avatar"],
                "x": 0.0,
                "y": 0.0
            }, exclude_ws=websocket)
            
            # Enviar nuevo estado
            current_players = []
            for uid, data in self.zonas[new_zona].items():
                if uid != usuario_id:
                    current_players.append({
                        "usuario_id": uid,
                        "nickname": data["nickname"],
                        "avatar": data["avatar"],
                        "x": data["x"],
                        "y": data["y"]
                    })
            await websocket.send_json({
                "type": "zone_state",
                "zona": new_zona,
                "players": current_players
            })
            return new_zona
        return old_zona

    async def broadcast_zone(self, zona: str, message: dict, exclude_ws: WebSocket = None):
        if zona in self.zonas:
            for uid, data in self.zonas[zona].items():
                ws = data["websocket"]
                if ws != exclude_ws:
                    try:
                        await ws.send_json(message)
                    except Exception:
                        pass # Si falla, se manejará en el bucle principal de desconexión

manager = ConnectionManager()

def authenticate_ws_token(token: str, db: Session) -> models.Usuario:
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
    except Exception:
        return None

    # Validar sesión
    token_hash = get_token_hash(token)
    sesion = db.query(models.Sesion).filter(
        models.Sesion.session_token_hash == token_hash,
        models.Sesion.is_active == True
    ).first()
    
    if not sesion:
        return None

    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user or not user.is_active or user.is_banned:
        return None
        
    return user


@router.websocket("/ws")
async def websocket_environment(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    Endpoint WebSocket para sincronización del entorno multijugador.
    El cliente debe enviar el token JWT como query parameter: /api/env/ws?token=XYZ
    """
    user = authenticate_ws_token(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Obtener el avatar del usuario
    avatar_record = db.query(models.Avatar).filter(models.Avatar.usuario_id == user.id).first()
    avatar_json = avatar_record.avatar_config_json if avatar_record else {"especie": "desconocido", "color": "desconocido"}

    zona_actual = "base_principal"
    
    await manager.connect(websocket, user.id, user.nickname, avatar_json, zona_actual)

    try:
        while True:
            # Esperar mensajes de movimiento o cambio de zona
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "move":
                # Actualizar posición en memoria
                if user.id in manager.zonas[zona_actual]:
                    manager.zonas[zona_actual][user.id]["x"] = data.get("x", 0.0)
                    manager.zonas[zona_actual][user.id]["y"] = data.get("y", 0.0)
                    
                    # Retransmitir a los demás en la zona
                    await manager.broadcast_zone(zona_actual, {
                        "type": "player_moved",
                        "usuario_id": user.id,
                        "x": data.get("x", 0.0),
                        "y": data.get("y", 0.0)
                    }, exclude_ws=websocket)
                    
            elif msg_type == "change_zone":
                nueva_zona = data.get("zona")
                if nueva_zona in manager.zonas:
                    zona_actual = await manager.change_zone(websocket, user.id, zona_actual, nueva_zona)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id, zona_actual)
        await manager.broadcast_zone(zona_actual, {
            "type": "player_left",
            "usuario_id": user.id
        })

@router.get("/active-users")
def get_active_users():
    """
    Devuelve un resumen de los usuarios conectados en cada zona.
    """
    resultado = {}
    for zona, usuarios in manager.zonas.items():
        resultado[zona] = []
        for uid, data in usuarios.items():
            resultado[zona].append({
                "usuario_id": uid,
                "nickname": data.get("nickname"),
                "x": data.get("x"),
                "y": data.get("y")
            })
    return {"status": "success", "zonas": resultado}
