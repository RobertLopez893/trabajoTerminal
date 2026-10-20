"""
=============================================================================
PRÁCTICA REDIS - PARTE 2: EL PRODUCTOR (SIMULADOR DEL CHAT ANIMOON)
=============================================================================
Este script simula lo que haría 'backend/chat/chat_server.py':
Cuando dos usuarios se envían mensajes en el chat:
1. El servidor entrega el mensaje al destinatario inmediatamente (WebSockets).
2. Para NO trabar el chat con la inferencia de BERT, envía los datos a Redis:
   a) Actualiza la ventana de contexto de la sala (ultimos 5 mensajes).
   b) Encola la tarea en 'cola_mensajes_nlp' para que el Worker de PLN la analice.
=============================================================================
"""

import sys
import json
import time
import redis

# Asegurar codificación utf-8 en terminales Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def conectar_redis():
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        return r
    except redis.ConnectionError:
        print("[ERROR] No se pudo conectar a Redis en localhost:6379.")
        print("Asegurate de iniciar el contenedor con: docker run -d --name animoon_redis -p 6379:6379 redis:alpine")
        sys.exit(1)

def enviar_mensaje_al_chat(r: redis.Redis, chat_id: str, emisor: str, texto: str):
    """
    Simula la llegada de un mensaje al Chat Server de Animoon.
    """
    timestamp_actual = time.strftime("%H:%M:%S")
    mensaje_formateado = f"{emisor}: {texto}"

    print(f"\n[CHAT {timestamp_actual}] Nuevo mensaje de '{emisor}' en sala '{chat_id}':")
    print(f"             \"{texto}\"")

    # 1. ACTUALIZAR LA VENTANA DESLIZANTE EN REDIS (ultimos 5 mensajes en RAM)
    clave_contexto = f"contexto:{chat_id}"
    r.rpush(clave_contexto, mensaje_formateado)
    r.ltrim(clave_contexto, -5, -1)  # Mantener solo los últimos 5
    r.expire(clave_contexto, 86400) # Expira en 24h si el chat queda inactivo

    # 2. ENCOLAR TAREA PARA EL WORKER DE PLN
    # Empaquetamos la información que el modelo necesitará
    tarea_pln = {
        "chat_id": chat_id,
        "emisor": emisor,
        "texto": texto,
        "timestamp": time.time(),
        "hora_legible": timestamp_actual
    }

    # LPUSH coloca la tarea al inicio de la cola
    r.lpush("cola_mensajes_nlp", json.dumps(tarea_pln))
    print(f"  └─> [REDIS] Mensaje agregado al buffer de contexto (RAM).")
    print(f"  └─> [REDIS] Tarea encolada en 'cola_mensajes_nlp'. El chat queda libre al instante!")

def modo_interactivo():
    r = conectar_redis()
    print("=" * 65)
    print("       ANIMOON CHAT — SIMULADOR DE PRODUCTOR (REDIS) ")
    print("=" * 65)
    print("Este script envia mensajes simulados a la cola de Redis.")
    print("Deja corriendo en otra terminal '03_consumidor_nlp_worker.py' para ver")
    print("como el modelo procesa los mensajes en tiempo real.\n")
    print("Opciones:")
    print("  1. Enviar conversacion sospechosa predefinida (Grooming)")
    print("  2. Enviar conversacion normal (Videojuegos)")
    print("  3. Escribir mensajes manualmente")
    print("  4. Salir")
    print("=" * 65)

    sala_id = "sala_demo_101"

    while True:
        opcion = input("\nSelecciona una opcion (1-4): ").strip()

        if opcion == "1":
            # Conversacion con intencion de grooming progresivo
            mensajes = [
                ("Usuario A", "q onda morro, juegas roblox?"),
                ("Usuario B", "si, cual es tu user?"),
                ("Usuario A", "oye y cuantos anos tienes neta?"),
                ("Usuario B", "tengo 10"),
                ("Usuario A", "tus papas no te entienden wey, yo si te compro robux"),
                ("Usuario A", "estas solo en tu casa ahorita? pasame tu whats porfa")
            ]
            print("\n>>> Enviando conversacion sospechosa a la sala...")
            for emisor, texto in mensajes:
                enviar_mensaje_al_chat(r, sala_id, emisor, texto)
                time.sleep(1.0) # Simula pausa entre tecleo de usuarios

        elif opcion == "2":
            # Conversacion inocua
            mensajes = [
                ("Usuario A", "hola, que nivel tienes en minecraft?"),
                ("Usuario B", "apenas empece ayer, hice mi casa"),
                ("Usuario A", "esta chido, luego te ayudo a picar diamantes"),
                ("Usuario B", "va dale, manana nos conectamos en la tarde")
            ]
            print("\n>>> Enviando conversacion normal a la sala...")
            for emisor, texto in mensajes:
                enviar_mensaje_al_chat(r, sala_id, emisor, texto)
                time.sleep(1.0)

        elif opcion == "3":
            print("\nModo manual activado. Escribe con formato: Emisor: Mensaje (o 'volver')")
            while True:
                linea = input("> ").strip()
                if linea.lower() == "volver":
                    break
                if ":" in linea:
                    partes = linea.split(":", 1)
                    enviar_mensaje_al_chat(r, sala_id, partes[0].strip(), partes[1].strip())
                else:
                    print("Formato invalido. Usa 'Usuario A: texto' o 'Usuario B: texto'")

        elif opcion == "4":
            print("Saliendo del simulador de chat.")
            break
        else:
            print("Opcion invalida.")

if __name__ == "__main__":
    modo_interactivo()
