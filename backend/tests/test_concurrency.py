import asyncio
import uuid
import sys
import os
import json
from datetime import datetime, timedelta

# Agregar la ruta del backend al sys.path para poder importar sus módulos
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.append(backend_path)

try:
    from backend.database.db import SessionLocal
    from backend.database import models
    from backend.api.jwt_manager import create_access_token, get_token_hash
except ImportError as e:
    print(f"Error importando módulos del backend: {e}")
    sys.exit(1)

try:
    import websockets
except ImportError:
    print("\n[!] Falta la librería websockets. Instálala con: pip install websockets\n")
    sys.exit(1)

NUM_USERS = 1000

async def connect_user(token: str, user_id: str, delay: float):
    await asyncio.sleep(delay) # Escalonar las conexiones para no ahogar el servidor de golpe
    url = f"ws://localhost:8000/api/env/ws?token={token}"
    try:
        async with websockets.connect(url, ping_interval=60, ping_timeout=120) as ws:
            print(f"[+] Bot {user_id[-4:]} conectado.")
            # Mantener la conexión abierta y simular que se mueven aleatoriamente cada 10 segundos
            import random
            while True:
                await asyncio.sleep(random.uniform(5, 15))
                move_payload = {
                    "type": "move", 
                    "x": random.uniform(-10.0, 10.0), 
                    "y": random.uniform(-10.0, 10.0)
                }
                await ws.send(json.dumps(move_payload))
    except Exception as e:
        print(f"[-] Error en WS {user_id[-4:]}: {e}")

async def main():
    print(f"== Generando {NUM_USERS} bots de prueba en la base de datos ==")
    db = SessionLocal()
    
    tokens = []
    bots_generados = []
    
    try:
        for i in range(NUM_USERS):
            user_id = str(uuid.uuid4())
            nickname = f"Bot_Test_{i}"
            bots_generados.append(user_id)
            
            # Crear usuario falso
            user = models.Usuario(
                id=user_id,
                nickname=nickname,
                telefono_cifrado="mock",
                telefono_iv_nonce="mock",
                telefono_tag="mock",
                argon2id_hash="mock",
                salt="mock",
                is_verified=True,
                is_active=True
            )
            db.add(user)
            db.flush() # <--- Fuerza a insertar el Usuario antes que el Avatar
            
            # Crear avatar
            avatar = models.Avatar(
                id=str(uuid.uuid4()),
                usuario_id=user_id,
                avatar_config_json={"especie": "conejo", "color": "azul"}
            )
            db.add(avatar)
            
            # Crear JWT
            token = create_access_token(data={"sub": user_id, "nickname": nickname})
            token_hash = get_token_hash(token)
            
            # Crear sesion en BD
            sesion = models.Sesion(
                id=str(uuid.uuid4()),
                usuario_id=user_id,
                ecdhe_public_key_ephemeral="mock",
                session_token_hash=token_hash,
                expires_at=datetime.utcnow() + timedelta(hours=1),
                is_active=True
            )
            db.add(sesion)
            
            tokens.append((token, user_id))
            
            # Commit por bloques
            if i > 0 and i % 100 == 0:
                db.commit()
                print(f"  ... {i} bots creados")
                
        db.commit()
        print(f"== {NUM_USERS} bots creados exitosamente. Iniciando asalto al servidor ==")
        
    except Exception as e:
        print("Error insertando en DB:", e)
        db.rollback()
        return
    finally:
        db.close()

    # Lanzar 1000 tareas asíncronas, espaciadas por 100 milisegundos
    tasks = [connect_user(tokens[i][0], tokens[i][1], delay=i * 0.1) for i in range(NUM_USERS)]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nPrueba detenida por el usuario. Limpiando la base de datos...")
        db = SessionLocal()
        db.query(models.Usuario).filter(models.Usuario.nickname.like("Bot_Test_%")).delete(synchronize_session=False)
        db.commit()
        db.close()
        print("Limpieza completada.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
