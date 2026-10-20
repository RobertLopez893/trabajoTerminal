"""
=============================================================================
PRÁCTICA REDIS - PARTE 1: CONCEPTOS BÁSICOS APLICADOS A ANIMOON
=============================================================================
En este script aprenderás las 3 estructuras de Redis fundamentales para conectar
el Chat de Animoon con el modelo de Procesamiento de Lenguaje Natural (PLN).

1. CLAVE-VALOR (Strings con expiración / TTL): Sesiones y tokens rápidos.
2. LISTAS COMO BUFFER / VENTANA DESLIZANTE: Mantener los últimos 5 mensajes en RAM.
3. LISTAS COMO COLAS DE TAREAS (FIFO): Productor (Chat) y Consumidor (Modelo PLN).
=============================================================================
"""

import redis
import json
import time
import sys

# Asegurar codificación utf-8 en terminales Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def conectar_redis():
    try:
        # decode_responses=True convierte automáticamente los bytes a strings de Python
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        print("[OK] Conectado exitosamente a Redis en localhost:6379\n")
        return r
    except redis.ConnectionError:
        print("[ERROR] No se pudo conectar a Redis. Asegúrate de tener el contenedor corriendo:")
        print("   docker run -d --name animoon_redis -p 6379:6379 redis:alpine")
        exit(1)

def demo_1_clave_valor(r: redis.Redis):
    print("=" * 60)
    print("1. CLAVE-VALOR (Strings con Expiración)")
    print("=" * 60)
    print("Ideal para guardar estados temporales, ej: '¿El usuario X está activo?'\n")

    # Guardar un valor con tiempo de vida (ex = segundos)
    r.set("usuario:101:estado", "escribiendo...", ex=5)
    valor = r.get("usuario:101:estado")
    ttl = r.ttl("usuario:101:estado")
    print(f"-> Clave guardada: 'usuario:101:estado' = '{valor}' (Expira en {ttl}s)")
    print("-> En PostgreSQL esto requeriría un UPDATE en disco. En Redis está en RAM.\n")

def demo_2_ventana_contexto(r: redis.Redis):
    print("=" * 60)
    print("2. BUFFER DE CONTEXTO (Los últimos 5 mensajes en RAM)")
    print("=" * 60)
    print("Tu modelo BERT necesita una ventana de 5 mensajes para detectar grooming.")
    print("En lugar de hacer 'SELECT ... LIMIT 5' en PostgreSQL en cada mensaje,")
    print("Redis guarda la ventana usando RPUSH + LTRIM en 0.2 milisegundos.\n")

    sala_id = "chat_sala_demo"
    clave_contexto = f"contexto:{sala_id}"
    
    # Limpiamos por si existía de pruebas anteriores
    r.delete(clave_contexto)

    mensajes_prueba = [
        "Usuario A: Hola, ¿juegas Roblox?",
        "Usuario B: Sí, me gusta mucho.",
        "Usuario A: ¿Qué nivel eres?",
        "Usuario B: Nivel 15.",
        "Usuario A: Oye, ¿cuántos años tienes?",
        "Usuario B: Tengo 11.",
        "Usuario A: ¿Estás solo en tu casa ahorita?"  # Mensaje 7: los primeros 2 deben salir del buffer
    ]

    for msg in mensajes_prueba:
        # 1. Agregamos al final de la lista
        r.rpush(clave_contexto, msg)
        # 2. Recortamos para que SIEMPRE conserve solo los últimos 5 elementos (índices -5 a -1)
        r.ltrim(clave_contexto, -5, -1)

    # Obtenemos todos los elementos de la ventana actual
    ventana_actual = r.lrange(clave_contexto, 0, -1)
    
    print(f"Total de mensajes enviados: {len(mensajes_prueba)}")
    print(f"Mensajes conservados en la ventana de Redis (Tamaño = {len(ventana_actual)}):")
    for i, m in enumerate(ventana_actual, 1):
        print(f"   [{i}] {m}")
    print()

def demo_3_cola_productor_consumidor(r: redis.Redis):
    print("=" * 60)
    print("3. COLA DE TAREAS (Productor - Consumidor)")
    print("=" * 60)
    print("El chat (Productor) envía mensajes a la cola con LPUSH.")
    print("El worker del modelo PLN (Consumidor) los extrae con RPOP / BRPOP.\n")

    cola_nombre = "cola_mensajes_nlp"
    r.delete(cola_nombre)

    # SIMULACIÓN DEL CHAT SERVER (PRODUCTOR)
    mensaje_chat = {
        "chat_id": "sala_101",
        "sender_id": "usr_depredador",
        "texto": "pásame tu whats y no le digas a tus papás",
        "timestamp": time.time()
    }
    print(f"[CHAT SERVER] Recibió mensaje de '{mensaje_chat['sender_id']}'.")
    print(f"[CHAT SERVER] Lo entrega al destinatario al instante (0 lag).")
    print(f"[CHAT SERVER] 'Avienta' copia a la cola de Redis: '{cola_nombre}'...")
    
    # Encolar en Redis (convertido a JSON string)
    r.lpush(cola_nombre, json.dumps(mensaje_chat))
    print(f"[REDIS] Mensajes en espera en la cola: {r.llen(cola_nombre)}\n")

    # SIMULACIÓN DEL WORKER DE PLN (CONSUMIDOR)
    print("[MODELO PLN] Worker en segundo plano revisando la cola...")
    # rpop extrae el elemento más antiguo de la cola (FIFO: First-In, First-Out)
    item_extraido = r.rpop(cola_nombre)
    
    if item_extraido:
        datos = json.loads(item_extraido)
        print(f"[MODELO PLN] Mensaje extraído con éxito:")
        print(f"             Sala: {datos['chat_id']}")
        print(f"             Texto a clasificar: \"{datos['texto']}\"")
        print(f"[MODELO PLN] Ahora BERT puede clasificarlo sin trabar el chat WebSocket!\n")

if __name__ == "__main__":
    r = conectar_redis()
    demo_1_clave_valor(r)
    demo_2_ventana_contexto(r)
    demo_3_cola_productor_consumidor(r)
    print("=" * 60)
    print(">>> [EXITO] Practica 1 completada con exito! <<<")
    print("=" * 60)
