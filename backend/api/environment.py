import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database import models
from backend.api.jwt_manager import verify_access_token, get_token_hash

router = APIRouter(prefix="/api/env", tags=["environment"])

import asyncio
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        # Estructura: {"nombre_zona": {"usuario_id": {"websocket": ws, "x": 0, "y": 0, "nickname": "...", "avatar": {...}}}}
        self.zonas: Dict[str, Dict[str, Any]] = {
            "base_principal": {},
            "crateres_gigantes": {},
            "aldea_lunatica": {},
            "lado_oscuro_de_la_luna": {}
        }
        self.loop_task = None

    def start_loop_if_needed(self):
        if self.loop_task is None:
            self.loop_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        CHUNK_SIZE = 100
        while True:
            await asyncio.sleep(0.1) # Tick de 10 Hz
            for zona, usuarios in self.zonas.items():
                if not usuarios:
                    continue
                
                # 1. Agrupar jugadores por chunks (Partición Espacial AoI)
                chunks = defaultdict(list)
                for uid, data in usuarios.items():
                    cx = int(data["x"] // CHUNK_SIZE)
                    cy = int(data["y"] // CHUNK_SIZE)
                    data["chunk"] = (cx, cy)
                    chunks[(cx, cy)].append({
                        "usuario_id": uid,
                        "nickname": data["nickname"],
                        "avatar": data["avatar"],
                        "x": data["x"],
                        "y": data["y"]
                    })
                
                # 2. Enviar a cada jugador los datos de su chunk y vecinos
                for uid, data in usuarios.items():
                    ws = data["websocket"]
                    cx, cy = data["chunk"]
                    
                    visible_players = []
                    for i in [-1, 0, 1]:
                        for j in [-1, 0, 1]:
                            visible_players.extend(chunks.get((cx + i, cy + j), []))
                    
                    # Remover al propio jugador para no enviarle su propio eco
                    visible_players = [p for p in visible_players if p["usuario_id"] != uid]
                    
                    if visible_players:
                        try:
                            await ws.send_json({
                                "type": "tick",
                                "zona": zona,
                                "players": visible_players
                            })
                        except Exception:
                            pass

    async def connect(self, websocket: WebSocket, usuario_id: str, nickname: str, avatar: dict, zona_inicial: str = "base_principal"):
        await websocket.accept()
        self.start_loop_if_needed()
        if zona_inicial not in self.zonas:
            zona_inicial = "base_principal"
            
        self.zonas[zona_inicial][usuario_id] = {
            "websocket": websocket,
            "x": 0.0,
            "y": 0.0,
            "nickname": nickname,
            "avatar": avatar
        }
        
        # Ya no enviamos "player_joined" porque el "tick" lo actualizará.
        # Solo enviamos el estado inicial de bienvenida
        await websocket.send_json({
            "type": "zone_state",
            "zona": zona_inicial,
            "players": [] # El tick rellenará la pantalla en 100ms
        })

    def disconnect(self, websocket: WebSocket, usuario_id: str, zona: str):
        if zona in self.zonas and usuario_id in self.zonas[zona]:
            del self.zonas[zona][usuario_id]
            
    async def change_zone(self, websocket: WebSocket, usuario_id: str, old_zona: str, new_zona: str):
        if old_zona in self.zonas and usuario_id in self.zonas[old_zona]:
            player_data = self.zonas[old_zona][usuario_id]
            del self.zonas[old_zona][usuario_id]
            
            if new_zona not in self.zonas:
                new_zona = "base_principal"
                
            player_data["x"] = 0.0
            player_data["y"] = 0.0
            self.zonas[new_zona][usuario_id] = player_data
            
            await websocket.send_json({
                "type": "zone_state",
                "zona": new_zona,
                "players": []
            })
            return new_zona
        return old_zona

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


from backend.database.db import SessionLocal

@router.websocket("/ws")
async def websocket_environment(websocket: WebSocket, token: str):
    """
    Endpoint WebSocket para sincronización del entorno multijugador.
    El cliente debe enviar el token JWT como query parameter: /api/env/ws?token=XYZ
    """
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Obtener el avatar del usuario
        avatar_record = db.query(models.Avatar).filter(models.Avatar.usuario_id == user.id).first()
        avatar_json = avatar_record.avatar_config_json if avatar_record else {"especie": "desconocido", "color": "desconocido"}
        
        user_id = user.id
        nickname = user.nickname
    finally:
        db.close() # LIBERAR LA CONEXIÓN INMEDIATAMENTE AL POOL

    zona_actual = "base_principal"
    
    await manager.connect(websocket, user_id, nickname, avatar_json, zona_actual)

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
                    # Ya NO hacemos broadcast aquí. El game_loop se encarga de enviarlo en el próximo "tick"
                    
            elif msg_type == "change_zone":
                nueva_zona = data.get("zona")
                if nueva_zona in manager.zonas:
                    zona_actual = await manager.change_zone(websocket, user.id, zona_actual, nueva_zona)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id, zona_actual)
        # Ya no enviamos "player_left" al instante, simplemente desaparece del "tick"

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
