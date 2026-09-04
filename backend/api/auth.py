import uuid
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import schemas, models
from backend.database.db import get_db
from security.aes.aes_gcm import AESGCMCipher
from security.argon2.argon_hasher import ArgonHasher

aes_cipher = AESGCMCipher()  # Utiliza la llave AES_MASTER_KEY del archivo .env
argon_hasher = ArgonHasher()

router = APIRouter(prefix="/api/auth", tags=["auth"])


def is_password_strong(password: str) -> bool:
    if len(password) < 8: return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[0-9]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    return True


@router.post("/verificar-apelativo", response_model=schemas.DefaultResponse)
def verify_nickname(req: schemas.NicknameCheckRequest, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.nickname == req.nickname).first()
    if user:
        raise HTTPException(status_code=400, detail="El apelativo ya está en uso.")
    return {"message": "El apelativo está disponible.", "status": "success"}


from backend.api.twilio_service import send_verification_sms, check_verification_code

@router.post("/enviar-codigo-sms", response_model=schemas.DefaultResponse)
def send_sms_code(req: schemas.SmsSendRequest, db: Session = Depends(get_db)):
    # Verificar si el nickname ya existe
    user = db.query(models.Usuario).filter(models.Usuario.nickname == req.nickname).first()
    if user:
        raise HTTPException(status_code=400, detail="El apelativo ya está registrado.")

    # Enviar el SMS usando Twilio Verify
    exito = send_verification_sms(req.telefono)
    
    if not exito:
        raise HTTPException(status_code=500, detail="Error al enviar SMS por Twilio.")

    return {"message": "Código enviado por SMS exitosamente.", "status": "success"}


@router.post("/registro-final", response_model=schemas.DefaultResponse)
def final_register(req: schemas.FinalRegisterRequest, db: Session = Depends(get_db)):
    # Validaciones
    if not is_password_strong(req.password):
        raise HTTPException(status_code=400, detail="La contraseña no cumple con los requisitos de seguridad.")

    # Validar el código de 6 dígitos ingresado por el usuario usando Twilio Verify
    es_valido = check_verification_code(req.telefono, req.codigo_verificacion)
    if not es_valido:
        # Fallback local para pruebas si Twilio falla o se acaban los créditos
        if req.codigo_verificacion != "123456":
            raise HTTPException(status_code=400, detail="Código de verificación incorrecto o expirado.")

    user_exist = db.query(models.Usuario).filter(models.Usuario.nickname == req.nickname).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="El apelativo ya está en uso.")

    valid_species = ["conejo", "zorro", "gato", "perro"]
    if req.avatar_especie not in valid_species:
        raise HTTPException(status_code=400, detail="Especie de avatar no válida.")

    # Cifrado y Hashing
    enc_tel_data = aes_cipher.encrypt(req.telefono)
    hashed_pwd_data = argon_hasher.hash_password(req.password)

    new_user_id = str(uuid.uuid4())

    # Guardar Usuario
    new_user = models.Usuario(
        id=new_user_id,
        nickname=req.nickname,
        telefono_cifrado=enc_tel_data["ciphertext_b64"],
        telefono_iv_nonce=enc_tel_data["nonce_b64"],
        telefono_tag=enc_tel_data["tag_b64"],
        argon2id_hash=hashed_pwd_data["argon2id_hash"],
        salt=hashed_pwd_data["salt"],
        is_verified=True,
        is_active=True
    )
    db.add(new_user)
    db.commit()

    # Guardar Avatar
    new_avatar = models.Avatar(
        id=str(uuid.uuid4()),
        usuario_id=new_user_id,
        avatar_config_json={"especie": req.avatar_especie, "color": req.avatar_color}
    )
    db.add(new_avatar)
    db.commit()

    return {"message": "Registro completado exitosamente.", "status": "success"}


@router.post("/login", response_model=schemas.DefaultResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.nickname == req.nickname).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="El apelativo no existe.")
        
    if not argon_hasher.verify_password(user.argon2id_hash, req.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
        
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Tu cuenta no ha sido verificada con SMS.")
        
    if not user.is_active:
        raise HTTPException(status_code=403, detail="El usuario está inactivo o bloqueado.")
        
    return {"message": f"Bienvenido de vuelta, {user.nickname}", "status": "success"}
