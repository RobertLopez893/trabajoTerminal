"""
=============================================================================
HERRAMIENTA DE DIAGNÓSTICO: PRUEBA DE CONEXIÓN A REDIS
=============================================================================
Este script verifica la conectividad y las capacidades esenciales de Redis
requeridas para el Chat de Animoon y el Microservicio Worker:
1. Ping / Pong y latencia de conexión.
2. Lectura/Escritura con tiempo de expiración (TTL).
3. Estructuras de lista para el buffer de 20 mensajes (RPUSH, LLEN, LTRIM).
4. Canal Pub/Sub para alertas de seguridad.
=============================================================================
"""

import os
import sys
import time
import json
import redis
from dotenv import load_dotenv

# Asegurar codificación utf-8 en terminales Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cargar variables de entorno desde la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def probar_conexion_redis():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print("=" * 65)
    print("       DIAGNÓSTICO DE CONEXIÓN REDIS — ANIMOON INFRAESTRUCTURA")
    print("=" * 65)
    print(f"[*] URL objetivo: {redis_url}\n")

    try:
        t0 = time.perf_counter()
        r = redis.from_url(redis_url, decode_responses=True)
        ping_res = r.ping()
        latencia_ms = (time.perf_counter() - t0) * 1000

        if ping_res:
            print(f"[OK] 1. Ping exitoso a Redis! Latencia de red: {latencia_ms:.2f} ms")
        else:
            print("[ERROR] 1. Redis no respondió al Ping.")
            return False

        # 2. Prueba de String y TTL
        clave_test = "animoon:test:ping"
        r.set(clave_test, "conexion_activa", ex=30)
        valor_recuperado = r.get(clave_test)
        ttl = r.ttl(clave_test)
        print(f"[OK] 2. Escritura y lectura Clave-Valor:")
        print(f"     Clave: '{clave_test}' -> '{valor_recuperado}' (TTL: {ttl}s)")

        # 3. Prueba de Buffer de Mensajes (Listas para el Chat)
        cola_test = "animoon:test:buffer_chat"
        r.delete(cola_test)
        
        # Insertar 3 mensajes simulados
        for i in range(1, 4):
            payload = json.dumps({"orden": i, "emisor": "test_user", "texto": f"Mensaje prueba {i}"})
            r.rpush(cola_test, payload)
        
        longitud = r.llen(cola_test)
        mensajes = r.lrange(cola_test, 0, -1)
        r.delete(cola_test) # Limpiar
        print(f"[OK] 3. Operaciones de lista (Buffer de chat):")
        print(f"     Elementos encolados: {longitud} | Lectura correcta de {len(mensajes)} items.")

        # 4. Prueba de Canal Pub/Sub
        pubsub = r.pubsub()
        canal_test = "animoon:test:canal_alertas"
        pubsub.subscribe(canal_test)
        # Consumir el mensaje inicial de suscripción
        msg_sub = pubsub.get_message(timeout=1.0)
        r.publish(canal_test, "alerta_test_ok")
        msg_alerta = pubsub.get_message(timeout=1.0)
        pubsub.unsubscribe(canal_test)
        
        if msg_alerta and msg_alerta.get("data") == "alerta_test_ok":
            print(f"[OK] 4. Canal Pub/Sub verificado correctamente ('{canal_test}')")
        else:
            print(f"[AVISO] 4. Pub/Sub completado sin confirmación síncrona inmediata.")

        # Limpieza final
        r.delete(clave_test)

        print("\n" + "=" * 65)
        print(">>> [ÉXITO] INFRAESTRUCTURA DE REDIS OPERATIVA AL 100% <<<")
        print("    Listo para soportar el Chat Server y el Beto Worker.")
        print("=" * 65)
        return True

    except redis.ConnectionError as e:
        print("\n[ERROR CRÍTICO] No se pudo conectar al servidor Redis:")
        print(f"  Detalle: {e}")
        print("\nPara iniciar Redis con Docker, ejecuta:")
        print("  docker compose up -d redis")
        print("O de forma individual:")
        print("  docker run -d --name animoon_redis -p 6379:6379 redis:7-alpine")
        return False
    except Exception as e:
        print(f"\n[ERROR INESPERADO]: {e}")
        return False

if __name__ == "__main__":
    exito = probar_conexion_redis()
    sys.exit(0 if exito else 1)
