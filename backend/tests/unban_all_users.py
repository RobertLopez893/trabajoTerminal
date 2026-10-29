"""
=============================================================================
HERRAMIENTA DE PRUEBAS: DESBANEO TOTAL DE USUARIOS (ANIMOON)
=============================================================================
Este script desbanea y reactiva a todos los usuarios bloqueados en la base
de datos operacional (PostgreSQL) y limpia la lista de bloqueo en Redis.

Uso:
  - Localmente:
      python backend/tests/unban_all_users.py

  - En entorno AWS EC2 (desde tu terminal):
      python backend/tests/unban_all_users.py --aws
=============================================================================
"""

import os
import sys
import argparse
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configurar rutas para importar módulos del backend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

sys.path.append(PROJECT_ROOT)

def desbanear_local():
    """Ejecuta el desbaneo contra la base de datos y Redis locales configurados."""
    print("=" * 65)
    print("[INFO] INICIANDO DESBANEO DE USUARIOS EN EL ENTORNO LOCAL")
    print("=" * 65)

    try:
        from backend.database.db import SessionLocal
        from backend.database.models import Usuario, Sesion
        import redis
    except ImportError as e:
        print(f"[ERROR] Error al importar librerías necesarias: {e}")
        return False

    db = SessionLocal()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        # 1. Consultar usuarios baneados o inactivos
        usuarios_afectados = db.query(Usuario).filter(
            (Usuario.is_banned == True) | (Usuario.is_active == False)
        ).all()

        total = len(usuarios_afectados)
        print(f"\n[BD] Usuarios suspendidos o inactivos encontrados: {total}")

        if total > 0:
            print("-" * 65)
            print(f"{'ID':<38} | {'NICKNAME':<15} | {'ESTADO ANTERIOR'}")
            print("-" * 65)
            for u in usuarios_afectados:
                estado = "BANEADO" if u.is_banned else "INACTIVO"
                print(f"{u.id:<38} | {u.nickname:<15} | {estado}")

                # Reactivar usuario
                u.is_banned = False
                u.is_active = True

            # Reactivar también las sesiones en la base de datos
            sesiones_reactivadas = db.query(Sesion).filter(Sesion.is_active == False).update({"is_active": True})
            db.commit()

            print("-" * 65)
            print(f"[OK] {total} usuario(s) desbaneado(s) y reactivado(s) en PostgreSQL.")
            print(f"[OK] {sesiones_reactivadas} sesión(es) reactivada(s).")
        else:
            print("[INFO] No hay usuarios baneados actualmente en la base de datos.")

        # 2. Limpiar conjunto 'banned_users' en Redis
        try:
            r = redis.Redis.from_url(redis_url, decode_responses=True)
            num_eliminados = r.delete("banned_users")
            print(f"[REDIS] Llave 'banned_users' eliminada en Redis (Elementos eliminados: {num_eliminados}).")
        except Exception as red_err:
            print(f"[AVISO] No se pudo conectar a Redis ({redis_url}): {red_err}")

        print("\n[EXITO] ¡DESBANEO COMPLETADO! Todos los usuarios pueden volver a chatear y loguearse.")
        print("=" * 65)
        return True

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error durante el desbaneo en base de datos: {e}")
        return False
    finally:
        db.close()


def desbanear_aws():
    """Ejecuta el desbaneo de forma remota en la instancia AWS EC2 vía SSH."""
    print("=" * 65)
    print("[AWS] INICIANDO DESBANEO REMOTO EN AWS EC2 (18.191.151.124)")
    print("=" * 65)

    # Buscar la llave animoon-key.pem en las ubicaciones posibles
    parent_dir = os.path.dirname(PROJECT_ROOT)
    candidate_paths = [
        os.path.join(parent_dir, "AWS", "animoon-key.pem"),
        os.path.join(PROJECT_ROOT, "AWS", "animoon-key.pem"),
        os.path.join(os.path.dirname(os.getcwd()), "AWS", "animoon-key.pem"),
        os.path.join(os.getcwd(), "AWS", "animoon-key.pem"),
        r"C:\Users\lopez\Desktop\Tareas ESCOM\Trabajo Terminal\AWS\animoon-key.pem"
    ]

    key_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            key_path = p
            break

    if not key_path:
        print("[ERROR] No se encontró la llave SSH 'animoon-key.pem'.")
        print("Rutas buscadas:")
        for p in candidate_paths:
            print(f"  - {p}")
        return False

    print(f"[INFO] Usando llave SSH: {key_path}")

    # Comando SQL para ejecutar dentro del contenedor postgres de AWS
    sql_cmd = (
        "UPDATE usuario SET is_banned = false, is_active = true WHERE is_banned = true OR is_active = false; "
        "UPDATE sesion SET is_active = true WHERE is_active = false;"
    )

    # Comando Redis para borrar banned_users en el contenedor redis de AWS
    remote_command = (
        f'sudo docker exec animoon_postgres psql -U postgres -d animoon_operacional -c "{sql_cmd}" && '
        'sudo docker exec animoon_redis redis-cli del banned_users && '
        'echo "--- ESTADO DE USUARIOS EN AWS TRAS DESBANEO ---" && '
        'sudo docker exec animoon_postgres psql -U postgres -d animoon_operacional -c "SELECT id, nickname, is_banned, is_active FROM usuario LIMIT 10;"'
    )

    ssh_cmd = [
        "ssh",
        "-i", key_path,
        "-o", "StrictHostKeyChecking=no",
        "ubuntu@18.191.151.124",
        remote_command
    ]

    try:
        res = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        print(res.stdout)
        print("\n[EXITO] ¡DESBANEO EN AWS COMPLETADO!")
        print("Todos los usuarios de prueba en AWS ya pueden iniciar sesión y chatear.")
        print("=" * 65)
        return True
    except subprocess.CalledProcessError as err:
        print(f"[ERROR] Error ejecutando comando remoto en AWS: {err}")
        if err.stderr:
            print("Detalle error SSH:", err.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Script de pruebas para desbanear y reactivar usuarios en Animoon."
    )
    parser.add_argument(
        "--aws",
        action="store_true",
        help="Ejecutar el desbaneo de forma remota en la instancia de AWS EC2."
    )

    args = parser.parse_args()

    if args.aws:
        desbanear_aws()
    else:
        # Detectar si estamos ejecutando directamente dentro de un contenedor en AWS
        if os.getenv("DB_HOST") == "db" or os.path.exists("/app/backend"):
            desbanear_local()
        else:
            exito = desbanear_local()
            if not exito:
                print("\n[TIP] Si tus servicios están corriendo en la nube de AWS, ejecuta:")
                print("      python backend/tests/unban_all_users.py --aws")

if __name__ == "__main__":
    main()
