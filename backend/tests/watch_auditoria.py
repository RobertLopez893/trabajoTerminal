"""
Monitor de Auditoría Criptográfica en Tiempo Real (Animoon)
Monitorea continuamente la base de datos 'animoon_auditoria' y muestra
en pantalla cada nuevo evento de seguridad generado por el Worker BETO,
descifrando la evidencia con AES-256-GCM y validando su hash SHA-256 en vivo.
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

sys.path.append(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from security.aes.aes_gcm import AESGCMCipher
from backend.database.db import SessionLocalAuditoria
from backend.database.models_auditoria import LogAuditoria, AlertaUsuario

aes = AESGCMCipher()


def formatear_evidencia(texto_plano: str) -> str:
    """Formatea la evidencia extraída para presentación limpia."""
    lineas = []
    for parte in texto_plano.split(" | "):
        parte = parte.strip()
        if parte:
            lineas.append(f"     💬 {parte}")
    return "\n".join(lineas) if lineas else f"     {texto_plano}"


import argparse

def imprimir_log_detalle(log, db):
    """Imprime una tarjeta detallada para un log de auditoría."""
    alerta = db.query(AlertaUsuario).filter(AlertaUsuario.log_id_ref == log.id).first()

    evidencia_descifrada = None
    hash_valido = False
    if log.evidencia_cifrada and log.iv_nonce and log.tag_autenticacion:
        try:
            evidencia_descifrada = aes.decrypt(
                log.evidencia_cifrada,
                log.iv_nonce,
                log.tag_autenticacion
            )
            hash_calculado = hashlib.sha256(evidencia_descifrada.encode("utf-8")).hexdigest()
            hash_valido = (hash_calculado == log.hash_integridad)
        except Exception as dec_err:
            evidencia_descifrada = f"[Error al descifrar: {dec_err}]"

    print("┌" + "─" * 78 + "┐")
    print(f"│ 🚨 EVENTO DE AUDITORÍA REGISTRADO [LOG #{log.id}]".ljust(79) + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│ • Tipo de Evento:    {log.tipo_evento}".ljust(79) + "│")
    print(f"│ • Timestamp:         {log.timestamp_evento}".ljust(79) + "│")
    print(f"│ • Usuario Agresor:   {log.usuario_id_ref}".ljust(79) + "│")
    print(f"│ • Bloque Afectado:   {log.bloque_id_ref}".ljust(79) + "│")
    print(f"│ • Hash SHA-256:      {log.hash_integridad}".ljust(79) + "│")
    
    status_hash = "✅ VÁLIDO (Cadena de custodia intacta)" if hash_valido else "❌ ALTERADO"
    print(f"│ • Integridad Hash:   {status_hash}".ljust(79) + "│")

    if alerta:
        print(f"│ • Alerta Tutor:      Estado: {alerta.estado}".ljust(79) + "│")

    print("├" + "─" * 78 + "┤")
    print("│ 📜 EVIDENCIA DESCIFRADA (AES-256-GCM):".ljust(79) + "│")
    if evidencia_descifrada:
        for l in formatear_evidencia(evidencia_descifrada).split("\n"):
            print(f"│ {l}".ljust(79) + "│")
    else:
        print(f"│   (Sin evidencia textual asociada)".ljust(79) + "│")
    print("└" + "─" * 78 + "┘\n")


def iniciar_monitor_auditoria(intervalo_segundos: float = 1.5, ver_ultimos: int = 0, seguir: bool = True):
    print("=" * 80)
    print("🛡️  MONITOR DE AUDITORÍA CRIPTOGRÁFICA (ANIMOON)")
    print(f"   Base de datos: animoon_auditoria | Intervalo: {intervalo_segundos}s")
    if seguir:
        print("   Presiona Ctrl + C para detener el monitoreo.")
    print("=" * 80)

    db = SessionLocalAuditoria()
    try:
        total_historico = db.query(LogAuditoria).count()
        ultimo_log = db.query(LogAuditoria).order_by(LogAuditoria.id.desc()).first()
        ultimo_id = ultimo_log.id if ultimo_log else 0
        print(f"[*] Registros históricos actuales: {total_historico} logs de auditoría.\n")

        if ver_ultimos > 0:
            print(f"[*] Mostrando los últimos {ver_ultimos} eventos registrados:")
            logs_previos = (
                db.query(LogAuditoria)
                .order_by(LogAuditoria.id.desc())
                .limit(ver_ultimos)
                .all()
            )
            for log in reversed(logs_previos):
                imprimir_log_detalle(log, db)

        if not seguir:
            return

        print(f"[*] Esperando nuevos eventos de seguridad desde el microservicio BETO...\n")
    finally:
        db.close()

    try:
        while True:
            time.sleep(intervalo_segundos)
            db = SessionLocalAuditoria()
            try:
                nuevos_logs = (
                    db.query(LogAuditoria)
                    .filter(LogAuditoria.id > ultimo_id)
                    .order_by(LogAuditoria.id.asc())
                    .all()
                )

                for log in nuevos_logs:
                    ultimo_id = log.id
                    imprimir_log_detalle(log, db)
            finally:
                db.close()

    except KeyboardInterrupt:
        print("\n[*] Monitor de auditoría detenido por el usuario.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de auditoría criptográfica")
    parser.add_argument("--last", type=int, default=0, help="Mostrar los últimos N logs antes de escuchar")
    parser.add_argument("--interval", type=float, default=1.5, help="Intervalo en segundos")
    parser.add_argument("--no-follow", action="store_true", help="Solo mostrar los últimos logs y salir")
    args = parser.parse_args()

    iniciar_monitor_auditoria(
        intervalo_segundos=args.interval,
        ver_ultimos=args.last,
        seguir=not args.no_follow
    )
