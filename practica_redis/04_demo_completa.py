"""
=============================================================================
PRÁCTICA REDIS - PARTE 4: DEMOSTRACIÓN COMPLETA EN VIVO (TODO EN UNO)
=============================================================================
Este script ejecuta todo el ecosistema de Animoon con Redis en un solo comando:
1. HILO 1 (Consumidor / Worker PLN): Lee mensajes de la cola de Redis y clasifica.
2. HILO 2 (Monitor de Alertas Pub/Sub): Escucha alertas de seguridad en tiempo real.
3. HILO PRINCIPAL (Chat Server): Envía una conversación simulada mensaje a mensaje.

Observarás cómo:
- El chat nunca se frena.
- Redis guarda la ventana de los últimos 5 mensajes en RAM.
- El modelo analiza en paralelo.
- Cuando hay grooming, se dispara la alerta instantáneamente.
=============================================================================
"""

import sys
import json
import time
import threading
import redis

# Asegurar codificación utf-8 en terminales Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

COLA_NLP = "cola_mensajes_nlp"
CANAL_ALERTAS = "canal_alertas_grooming"
SALA_ID = "chat_animoon_demo"

def conectar_redis():
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        return r
    except redis.ConnectionError:
        print("[ERROR] No se pudo conectar a Redis en localhost:6379.")
        print("Inicia el contenedor con: docker run -d --name animoon_redis -p 6379:6379 redis:alpine")
        sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. HILO DE MONITOREO DE ALERTAS (Pub/Sub)
# ─────────────────────────────────────────────────────────────────────────────
def hilo_monitor_alertas(detener_evento):
    r = conectar_redis()
    pubsub = r.pubsub()
    pubsub.subscribe(CANAL_ALERTAS)

    while not detener_evento.is_set():
        # get_message con timeout para poder salir limpiamente al final
        mensaje = pubsub.get_message(timeout=0.5)
        if mensaje and mensaje["type"] == "message":
            datos_alerta = json.loads(mensaje["data"])
            nivel = datos_alerta["nivel"]
            nombre = datos_alerta["nombre_nivel"]
            emisor = datos_alerta["emisor_sospechoso"]
            ultimo_txt = datos_alerta["ultimo_mensaje"]

            print(f"\n🔔 [SISTEMA DE SEGURIDAD / ALERTA RECIBIDA]")
            print(f"   >>> NIVEL: {nombre} (Nivel {nivel})")
            print(f"   >>> Sala: {datos_alerta['chat_id']} | Emisor: {emisor}")
            print(f"   >>> Detonante: \"{ultimo_txt}\"")
            if nivel == 2:
                print(f"   >>> ACCION AUTOMATICA: Notificando a padres y marcando chat para revision!")
            print()

# ─────────────────────────────────────────────────────────────────────────────
# 2. HILO DEL WORKER DE PLN (Consumidor)
# ─────────────────────────────────────────────────────────────────────────────
def hilo_worker_pln(detener_evento):
    r = conectar_redis()

    while not detener_evento.is_set():
        # Usamos timeout de 1 segundo para no quedar bloqueados indefinidamente al apagar
        resultado = r.brpop(COLA_NLP, timeout=1)
        if not resultado:
            continue

        _, item_json = resultado
        tarea = json.loads(item_json)

        chat_id = tarea["chat_id"]
        emisor = tarea["emisor"]
        texto = tarea["texto"]

        # Recuperar ventana de 5 mensajes desde Redis
        ventana = r.lrange(f"contexto:{chat_id}", 0, -1)
        texto_acumulado = " | ".join(ventana).lower()

        # Detección de patrones
        nivel = 0
        if any(w in texto_acumulado for w in ["estas solo", "no le digas a tus papas", "es un secreto", "manda foto"]):
            nivel = 2
        elif any(w in texto_acumulado for w in ["cuantos anos tienes", "pasame tu whats", "tus papas no te entienden"]):
            nivel = 1

        print(f"   [WORKER PLN] Proceso mensaje de '{emisor}' | Contexto en RAM: {len(ventana)} msgs | Nivel detectado: {nivel}")

        if nivel >= 1:
            alerta = {
                "nivel": nivel,
                "nombre_nivel": "ALTO RIESGO" if nivel == 2 else "RIESGO MEDIO",
                "chat_id": chat_id,
                "emisor_sospechoso": emisor,
                "ultimo_mensaje": texto
            }
            r.publish(CANAL_ALERTAS, json.dumps(alerta))

# ─────────────────────────────────────────────────────────────────────────────
# 3. HILO PRINCIPAL: SIMULADOR DE CONVERSACIÓN (Chat Server Productor)
# ─────────────────────────────────────────────────────────────────────────────
def ejecutar_demo():
    r = conectar_redis()

    # Limpiar estado previo en Redis para la prueba
    r.delete(COLA_NLP)
    r.delete(f"contexto:{SALA_ID}")

    detener = threading.Event()

    t_alertas = threading.Thread(target=hilo_monitor_alertas, args=(detener,), daemon=True)
    t_worker = threading.Thread(target=hilo_worker_pln, args=(detener,), daemon=True)

    t_alertas.start()
    t_worker.start()

    time.sleep(0.3)

    print("=" * 70)
    print("   DEMOSTRACIÓN COMPLETA: CHAT ANIMOON <---> REDIS <---> MODELO PLN")
    print("=" * 70)
    print("Se simulará una conversación en tiempo real:")
    print("1. Saludos normales de videojuegos (Nivel 0)")
    print("2. Pregunta de edad y aislamiento (Nivel 1)")
    print("3. Intento de verse a solas y secreto (Nivel 2 - Alarma)")
    print("=" * 70 + "\n")

    conversacion = [
        ("Usuario A", "Hola wey, juegas Free Fire o Roblox?"),
        ("Usuario B", "Que onda! Si, juego Roblox"),
        ("Usuario A", "Pasa tu user y te agrego"),
        ("Usuario B", "Soy xX_gamer10_Xx"),
        ("Usuario A", "Oye y cuantos anos tienes neta?"),
        ("Usuario B", "Tengo 9 anos"),
        ("Usuario A", "Tus papas no te entienden, yo te compro skins"),
        ("Usuario A", "Oye, estas solo en tu casa ahorita? Es un secreto, no le digas a tus papas")
    ]

    for emisor, texto in conversacion:
        time.sleep(1.2) # Pausa natural entre mensajes

        print(f"[CHAT SERVER] >> [{emisor}]: \"{texto}\"")

        # 1. Actualizar contexto en RAM
        r.rpush(f"contexto:{SALA_ID}", f"{emisor}: {texto}")
        r.ltrim(f"contexto:{SALA_ID}", -5, -1)

        # 2. Encolar tarea en Redis
        tarea = {
            "chat_id": SALA_ID,
            "emisor": emisor,
            "texto": texto
        }
        r.lpush(COLA_NLP, json.dumps(tarea))

    # Esperar a que el worker termine de procesar el último mensaje
    time.sleep(2.0)
    detener.set()

    print("\n" + "=" * 70)
    print("RESUMEN DE LO QUE OCURRIÓ:")
    print("1. El Chat Server nunca esperó la respuesta del modelo de IA.")
    print("2. Redis almacenó en RAM únicamente los últimos 5 mensajes:")
    ventana_final = r.lrange(f"contexto:{SALA_ID}", 0, -1)
    for i, m in enumerate(ventana_final, 1):
        print(f"   [{i}] {m}")
    print("3. El Worker de PLN procesó los mensajes en segundo plano de la cola.")
    print("4. El Sistema de Alertas recibió la notificación Pub/Sub en tiempo real.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    ejecutar_demo()
