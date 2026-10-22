"""
=============================================================================
MICROSERVICIO CONSUMIDOR DE ANÁLISIS NLP: BETO WORKER (FASE 3)
=============================================================================
Este servicio es un proceso consumidor independiente que:
1. Extrae bloques de 20 mensajes de la cola 'queue:beto_jobs' (Redis BRPOP).
2. Evalúa las ventanas de conversación utilizando BETO ONNX (inference.py).
3. Actualiza el estado del 'BloqueAnalisis' en PostgreSQL operacional.
4. Si se detecta Grooming (Nivel 2):
   - Aplica suspensión permanente al agresor (Usuario.is_banned = True).
   - Genera registro en LogAuditoria cifrado con AES-GCM y firmado con SHA-256.
   - Crea registro en AlertaUsuario.
   - Descifra el teléfono del tutor de la víctima y envía alerta SMS (Twilio).
   - Publica en Redis Pub/Sub ('channel:grooming_alerts') para activar
     la salida segura (SAFE_EXIT) y matar la conexión del agresor (Código 4003).
=============================================================================
"""

import os
import sys
import json
import time
import signal
import hashlib
import logging
from datetime import datetime, timezone
import redis
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [BETO_WORKER]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("BetoWorker")

# Rutas del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal, SessionLocalAuditoria
from backend.database.models import BloqueAnalisis, Usuario, Chat
from backend.database.models_auditoria import LogAuditoria, AlertaUsuario
from backend.beto_worker.inference import AnalizadorBETO
from backend.beto_worker.notifier import enviar_alerta_sms

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "queue:beto_jobs"
CHANNEL_ALERTS = "channel:grooming_alerts"

# Control de parada limpia
running = True

def handle_exit_signal(sig, frame):
    global running
    logger.info("Señal de terminación recibida. Cerrando worker limpiamente...")
    running = False

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)


def procesar_trabajo(job_data: dict, analizador: AnalizadorBETO, aes_cipher: AESGCMCipher, r: redis.Redis):
    """
    Procesa un bloque individual extraído de Redis.
    """
    bloque_id = job_data.get("bloque_id")
    chat_id = job_data.get("chat_id")
    numero_bloque = job_data.get("numero_bloque")
    usuario_a_id = job_data.get("usuario_a_id")
    usuario_b_id = job_data.get("usuario_b_id")
    mensajes = job_data.get("mensajes", [])

    logger.info(f"--- Procesando Bloque #{numero_bloque} (ID: {bloque_id}) de Sala '{chat_id}' ---")
    logger.info(f"Total de mensajes a evaluar en ventanas: {len(mensajes)}")

    # 1. Inferencia con BETO ONNX
    t0 = time.perf_counter()
    res = analizador.analizar_bloque(mensajes, usuario_a_id, usuario_b_id)
    t_inferencia = (time.perf_counter() - t0) * 1000

    es_grooming = res["grooming_detectado"]
    score = res["confidence_score"]
    fase = res["fase_detectada"]
    agresor_id = res["agresor_id"]

    logger.info(
        f"Inferencia completada en {t_inferencia:.2f} ms | "
        f"Grooming: {es_grooming} | Fase: {fase} | Confianza: {score:.2%}"
    )

    # Identificar víctima y agresor dentro de los usuarios del chat
    victima_id = None
    if es_grooming and agresor_id:
        victima_id = usuario_b_id if agresor_id == usuario_a_id else usuario_a_id
    elif usuario_a_id and usuario_b_id:
        victima_id = usuario_b_id

    # 2. Actualización en Base de Datos Operacional (animoon_operacional)
    db_op = SessionLocal()
    try:
        bloque = db_op.query(BloqueAnalisis).filter(BloqueAnalisis.id == bloque_id).first()
        if bloque:
            bloque.estado = "ANALIZADO"
            bloque.confidence_score = score
            bloque.grooming_detectado = es_grooming
            bloque.agresor_usuario_id = agresor_id if es_grooming else None
            bloque.fase_detectada = fase
            bloque.analizado_at = datetime.now(timezone.utc)

        # Si hay grooming, suspender inmediatamente al agresor
        if es_grooming and agresor_id:
            agresor = db_op.query(Usuario).filter(Usuario.id == agresor_id).first()
            if agresor:
                agresor.is_banned = True
                agresor.is_active = False
                logger.warning(f"🚫 [SEGURIDAD] Usuario agresor '{agresor_id}' ha sido suspendido (is_banned=True, is_active=False).")

            # Revocar todas las sesiones activas en la BD operacional
            from backend.database.models import Sesion
            revocadas = db_op.query(Sesion).filter(
                Sesion.usuario_id == agresor_id,
                Sesion.is_active == True
            ).update({"is_active": False})
            logger.warning(f"🚫 [SEGURIDAD] Se revocaron {revocadas} sesiones activas del agresor '{agresor_id}'.")

        db_op.commit()
        logger.info(f"[DB OPERACIONAL] Bloque '{bloque_id}' actualizado a estado ANALIZADO.")
    except Exception as e:
        db_op.rollback()
        logger.error(f"[DB ERROR OPERACIONAL] Fallo al actualizar BloqueAnalisis: {e}")
    finally:
        db_op.close()

    # 3. Flujo Crítico de Seguridad ante Detección de Grooming (Nivel 2)
    if es_grooming and agresor_id and victima_id:
        logger.warning(f"🚨 ¡GROOMING CONFIRMADO! Activando protocolo de contención para sala '{chat_id}'...")

        evidencia_texto = res.get("ventana_evidencia") or "Evidencia no disponible en texto plano"
        hash_integridad = hashlib.sha256(evidencia_texto.encode("utf-8")).hexdigest()

        # Cifrar evidencia con AES-GCM
        enc_evidencia = aes_cipher.encrypt(evidencia_texto)

        # 3.1 Registrar en Base de Datos de Auditoría (animoon_auditoria)
        db_audit = SessionLocalAuditoria()
        try:
            nuevo_log = LogAuditoria(
                usuario_id_ref=agresor_id,
                bloque_id_ref=bloque_id,
                tipo_evento="DETECCION_GROOMING_NIVEL_2",
                descripcion=f"Detección de Grooming en sala '{chat_id}' con confianza {score:.2%}.",
                evidencia_cifrada=enc_evidencia["ciphertext_b64"],
                iv_nonce=enc_evidencia["nonce_b64"],
                tag_autenticacion=enc_evidencia["tag_b64"],
                hash_integridad=hash_integridad
            )
            db_audit.add(nuevo_log)
            db_audit.commit()
            db_audit.refresh(nuevo_log)

            nueva_alerta = AlertaUsuario(
                usuario_receptor_id_ref=victima_id,
                usuario_victima_id_ref=victima_id,
                log_id_ref=nuevo_log.id,
                estado="ENVIADA"
            )
            db_audit.add(nueva_alerta)
            db_audit.commit()
            logger.info(f"[DB AUDITORÍA] Log #{nuevo_log.id} y Alerta #{nueva_alerta.id} creados exitosamente.")
        except Exception as e:
            db_audit.rollback()
            logger.error(f"[DB ERROR AUDITORÍA] Error al registrar evidencia en auditoría: {e}")
        finally:
            db_audit.close()

        # 3.2 Notificación SMS al tutor/contacto de la víctima
        db_op = SessionLocal()
        try:
            victima = db_op.query(Usuario).filter(Usuario.id == victima_id).first()
            if victima and victima.telefono_cifrado:
                try:
                    telefono_plano = aes_cipher.decrypt(
                        victima.telefono_cifrado,
                        victima.telefono_iv_nonce,
                        victima.telefono_tag
                    )
                    enviar_alerta_sms(telefono_plano, motivo=f"Protocolo de protección activa ({fase})")
                except Exception as dec_err:
                    logger.error(f"[CRYPTO ERROR] No se pudo descifrar teléfono de víctima: {dec_err}")
        except Exception as e:
            logger.error(f"[ERROR TUTOR] Error al consultar datos de tutor: {e}")
        finally:
            db_op.close()

        # 3.3 Publicar Alerta en Redis Pub/Sub para que chat_server.py actúe en caliente
        alerta_pubsub = {
            "chat_id": chat_id,
            "agresor_id": agresor_id,
            "victima_id": victima_id,
            "motivo": f"Comportamiento de grooming detectado ({score:.1%})"
        }
        r.publish(CHANNEL_ALERTS, json.dumps(alerta_pubsub))
        r.sadd("banned_users", agresor_id)
        logger.info(f"[PUB/SUB] Alerta emitida en '{CHANNEL_ALERTS}' para expulsar agresor y salvar víctima.")


def main():
    global running
    logger.info("=== INICIANDO MICROSERVICIO BETO WORKER (ANIMOON) ===")
    logger.info(f"Conectando a Redis: {REDIS_URL}")
    logger.info(f"Cola de escucha: {QUEUE_NAME}")

    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        logger.info("Conexión con Redis establecida con éxito.")
    except Exception as e:
        logger.critical(f"No se pudo conectar a Redis: {e}")
        sys.exit(1)

    try:
        aes_cipher = AESGCMCipher()
        logger.info("Cifrador AES-GCM inicializado con llave maestra.")
    except Exception as e:
        logger.critical(f"No se pudo inicializar AESGCMCipher: {e}")
        sys.exit(1)

    try:
        analizador = AnalizadorBETO()
        logger.info("Motor BETO ONNX cargado y listo en memoria.")
    except Exception as e:
        logger.critical(f"Fallo al cargar el modelo BETO ONNX: {e}")
        sys.exit(1)

    logger.info(">>> Worker esperando tareas en 'queue:beto_jobs' (Modo Bloqueante BRPOP)...")

    while running:
        try:
            # BRPOP bloquea pasivamente durante 2 segundos para permitir captura limpia de señales
            item = r.brpop(QUEUE_NAME, timeout=2)
            if item:
                _, job_raw = item
                try:
                    job_data = json.loads(job_raw)
                    procesar_trabajo(job_data, analizador, aes_cipher, r)
                except json.JSONDecodeError:
                    logger.error("Error decodificando payload JSON de la cola.")
                except Exception as proc_err:
                    logger.error(f"Error procesando trabajo de la cola: {proc_err}", exc_info=True)
        except redis.ConnectionError:
            logger.warning("Conexión perdida con Redis. Reintentando en 3 segundos...")
            time.sleep(3)
        except Exception as loop_err:
            if running:
                logger.error(f"Error inesperado en loop principal del worker: {loop_err}", exc_info=True)
                time.sleep(1)

    logger.info("BETO Worker detenido correctamente.")


if __name__ == "__main__":
    main()
