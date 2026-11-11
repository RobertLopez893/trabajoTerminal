import json
import os
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import redis.asyncio as aioredis

from backend.database.db import get_db
from backend.database import models
from backend.api.jwt_manager import verify_access_token, get_token_hash
from backend.api.deps import get_current_user

router = APIRouter(prefix="/api/env", tags=["environment"])

import asyncio
from collections import defaultdict

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

async def listen_chat_invitations(conn_manager):
    """Escucha invitaciones de chat desde Redis y las envía por WS al jugador en el mundo."""
    try:
        r = aioredis.from_url(REDIS_URL, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("channel:chat_invitations")
        async for raw_event in pubsub.listen():
            if raw_event["type"] == "message":
                try:
                    data = json.loads(raw_event["data"])
                    target_id = data.get("target_user_id")
                    if target_id:
                        await conn_manager.send_chat_invitation(
                            target_user_id=target_id,
                            sender_id=data.get("from_user_id"),
                            sender_nickname=data.get("from_nickname", "Un jugador"),
                            sender_species=data.get("from_species", "gato"),
                            sender_color=data.get("from_color", "azul")
                        )
                except Exception:
                    pass
    except Exception:
        pass

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
        self.invitations_task = None

    def start_loop_if_needed(self):
        if self.loop_task is None:
            self.loop_task = asyncio.create_task(self.game_loop())
            self.invitations_task = asyncio.create_task(listen_chat_invitations(self))

    async def send_chat_invitation(self, target_user_id: str, sender_id: str, sender_nickname: str, sender_species: str, sender_color: str) -> bool:
        """Busca al usuario objetivo en cualquiera de las zonas y le envía el evento de invitación."""
        for zona, usuarios in self.zonas.items():
            if target_user_id in usuarios:
                ws = usuarios[target_user_id].get("websocket")
                if ws:
                    try:
                        await ws.send_json({
                            "type": "chat_invitation",
                            "from_user_id": sender_id,
                            "from_nickname": sender_nickname,
                            "from_species": sender_species,
                            "from_color": sender_color
                        })
                        return True
                    except Exception:
                        pass
        return False

    async def game_loop(self):
        CHUNK_SIZE = 10000
        while True:
            await asyncio.sleep(0.1) # Tick de 10 Hz
            for zona, usuarios in self.zonas.items():
                if not usuarios:
                    continue
                
                # Agrupar jugadores por chunks (Partición Espacial AoI)
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
                
                # Enviar a cada jugador los datos de su chunk y vecinos
                for uid, data in usuarios.items():
                    ws = data["websocket"]
                    cx, cy = data["chunk"]
                    
                    visible_players = []
                    for i in [-1, 0, 1]:
                        for j in [-1, 0, 1]:
                            visible_players.extend(chunks.get((cx + i, cy + j), []))
                    
                    # Remover al propio jugador para no enviarle su propio eco
                    # No removemos al propio jugador para que se vea a s mismo
                    # visible_players = [p for p in visible_players if p["usuario_id"] != uid]
                    
                    if visible_players:
                        try:
                            await ws.send_json({
                                "type": "tick",
                                "zona": zona,
                                "players": visible_players
                            })
                        except Exception:
                            pass

    async def connect(self, websocket: WebSocket, usuario_id: str, nickname: str, avatar: dict, zona_inicial: str = "base_principal", x: float = 0.0, y: float = 0.0):
        await websocket.accept()
        self.start_loop_if_needed()
        if zona_inicial not in self.zonas:
            zona_inicial = "base_principal"
            
        # Remover al usuario de cualquier zona previa para evitar duplicados o usuarios fantasma
        for z in list(self.zonas.keys()):
            if usuario_id in self.zonas[z]:
                del self.zonas[z][usuario_id]

        self.zonas[zona_inicial][usuario_id] = {
            "websocket": websocket,
            "x": x,
            "y": y,
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

    def disconnect(self, websocket: WebSocket, usuario_id: str, zona: str = None):
        if zona and zona in self.zonas and usuario_id in self.zonas[zona]:
            del self.zonas[zona][usuario_id]
        else:
            for z in list(self.zonas.keys()):
                if usuario_id in self.zonas[z]:
                    del self.zonas[z][usuario_id]
            
    async def change_zone(self, websocket: WebSocket, usuario_id: str, old_zona: str, new_zona: str, x: float = 0.0, y: float = 0.0):
        if new_zona not in self.zonas:
            new_zona = "base_principal"

        # Extraer player_data de la zona previa (o de cualquier zona donde se encuentre)
        player_data = None
        for z in list(self.zonas.keys()):
            if usuario_id in self.zonas[z]:
                player_data = self.zonas[z].pop(usuario_id, None)
                break
                
        if player_data is not None:
            player_data["websocket"] = websocket
            player_data["x"] = x
            player_data["y"] = y
            self.zonas[new_zona][usuario_id] = player_data
        
        await websocket.send_json({
            "type": "zone_state",
            "zona": new_zona,
            "players": []
        })
        return new_zona


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
async def websocket_environment(
    websocket: WebSocket,
    token: str,
    zona: str = "base_principal",
    x: float = 0.0,
    y: float = 0.0
):
    """
    Endpoint WebSocket para sincronización del entorno multijugador.
    El cliente puede enviar el token JWT y la zona: /api/env/ws?token=XYZ&zona=crateres_gigantes
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

    zona_actual = zona if zona in manager.zonas else "base_principal"
    
    await manager.connect(websocket, user_id, nickname, avatar_json, zona_actual, x, y)

    try:
        while True:
            # Esperar mensajes de movimiento o cambio de zona
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "move":
                # Actualizar posición en memoria
                if zona_actual in manager.zonas and user_id in manager.zonas[zona_actual]:
                    try:
                        manager.zonas[zona_actual][user_id]["x"] = float(data.get("x", 0.0))
                        manager.zonas[zona_actual][user_id]["y"] = float(data.get("y", 0.0))
                    except (ValueError, TypeError):
                        pass
                    
            elif msg_type == "change_zone":
                nueva_zona = data.get("zona")
                try:
                    target_x = float(data.get("x", 0.0))
                    target_y = float(data.get("y", 0.0))
                except (ValueError, TypeError):
                    target_x = 0.0
                    target_y = 0.0
                if nueva_zona in manager.zonas:
                    zona_actual = await manager.change_zone(websocket, user_id, zona_actual, nueva_zona, target_x, target_y)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, zona_actual)
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


class ChatInviteRequest(BaseModel):
    target_user_id: str


@router.post("/invite-chat")
async def invite_to_chat(
    req: ChatInviteRequest,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Envía una invitación/notificación de chat a otro usuario en el mundo en tiempo real.
    """
    avatar_record = db.query(models.Avatar).filter(models.Avatar.usuario_id == current_user.id).first()
    avatar_cfg = avatar_record.avatar_config_json if avatar_record else {}
    species = avatar_cfg.get("especie", "gato")
    color = avatar_cfg.get("color", "azul")

    notified = await manager.send_chat_invitation(
        target_user_id=req.target_user_id,
        sender_id=current_user.id,
        sender_nickname=current_user.nickname,
        sender_species=species,
        sender_color=color
    )
    return {"status": "success", "notified": notified}



