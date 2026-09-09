import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
import os
import sys

# Agregar ruta base
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from security.eddsa.eddsa_signer import EdDSASigner

# Inicializar signer global para usar la llave PEM del entorno
signer = EdDSASigner()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Genera un JWT firmado con la llave Ed25519 (EdDSA).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24) # 24 horas por defecto
    
    to_encode.update({"exp": expire})
    
    # PyJWT permite firmar usando el objeto llave privada de cryptography
    encoded_jwt = jwt.encode(to_encode, signer.private_key, algorithm="EdDSA")
    return encoded_jwt

def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verifica un JWT utilizando la llave pública asociada.
    Retorna el payload si es válido, lanza error en caso contrario.
    """
    try:
        payload = jwt.decode(token, signer.public_key, algorithms=["EdDSA"])
        return payload
    except jwt.PyJWTError as e:
        raise ValueError(f"Token inválido: {e}")

def get_token_hash(token: str) -> str:
    """
    Genera un hash SHA-256 del token para almacenarlo de forma segura.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
