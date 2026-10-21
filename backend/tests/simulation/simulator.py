"""
Motor de Simulación de Conversaciones WebSocket TLS 1.3 para Animoon.
Permite ejecutar escenarios automatizados entre dos clientes simulando el comportamiento
real de la aplicación móvil (cifrado AES-256-GCM, recepción de eventos y validación de seguridad).
"""

import os
import sys
import ssl
import json
import time
import uuid
import asyncio
import redis
import websockets
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.dirname(CURRENT_DIR)
BACKEND_DIR = os.path.dirname(TESTS_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocal, SessionLocalAuditoria
from backend.database.models import Usuario, Chat, BloqueAnalisis
from backend.database.models_auditoria import LogAuditoria, AlertaUsuario
from backend.tests.simulation.scenarios import CONVERSACION_INOCUA, ATAQUE_GROOMING

WS_URL = os.getenv("WS_URL", "wss://127.0.0.1:8765")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

aes = AESGCMCipher()


def configurar_ssl():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def asegurar_usuarios_db(chat_id: str, u1: str, u2: str, u1_tel="+525511223344", u2_tel="+525599887766"):
    """Crea o reinicia usuarios en PostgreSQL para pruebas limpias."""
    db = SessionLocal()
    try:
        for uid, tel in [(u1, u1_tel), (u2, u2_tel)]:
            u = db.query(Usuario).filter(Usuario.id == uid).first()
            if not u:
                enc = aes.encrypt(tel)
                db.add(Usuario(
                    id=uid,
                    nickname=f"nick_{uid[:12]}",
                    telefono_cifrado=enc["ciphertext_b64"],
                    telefono_iv_nonce=enc["nonce_b64"],
                    telefono_tag=enc["tag_b64"],
                    argon2id_hash="dummy_hash",
                    salt="dummy_salt",
                    is_verified=True,
                    is_active=True,
                    is_banned=False
                ))
            else:
                u.is_banned = False
        db.commit()

        c = db.query(Chat).filter(Chat.id == chat_id).first()
        if not c:
            db.add(Chat(id=chat_id, usuario_a_id=u1, usuario_b_id=u2))
            db.commit()
    finally:
        db.close()


async def ejecutar_simulacion(nombre_escenario: str = "inocua", chat_id: str = None, delay_entre_mensajes: float = 0.08):
    """
    Ejecuta un escenario completo de conversación a través de WebSockets TLS 1.3 reales.
    """
    if nombre_escenario == "inocua":
        dialogo = CONVERSACION_INOCUA
        u_a_role = "alice"
        u_b_role = "bob"
        espera_grooming = False
    elif nombre_escenario == "grooming":
        dialogo = ATAQUE_GROOMING
        u_a_role = "agresor"
        u_b_role = "victima"
        espera_grooming = True
    else:
        raise ValueError(f"Escenario no reconocido: {nombre_escenario}")

    chat_id = chat_id or f"sim_{nombre_escenario}_{uuid.uuid4().hex[:8]}"
    u_a_id = f"{u_a_role}_{uuid.uuid4().hex[:8]}"
    u_b_id = f"{u_b_role}_{uuid.uuid4().hex[:8]}"

    asegurar_usuarios_db(chat_id, u_a_id, u_b_id)

    ssl_ctx = configurar_ssl()
    print("=" * 80)
    print(f"🎬 INICIANDO SIMULACIÓN: [{nombre_escenario.upper()}] (20 mensajes)")
    print(f"   Sala: {chat_id} | Cliente A ({u_a_role}): {u_a_id} | Cliente B ({u_b_role}): {u_b_id}")
    print("=" * 80)

    eventos_capturados = {
        "mensajes_enviados": 0,
        "mensajes_recibidos": 0,
        "agresor_expulsado": False,
        "agresor_codigo_cierre": None,
        "victima_safe_exit": False,
        "victima_motivo_exit": None
    }

    async with websockets.connect(WS_URL, ssl=ssl_ctx) as ws_a, \
               websockets.connect(WS_URL, ssl=ssl_ctx) as ws_b:

        # Mapeo rápido de sockets y roles
        role_to_id = {u_a_role: u_a_id, u_b_role: u_b_id}
        role_to_ws = {u_a_role: ws_a, u_b_role: ws_b}

        # Listener para Cliente A
        async def listener_a():
            try:
                async for raw in ws_a:
                    msg = json.loads(raw)
                    eventos_capturados["mensajes_recibidos"] += 1
            except websockets.exceptions.ConnectionClosed as e:
                eventos_capturados["agresor_expulsado"] = True
                eventos_capturados["agresor_codigo_cierre"] = e.code

        # Listener para Cliente B
        async def listener_b():
            try:
                async for raw in ws_b:
                    msg = json.loads(raw)
                    eventos_capturados["mensajes_recibidos"] += 1
                    if msg.get("action") == "SAFE_EXIT":
                        eventos_capturados["victima_safe_exit"] = True
                        eventos_capturados["victima_motivo_exit"] = msg.get("motivo")
            except websockets.exceptions.ConnectionClosed:
                pass

        task_a = asyncio.create_task(listener_a())
        task_b = asyncio.create_task(listener_b())

        # Disparo secuencial de la conversación
        for idx, paso in enumerate(dialogo, start=1):
            emisor_role = paso["emisor"]
            receptor_role = u_b_role if emisor_role == u_a_role else u_a_role
            texto = paso["texto"]

            emisor_id = role_to_id[emisor_role]
            receptor_id = role_to_id[receptor_role]
            ws_emisor = role_to_ws[emisor_role]

            # Cifrado en RAM antes de enviar al WebSocket
            enc = aes.encrypt(texto)
            payload = {
                "chat_id": chat_id,
                "sender_id": emisor_id,
                "target_id": receptor_id,
                "encrypted_message": enc,
                "timestamp": str(time.time()),
                "is_file": False
            }

            try:
                await ws_emisor.send(json.dumps(payload))
                eventos_capturados["mensajes_enviados"] += 1
                icono = "🔴" if emisor_role == "agresor" else ("🟢" if emisor_role == "victima" else "💬")
                print(f"  [{idx:02d}/20] {icono} {emisor_role.upper()}: {texto}")
            except websockets.exceptions.ConnectionClosed:
                print(f"  [!] Socket de {emisor_role} cerrado antes de enviar mensaje {idx}.")
                break

            await asyncio.sleep(delay_entre_mensajes)

        print("\n[*] Todos los 20 mensajes fueron transmitidos al Chat Server.")
        print("[*] Esperando que Redis y el BETO Worker procesen el bloque en segundo plano...")

        # Dar margen al worker de procesar el bloque y emitir alertas si aplica
        for _ in range(60):
            if espera_grooming and eventos_capturados["agresor_expulsado"] and eventos_capturados["victima_safe_exit"]:
                break
            await asyncio.sleep(0.5)

        task_a.cancel()
        task_b.cancel()

    # -------------------------------------------------------------------------
    # VALIDACIONES EN BASE DE DATOS Y REDIS
    # -------------------------------------------------------------------------
    print("\n" + "─" * 80)
    print("📋 RESULTADOS Y VERIFICACIÓN EN BASE DE DATOS")
    print("─" * 80)

    db_op = SessionLocal()
    db_audit = SessionLocalAuditoria()
    try:
        bloque = db_op.query(BloqueAnalisis).filter(BloqueAnalisis.chat_id == chat_id).order_by(BloqueAnalisis.numero_bloque.desc()).first()
        bloque_estado = bloque.estado if bloque else "NO_EXISTE"
        grooming_detectado = bloque.grooming_detectado if bloque else False

        user_a = db_op.query(Usuario).filter(Usuario.id == u_a_id).first()
        user_b = db_op.query(Usuario).filter(Usuario.id == u_b_id).first()

        log_audit = db_audit.query(LogAuditoria).filter(LogAuditoria.bloque_id_ref == (bloque.id if bloque else "")).first()
        alerta = db_audit.query(AlertaUsuario).filter(AlertaUsuario.log_id_ref == log_audit.id).first() if log_audit else None

        print(f"  • Mensajes enviados al WebSocket:       {eventos_capturados['mensajes_enviados']}/20")
        print(f"  • Bloque de Análisis en PostgreSQL:     {bloque_estado} (ID: {bloque.id if bloque else 'N/A'})")
        print(f"  • Clasificación BETO Grooming:          {grooming_detectado}")
        print(f"  • Estado Usuario A ({u_a_role}):            is_banned={user_a.is_banned if user_a else 'N/A'}")
        print(f"  • Estado Usuario B ({u_b_role}):            is_banned={user_b.is_banned if user_b else 'N/A'}")

        if espera_grooming:
            print(f"  • Expulsión Socket Agresor:             {eventos_capturados['agresor_expulsado']} (Código: {eventos_capturados['agresor_codigo_cierre']})")
            print(f"  • Notificación SAFE_EXIT a Víctima:     {eventos_capturados['victima_safe_exit']}")
            print(f"  • Log de Auditoría Criptográfica:       {'CREADO' if log_audit else 'NO_REGISTRADO'}")
            if log_audit:
                print(f"    - Hash SHA-256 Integridad:            {log_audit.hash_integridad}")
                print(f"    - Evidencia Cifrada AES-256-GCM:       {log_audit.evidencia_cifrada[:35]}...")
            print(f"  • Alerta para Tutor en BD:              {'CREADA' if alerta else 'NO_REGISTRADA'}")

        exito = False
        if not espera_grooming:
            exito = (bloque_estado == "ANALIZADO") and (not grooming_detectado) and (not user_a.is_banned)
        else:
            exito = (bloque_estado == "ANALIZADO") and grooming_detectado and user_a.is_banned and \
                    eventos_capturados["agresor_expulsado"] and eventos_capturados["victima_safe_exit"] and \
                    (log_audit is not None)

        print("\n" + "=" * 80)
        if exito:
            print(f"✅ [ÉXITO] SIMULACIÓN '{nombre_escenario.upper()}' CUMPLIDA SATISFACTORIAMENTE.")
        else:
            print(f"⚠️ [ATENCIÓN] SIMULACIÓN '{nombre_escenario.upper()}' CON OBSERVACIONES.")
        print("=" * 80 + "\n")

        return {
            "escenario": nombre_escenario,
            "exito": exito,
            "bloque_estado": bloque_estado,
            "grooming_detectado": grooming_detectado,
            "agresor_banned": user_a.is_banned if user_a else False,
            "agresor_expulsado": eventos_capturados["agresor_expulsado"],
            "victima_safe_exit": eventos_capturados["victima_safe_exit"]
        }
    finally:
        db_op.close()
        db_audit.close()


if __name__ == "__main__":
    escenario = sys.argv[1] if len(sys.argv) > 1 else "grooming"
    asyncio.run(ejecutar_simulacion(escenario))
