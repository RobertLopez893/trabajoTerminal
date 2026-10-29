import os
import sys
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

# Inclusión de rutas del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.database.db import get_db, get_db_auditoria
from backend.database import models, schemas
from backend.database.models_auditoria import LogAuditoria
from backend.api.jwt_manager import create_access_token, verify_access_token
from security.aes.aes_gcm import AESGCMCipher
from backend.api.twilio_service import send_notification_sms

logger = logging.getLogger("AppealsAPI")
aes_cipher = AESGCMCipher()

router = APIRouter(prefix="/api/admin", tags=["admin_appeals"])

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin.animoon")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminDemo#2026")

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def formatear_fecha_es(fecha: Optional[datetime]) -> str:
    if not fecha:
        return "Fecha no disponible"
    mes_nombre = MESES_ES[fecha.month - 1]
    return f"{fecha.day} de {mes_nombre} de {fecha.year} · {fecha.strftime('%H:%M')}"


def reactivar_usuario_en_redis(usuario_id: str):
    """Limpia el ID de la lista negra 'banned_users' en Redis si está disponible."""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.Redis.from_url(redis_url, decode_responses=True)
        r.srem("banned_users", usuario_id)
        logger.info(f"[REDIS] Usuario '{usuario_id}' retirado de 'banned_users'.")
    except Exception as e:
        logger.warning(f"[REDIS] No se pudo sincronizar desbaneo en Redis: {e}")


def get_current_admin(
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> str:
    """Valida que la petición cuente con un token administrativo firmado."""
    raw_token = None
    if x_admin_token:
        raw_token = x_admin_token.replace("Bearer ", "").strip()
    elif authorization and "Bearer " in authorization:
        raw_token = authorization.split("Bearer ")[1].strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autorización administrativa."
        )

    try:
        payload = verify_access_token(raw_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token administrativo inválido o expirado: {e}"
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador."
        )

    return payload.get("sub", ADMIN_USERNAME)


# =============================================================================
# ENDPOINTS ADMINISTRATIVOS (APELACIONES)
# =============================================================================

@router.post("/login", response_model=schemas.AdminLoginResponse)
def admin_login(req: schemas.AdminLoginRequest):
    """
    Autentica al administrador y expide un token JWT con rol 'admin'.
    """
    if req.username != ADMIN_USERNAME or req.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales administrativas incorrectas."
        )

    token = create_access_token(
        data={"sub": req.username, "role": "admin"},
        expires_delta=timedelta(hours=24)
    )

    return schemas.AdminLoginResponse(
        message="Inicio de sesión administrativo exitoso.",
        admin_token=token,
        expires_in_seconds=86400
    )


@router.get("/appeals", response_model=List[schemas.AdminAppealDto])
def list_appeals(
    admin_user: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
    db_audit: Session = Depends(get_db_auditoria)
):
    """
    Lista todas las apelaciones registradas en el sistema.
    Si la base de datos no tiene registros, entrega las apelaciones estándar de muestra
    para permitir la evaluación interactiva del panel.
    """
    apelaciones_db = db.query(models.Apelacion).order_by(models.Apelacion.created_at.desc()).all()

    items: List[schemas.AdminAppealDto] = []

    # Estado mapping
    status_map = {
        "PENDIENTE": "PENDING",
        "EN_REVISION": "IN_REVIEW",
        "APROBADA": "APPROVED",
        "ACEPTADA": "APPROVED",
        "RECHAZADA": "REJECTED"
    }

    for ap in apelaciones_db:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == ap.usuario_id).first()
        nickname = usuario.nickname if usuario else "Usuario Desconocido"

        # Buscar bloque para obtener tipo de incidencia
        bloque = db.query(models.BloqueAnalisis).filter(models.BloqueAnalisis.id == ap.bloque_id).first()
        incidencia = "Detección de Grooming (Nivel 2)"
        if bloque and bloque.fase_detectada:
            incidencia = bloque.fase_detectada

        # Buscar evidencia descifrada en auditoría si existe
        evidencia_txt = "Evidencia registrada en el bloque de análisis."
        log = db_audit.query(LogAuditoria).filter(LogAuditoria.bloque_id_ref == ap.bloque_id).first()
        if log and log.evidencia_cifrada and log.iv_nonce and log.tag_autenticacion:
            try:
                dec = aes_cipher.decrypt(log.evidencia_cifrada, log.iv_nonce, log.tag_autenticacion)
                evidencia_txt = dec.replace(" | ", "\n\n")
            except Exception:
                pass

        # Desencriptar o leer notas del administrador
        resolucion_txt = ""
        if ap.notas_admin_cifradas:
            resolucion_txt = ap.notas_admin_cifradas

        estado_api = status_map.get(ap.estado, ap.estado)
        t_res = int(ap.updated_at.timestamp() * 1000) if ap.updated_at and estado_api in ["APPROVED", "REJECTED"] else 0

        items.append(
            schemas.AdminAppealDto(
                id=ap.id,
                nickname=nickname,
                date=formatear_fecha_es(ap.created_at),
                incident=incidencia,
                explanation=ap.justificacion,
                evidence=evidencia_txt,
                status=estado_api,
                resolution=resolucion_txt,
                resolvedAt=t_res,
                resolvedBy=admin_user if estado_api in ["APPROVED", "REJECTED"] else ""
            )
        )

    # Si no hay apelaciones en BD, poblamos con las muestras de diseño
    if not items:
        muestras = [
            schemas.AdminAppealDto(
                id="AP-DEMO-003",
                nickname="CometaAzul",
                date="20 de octubre de 2026 · 16:40",
                incident="Solicitud de información personal",
                explanation="Creo que se interpretó mal mi pregunta. Quisiera que revisaran el contexto de la conversación.",
                evidence="16:35 · CometaAzul: ¿En qué escuela estás?\n\n16:36 · Jugador: Prefiero no compartir esa información.\n\n16:36 · CometaAzul: Está bien, podemos seguir con el juego.",
                status="PENDING"
            ),
            schemas.AdminAppealDto(
                id="AP-DEMO-002",
                nickname="ZorroEstelar",
                date="19 de octubre de 2026 · 18:20",
                incident="Invitación a una conversación externa",
                explanation="Quiero explicar lo que ocurrió antes de que se suspendiera mi cuenta y solicitar una revisión.",
                evidence="18:15 · ZorroEstelar: ¿Podemos hablar en otra aplicación?\n\n18:16 · Jugador: Prefiero quedarme en ANIMOON.\n\n18:16 · ZorroEstelar: De acuerdo.",
                status="PENDING"
            ),
            schemas.AdminAppealDto(
                id="AP-DEMO-001",
                nickname="LunaVioleta",
                date="18 de octubre de 2026 · 15:10",
                incident="Solicitud de mantener una conversación en secreto",
                explanation="Solicito que revisen los mensajes completos para aclarar lo que intentaba decir.",
                evidence="15:05 · LunaVioleta: No cuentes lo que estamos hablando.\n\n15:06 · Jugador: Si algo me preocupa, puedo hablar con mi tutor.\n\n15:06 · LunaVioleta: Entiendo.",
                status="PENDING"
            )
        ]
        return muestras

    return items


@router.post("/appeals/{appeal_id}/review", response_model=schemas.DefaultResponse)
def mark_appeal_in_review(
    appeal_id: str,
    admin_user: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Marca una apelación como 'EN_REVISION' ('IN_REVIEW').
    """
    ap = db.query(models.Apelacion).filter(models.Apelacion.id == appeal_id).first()
    if ap:
        ap.estado = "EN_REVISION"
        ap.updated_at = datetime.utcnow()
        db.commit()

    return schemas.DefaultResponse(
        message=f"Apelación {appeal_id} marcada en revisión.",
        status="success"
    )


@router.post("/appeals/{appeal_id}/resolve", response_model=schemas.AdminAppealDto)
def resolve_appeal(
    appeal_id: str,
    req: schemas.AdminAppealResolveRequest,
    admin_user: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
    db_audit: Session = Depends(get_db_auditoria)
):
    """
    Resuelve la apelación (Aprobar / Rechazar).
    Si es Aprobada, levanta inmediatamente el ban del usuario en PostgreSQL y Redis.
    """
    ap = db.query(models.Apelacion).filter(models.Apelacion.id == appeal_id).first()
    nuevo_estado = "APPROVED" if req.approved else "REJECTED"
    now_dt = datetime.utcnow()
    now_ms = int(now_dt.timestamp() * 1000)

    if ap:
        ap.estado = "APROBADA" if req.approved else "RECHAZADA"
        ap.notas_admin_cifradas = req.reason
        ap.updated_at = now_dt

        # Si se aprueba la apelación, desbanear al usuario
        usuario = None
        if ap.usuario_id:
            usuario = db.query(models.Usuario).filter(models.Usuario.id == ap.usuario_id).first()
            if req.approved and usuario:
                usuario.is_banned = False
                usuario.is_active = True
                reactivar_usuario_en_redis(usuario.id)
                logger.warning(f"✅ [APELACIÓN APROBADA] Usuario '{usuario.nickname}' ({usuario.id}) ha sido desbaneado.")

        db.commit()

        # RF-AP-08 / RF-AD-06: Notificar al tutor vía SMS dentro de 30 segundos tras el dictamen
        if usuario and usuario.telefono_cifrado:
            try:
                tel_plano = aes_cipher.decrypt(
                    usuario.telefono_cifrado,
                    usuario.telefono_iv_nonce,
                    usuario.telefono_tag
                )
                if req.approved:
                    msg_sms = (
                        f"Animoon Seguridad: La apelación para la cuenta '{usuario.nickname}' fue APROBADA. "
                        f"El acceso ha sido restaurado exitosamente. Motivo: {req.reason}"
                    )
                else:
                    msg_sms = (
                        f"Animoon Seguridad: La apelación para la cuenta '{usuario.nickname}' fue RECHAZADA. "
                        f"La suspensión se mantiene definitiva. Motivo: {req.reason}"
                    )
                send_notification_sms(tel_plano, msg_sms)
            except Exception as e_sms:
                logger.error(f"Error enviando SMS de dictamen de apelación: {e_sms}")

        nickname = usuario.nickname if usuario else "Usuario"

        return schemas.AdminAppealDto(
            id=ap.id,
            nickname=nickname,
            date=formatear_fecha_es(ap.created_at),
            incident="Revisión de suspensión por apelación",
            explanation=ap.justificacion,
            evidence="Revisión completada por el administrador.",
            status=nuevo_estado,
            resolution=req.reason,
            resolvedAt=now_ms,
            resolvedBy=admin_user
        )

    # Respuesta para casos de muestra (AP-DEMO-*)
    return schemas.AdminAppealDto(
        id=appeal_id,
        nickname="Usuario Demostración",
        date=formatear_fecha_es(now_dt),
        incident="Incidencia resuelta",
        explanation="Apelación de prueba evaluada.",
        evidence="Conversación de demostración.",
        status=nuevo_estado,
        resolution=req.reason,
        resolvedAt=now_ms,
        resolvedBy=admin_user
    )


# =============================================================================
# ENDPOINT PÚBLICO / USUARIO (SUBMIT DE APELACIÓN)
# =============================================================================

@router.post("/submit-appeal", response_model=schemas.DefaultResponse)
def submit_appeal(
    req: schemas.UserAppealSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Permite a un usuario sancionado enviar una apelación con su justificación.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.nickname == req.nickname).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El apelativo ingresado no existe."
        )

    if not usuario.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cuenta no se encuentra suspendida."
        )

    # RN-AP-02 / RF-AP-05: Si ya existe una apelación registrada y pendiente, impedir un segundo envío
    apelacion_pendiente = (
        db.query(models.Apelacion)
        .filter(
            models.Apelacion.usuario_id == usuario.id,
            models.Apelacion.estado.in_(["PENDIENTE", "EN_REVISION"])
        )
        .first()
    )
    if apelacion_pendiente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una apelación registrada en proceso de revisión para esta cuenta."
        )

    # RN-AP-04: Si la apelación fue rechazada previamente, el ban se mantiene definitivo
    apelacion_rechazada = (
        db.query(models.Apelacion)
        .filter(
            models.Apelacion.usuario_id == usuario.id,
            models.Apelacion.estado == "RECHAZADA"
        )
        .first()
    )
    if apelacion_rechazada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La apelación previa para esta suspensión fue evaluada y rechazada. La sanción se mantiene."
        )

    # Buscar el bloque que originó el baneo
    bloque = (
        db.query(models.BloqueAnalisis)
        .filter(models.BloqueAnalisis.agresor_usuario_id == usuario.id)
        .order_by(models.BloqueAnalisis.created_at.desc())
        .first()
    )

    bloque_id = bloque.id if bloque else str(uuid.uuid4())

    nueva_apelacion = models.Apelacion(
        id=f"AP-{str(uuid.uuid4())[:8].upper()}",
        usuario_id=usuario.id,
        bloque_id=bloque_id,
        justificacion=req.justificacion,
        estado="PENDIENTE"
    )
    db.add(nueva_apelacion)
    db.commit()

    return schemas.DefaultResponse(
        message="Tu apelación ha sido enviada exitosamente. Será evaluada por el equipo de moderación.",
        status="success"
    )
