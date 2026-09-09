from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.db import get_db
from backend.database import models
from backend.api.jwt_manager import verify_access_token, get_token_hash

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Usuario:
    token = credentials.credentials
    
    try:
        # Verificar firma EdDSA y expiración
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token no contiene ID de usuario.")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    # Verificar que el token esté registrado y activo en la tabla SESION
    token_hash = get_token_hash(token)
    sesion = db.query(models.Sesion).filter(
        models.Sesion.session_token_hash == token_hash,
        models.Sesion.is_active == True,
        models.Sesion.expires_at > datetime.utcnow()
    ).first()
    
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida, revocada o expirada."
        )

    # Buscar al usuario
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not user.is_active or user.is_banned:
        raise HTTPException(status_code=403, detail="Usuario inactivo o bloqueado.")

    return user

def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Sesion:
    """Devuelve la sesión actual en caso de que necesitemos la llave ECDHE"""
    token = credentials.credentials
    token_hash = get_token_hash(token)
    
    sesion = db.query(models.Sesion).filter(
        models.Sesion.session_token_hash == token_hash,
        models.Sesion.is_active == True
    ).first()
    
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión inválida")
        
    return sesion
