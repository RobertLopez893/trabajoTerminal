"""
=============================================================================
PRUEBA DE INTEGRACIÓN: MICROSERVICIO WORKER BETO (FASE 3)
=============================================================================
Este script valida de punta a punta el funcionamiento del Worker de IA:
1. INFERENCIA ONNX: Carga del modelo BETO y tokenizador en memoria.
2. CASO SEGURO:
   - Envío de un bloque de conversación normal.
   - Verificación de BloqueAnalisis -> ANALIZADO (grooming_detectado=False).
   - Verificación de que ningún usuario fue suspendido.
3. CASO GROOMING (AMENAZA DETECTADA):
   - Envío de un bloque simulando patrones de aislamiento y secreto.
   - Verificación de BloqueAnalisis -> ANALIZADO (grooming_detectado=True).
   - Verificación de suspensión en PostgreSQL: Usuario agresor is_banned=True.
   - Verificación de LogAuditoria en animoon_auditoria (Evidencia AES-GCM + Hash SHA-256).
   - Verificación de AlertaUsuario en animoon_auditoria.
   - Verificación de evento publicado en canal Pub/Sub 'channel:grooming_alerts'.
=============================================================================
"""

import os
import sys
import json
import time
import uuid
import hashlib
import redis
from datetime import datetime, timezone
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
from backend.beto_worker.worker import procesar_trabajo

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
aes = AESGCMCipher()


def crear_usuarios_y_chat(chat_id: str, u1: str, u2: str):
    db = SessionLocal()
    try:
        for uid in [u1, u2]:
            u = db.query(Usuario).filter(Usuario.id == uid).first()
            if not u:
                enc = aes.encrypt("+525512345678")
                db.add(Usuario(
                    id=uid,
                    nickname=f"nick_{uuid.uuid4().hex[:12]}",
                    telefono_cifrado=enc["ciphertext_b64"],
                    telefono_iv_nonce=enc["nonce_b64"],
                    telefono_tag=enc["tag_b64"],
                    argon2id_hash="dummy_hash",
                    salt="dummy_salt",
                    is_verified=True,
                    is_active=True,
                    is_banned=False
                ))
        db.commit()

        c = db.query(Chat).filter(Chat.id == chat_id).first()
        if not c:
            db.add(Chat(id=chat_id, usuario_a_id=u1, usuario_b_id=u2))
            db.commit()
    finally:
        db.close()


def ejecutar_test_fase_3():
    print("=" * 75)
    print("   VALIDACIÓN INTEGRAL DEL WORKER BETO (FASE 3)")
    print("=" * 75)

    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    print("[OK] Conexión a Redis exitosa.")

    print("[*] Inicializando motor BETO ONNX...")
    analizador = AnalizadorBETO()
    print("[OK] AnalizadorBETO cargado y validado en memoria.")

    # -------------------------------------------------------------
    # PRUEBA 1: CONVERSACIÓN INOCUA (CASO SEGURO)
    # -------------------------------------------------------------
    print("\n" + "─" * 75)
    print("1. PROBANDO FLUJO CONVERSACIÓN SEGURA (SIN RIESGO)")
    print("─" * 75)

    chat_seguro_id = f"test_chat_safe_{uuid.uuid4().hex[:8]}"
    alice_id = f"alice_{uuid.uuid4().hex[:8]}"
    bob_id = f"bob_{uuid.uuid4().hex[:8]}"
    crear_usuarios_y_chat(chat_seguro_id, alice_id, bob_id)

    db_op = SessionLocal()
    bloque_safe = BloqueAnalisis(
        id=str(uuid.uuid4()),
        chat_id=chat_seguro_id,
        numero_bloque=1,
        total_mensajes=20,
        estado="PENDIENTE",
        modelo_version="BETO_ONNX"
    )
    db_op.add(bloque_safe)
    db_op.commit()
    bloque_safe_id = bloque_safe.id
    db_op.close()

    mensajes_seguros = [
        {"orden": i, "emisor_id": alice_id if i % 2 != 0 else bob_id,
         "texto": f"Hola, ¿cómo estás? Estamos hablando de la tarea de matemáticas {i}.",
         "timestamp": datetime.now(timezone.utc).isoformat()}
        for i in range(1, 21)
    ]

    job_safe = {
        "bloque_id": bloque_safe_id,
        "chat_id": chat_seguro_id,
        "numero_bloque": 1,
        "usuario_a_id": alice_id,
        "usuario_b_id": bob_id,
        "mensajes": mensajes_seguros
    }

    print(f"[*] Procesando bloque seguro en worker...")
    procesar_trabajo(job_safe, analizador, aes, r)

    # Verificaciones Caso Seguro
    db_op = SessionLocal()
    blq_res = db_op.query(BloqueAnalisis).filter(BloqueAnalisis.id == bloque_safe_id).first()
    assert blq_res.estado == "ANALIZADO", f"Error: Estado esperado ANALIZADO, recibido {blq_res.estado}"
    assert blq_res.grooming_detectado is False, "Error: Falso positivo, no debió detectar grooming"
    print(f"[OK] Bloque seguro verificado: Estado={blq_res.estado} | Grooming={blq_res.grooming_detectado} | Confianza={blq_res.confidence_score}")

    u_alice = db_op.query(Usuario).filter(Usuario.id == alice_id).first()
    assert u_alice.is_banned is False, "Error: Alice no debió ser suspendida"
    print(f"[OK] Usuario verificado: Alice permanece activa (is_banned=False).")
    db_op.close()

    # -------------------------------------------------------------
    # PRUEBA 2: CONVERSACIÓN CON PATRÓN DE GROOMING (CASO CRÍTICO)
    # -------------------------------------------------------------
    print("\n" + "─" * 75)
    print("2. PROBANDO FLUJO DE AMENAZA (PATRÓN DE GROOMING DETECTADO)")
    print("─" * 75)

    chat_amenaza_id = f"test_chat_threat_{uuid.uuid4().hex[:8]}"
    agresor_id = f"agresor_{uuid.uuid4().hex[:8]}"
    victima_id = f"victima_{uuid.uuid4().hex[:8]}"
    crear_usuarios_y_chat(chat_amenaza_id, agresor_id, victima_id)

    db_op = SessionLocal()
    bloque_threat = BloqueAnalisis(
        id=str(uuid.uuid4()),
        chat_id=chat_amenaza_id,
        numero_bloque=1,
        total_mensajes=20,
        estado="PENDIENTE",
        modelo_version="BETO_ONNX"
    )
    db_op.add(bloque_threat)
    db_op.commit()
    bloque_threat_id = bloque_threat.id
    db_op.close()

    # Suscribirse al canal de alertas para verificar que el worker emita el evento Pub/Sub
    pubsub = r.pubsub()
    pubsub.subscribe("channel:grooming_alerts")
    # Consumir mensaje de suscripción
    pubsub.get_message(timeout=1.0)

    # Conversación simulando aislamiento, secretismo y solicitud de fotos privadas
    mensajes_amenaza = [
        {"orden": 1, "emisor_id": agresor_id, "texto": "Hola linda, eres muy bonita.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 2, "emisor_id": victima_id, "texto": "Hola, gracias.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 3, "emisor_id": agresor_id, "texto": "¿Cuántos años tienes? Te ves más grande en tus fotos.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 4, "emisor_id": victima_id, "texto": "Tengo 12.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 5, "emisor_id": agresor_id, "texto": "No le digas a tus papás que hablamos, este es nuestro secreto especial.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 6, "emisor_id": agresor_id, "texto": "Pásame tu WhatsApp para hablar por privado donde nadie nos vea.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 7, "emisor_id": victima_id, "texto": "No tengo WhatsApp.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 8, "emisor_id": agresor_id, "texto": "Mándame una foto tuya sin ropa, te voy a dar dinero y regalos si no dices nada.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 9, "emisor_id": agresor_id, "texto": "Recuerda que tus papás no deben enterarse de esto, promételo.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 10, "emisor_id": victima_id, "texto": "Me estás dando miedo.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 11, "emisor_id": agresor_id, "texto": "No tengas miedo mi amor, sólo tú y yo.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 12, "emisor_id": agresor_id, "texto": "Mándame las fotos ahorita o me voy a enojar contigo.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 13, "emisor_id": victima_id, "texto": "Déjame en paz.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 14, "emisor_id": agresor_id, "texto": "Te dije que nadie debe ver nuestros mensajes, bórralos.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 15, "emisor_id": agresor_id, "texto": "Te veo afuera de tu escuela a la salida.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 16, "emisor_id": victima_id, "texto": "No quiero.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 17, "emisor_id": agresor_id, "texto": "Es un secreto entre nosotros dos nada más.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 18, "emisor_id": agresor_id, "texto": "No le cuentes a nadie.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 19, "emisor_id": agresor_id, "texto": "Mándame la foto privada ya.", "timestamp": datetime.now(timezone.utc).isoformat()},
        {"orden": 20, "emisor_id": agresor_id, "texto": "Guarda el secreto.", "timestamp": datetime.now(timezone.utc).isoformat()}
    ]

    job_threat = {
        "bloque_id": bloque_threat_id,
        "chat_id": chat_amenaza_id,
        "numero_bloque": 1,
        "usuario_a_id": agresor_id,
        "usuario_b_id": victima_id,
        "mensajes": mensajes_amenaza
    }

    print(f"[*] Procesando bloque de amenaza en worker...")
    procesar_trabajo(job_threat, analizador, aes, r)

    # 1. Verificar actualización en PostgreSQL Operacional
    db_op = SessionLocal()
    blq_res = db_op.query(BloqueAnalisis).filter(BloqueAnalisis.id == bloque_threat_id).first()
    assert blq_res.estado == "ANALIZADO", f"Error: Estado no actualizado"
    assert blq_res.grooming_detectado is True, "Error: No detectó la amenaza de grooming"
    print(f"[OK] Bloque amenaza verificado: Estado={blq_res.estado} | Grooming={blq_res.grooming_detectado} | Fase={blq_res.fase_detectada} | Confianza={blq_res.confidence_score:.2%}")

    u_agr = db_op.query(Usuario).filter(Usuario.id == agresor_id).first()
    assert u_agr.is_banned is True, "Error: El agresor debió ser suspendido (is_banned=True)"
    print(f"[OK] Agresor suspendido en base de datos (Usuario.is_banned = True).")
    db_op.close()

    # 2. Verificar Auditoría en PostgreSQL (animoon_auditoria)
    db_audit = SessionLocalAuditoria()
    log = db_audit.query(LogAuditoria).filter(LogAuditoria.bloque_id_ref == bloque_threat_id).first()
    assert log is not None, "Error: No se creó el LogAuditoria en animoon_auditoria"
    assert log.tipo_evento == "DETECCION_GROOMING_NIVEL_2"
    assert log.evidencia_cifrada is not None
    assert log.hash_integridad is not None

    # Validar descifrado y hash SHA-256 de la evidencia
    evidencia_descifrada = aes.decrypt(log.evidencia_cifrada, log.iv_nonce, log.tag_autenticacion)
    hash_verificado = hashlib.sha256(evidencia_descifrada.encode("utf-8")).hexdigest()
    assert hash_verificado == log.hash_integridad, "Error: El hash SHA-256 no coincide con la evidencia descifrada"
    print(f"[OK] LogAuditoria verificado:")
    print(f"     ID Log: #{log.id} | Tipo: {log.tipo_evento}")
    print(f"     Evidencia AES-GCM descifrada con éxito: '{evidencia_descifrada[:80]}...'")
    print(f"     Firma Hash SHA-256 verificada: {hash_verificado[:16]}... (INTEGRIDAD OK)")

    alerta_usr = db_audit.query(AlertaUsuario).filter(AlertaUsuario.log_id_ref == log.id).first()
    assert alerta_usr is not None, "Error: No se creó AlertaUsuario"
    print(f"[OK] AlertaUsuario creada en auditoría: ID #{alerta_usr.id} | Estado: {alerta_usr.estado}")
    db_audit.close()

    # 3. Verificar Alerta emitida en Pub/Sub
    msg_pubsub = pubsub.get_message(timeout=3.0)
    assert msg_pubsub is not None, "Error: No se recibió mensaje en canal Pub/Sub"
    data_alerta = json.loads(msg_pubsub["data"])
    assert data_alerta["chat_id"] == chat_amenaza_id
    assert data_alerta["agresor_id"] == agresor_id
    print(f"[OK] Evento Pub/Sub recibido en canal 'channel:grooming_alerts':")
    print(f"     Chat ID:     {data_alerta['chat_id']}")
    print(f"     Agresor ID:  {data_alerta['agresor_id']}")
    print(f"     Víctima ID:  {data_alerta['victima_id']}")
    print(f"     Motivo:      {data_alerta['motivo']}")

    pubsub.unsubscribe()

    print("\n" + "=" * 75)
    print(">>> [ÉXITO TOTAL] FASE 3 (BETO WORKER) VERIFICADA COMPLETAMENTE <<<")
    print("    1. Inferencia ONNX operativa sobre ventanas de 5 mensajes.")
    print("    2. Caso seguro verificado: cero falsos positivos, sin ban.")
    print("    3. Caso Grooming detectado: ban en BD, evidencia cifrada AES-GCM,")
    print("       hash SHA-256 verificado, alerta en auditoría y Pub/Sub emitido.")
    print("=" * 75)


if __name__ == "__main__":
    ejecutar_test_fase_3()
