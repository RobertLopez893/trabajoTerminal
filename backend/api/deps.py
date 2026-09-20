from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.db import get_db
from backend.database import models
from backend.api.jwt_manager import verify_access_token, get_token_hash

security = HTTPBearer()

from datetime import timedelta

def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Sesion:
    """Devuelve la sesión actual, verificando expiración de inactividad (Sliding Session)"""
    token = credentials.credentials
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token no contiene ID de usuario.")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    token_hash = get_token_hash(token)
    sesion = db.query(models.Sesion).filter(
        models.Sesion.session_token_hash == token_hash,
        models.Sesion.is_active == True
    ).first()
    
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión inválida o revocada.")
        
    # Validar sliding expiration por inactividad
    if sesion.expires_at < datetime.utcnow():
        sesion.is_active = False
        db.commit()
        raise HTTPException(status_code=401, detail="Sesión expirada por inactividad.")

    # Renovar expiración 15 minutos hacia el futuro
    sesion.expires_at = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
        
    return sesion

def get_current_user(
    sesion: models.Sesion = Depends(get_current_session),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """Devuelve el usuario actual basándose en la sesión activa"""
    user = db.query(models.Usuario).filter(models.Usuario.id == sesion.usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not user.is_active or user.is_banned:
        raise HTTPException(status_code=403, detail="Usuario inactivo o bloqueado.")

    return user
