"""
=============================================================================
PRÁCTICA REDIS - PARTE 3: EL CONSUMIDOR (WORKER DEL MODELO DE PLN)
=============================================================================
Este script representa el Worker del Modelo de PLN de Animoon:
1. Se queda escuchando en segundo plano la cola 'cola_mensajes_nlp' usando BRPOP
   (Bloqueo eficiente: consume 0% de CPU mientras no haya mensajes).
2. Cuando el Chat envía un mensaje, el Worker despierta de inmediato.
3. Lee de Redis la ventana de los últimos 5 mensajes de esa sala (RAM).
4. Realiza el análisis de riesgo (simulado o conectando BERT).
5. Si detecta riesgo Nivel 1 o 2 (Grooming), emite una ALERTA en tiempo real
   a través del canal Pub/Sub 'canal_alertas_grooming'.
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

# Definición de niveles según el Trabajo Terminal
NIVELES_RIESGO = {
    0: ("BAJO RIESGO", "Charla comun, videojuegos, tareas"),
    1: ("RIESGO MEDIO", "Sondeo de edad, aislamiento, pedir otras redes"),
    2: ("ALTO RIESGO", "Grooming explicito, fotos, verse a solas, secreto")
}

def clasificador_reglas_demostracion(ventana_mensajes: list) -> tuple:
    """
    Clasificador didáctico para la práctica que analiza la ventana de contexto.
    (En producción, aquí se llama a clasificar_ventana de BERT / LoRA).
    """
    texto_acumulado = " | ".join(ventana_mensajes).lower()

    # Patrones de alto riesgo (Nivel 2)
    alto_riesgo_palabras = [
        "estas solo", "estas sola", "te quedas solo", "no le digas a tus papas",
        "es un secreto", "pasa pack", "manda foto", "nos vemos en", "direccion de tu escuela"
    ]
    # Patrones de riesgo medio (Nivel 1)
    medio_riesgo_palabras = [
        "cuantos anos tienes", "cuantos tienes", "que edad tienes", "pasame tu whats",
        "tienes insta", "pasa tu cel", "tus papas no te entienden", "jefes"
    ]

    for p in alto_riesgo_palabras:
        if p in texto_acumulado:
            return 2, {"Bajo": 0.05, "Medio": 0.15, "Alto": 0.80}

    for p in medio_riesgo_palabras:
        if p in texto_acumulado:
            return 1, {"Bajo": 0.15, "Medio": 0.70, "Alto": 0.15}

    return 0, {"Bajo": 0.90, "Medio": 0.08, "Alto": 0.02}

def iniciar_worker():
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
    except redis.ConnectionError:
        print("[ERROR] No se pudo conectar a Redis en localhost:6379.")
        print("Inicia el contenedor con: docker run -d --name animoon_redis -p 6379:6379 redis:alpine")
        sys.exit(1)

    nombre_cola = "cola_mensajes_nlp"
    canal_alertas = "canal_alertas_grooming"

    print("=" * 65)
    print("      WORKER DE PLN — CONSUMIDOR EN SEGUNDO PLANO (REDIS)    ")
    print("=" * 65)
    print(f"[*] Escuchando la cola de tareas: '{nombre_cola}'")
    print(f"[*] Canal de alertas Pub/Sub:      '{canal_alertas}'")
    print(f"[*] Esperando mensajes del chat de Animoon... (Ctrl+C para salir)\n")

    contador_procesados = 0

    try:
        while True:
            # BRPOP (Blocking Right Pop):
            # Espera eficientemente hasta que haya un elemento en la cola.
            # timeout=0 significa espera indefinida sin consumir CPU.
            resultado = r.brpop(nombre_cola, timeout=0)
            
            if not resultado:
                continue

            cola_origen, item_json = resultado
            datos = json.loads(item_json)
            contador_procesados += 1

            chat_id = datos.get("chat_id")
            emisor = datos.get("emisor")
            texto = datos.get("texto")
            hora = datos.get("hora_legible", "N/A")

            print(f"\n─────────────────────────────────────────────────────────────────")
            print(f"[WORKER #{contador_procesados}] Nuevo trabajo extraido de la cola ({hora})")
            print(f"  Sala: {chat_id} | Emisor: {emisor}")
            print(f"  Texto recibido: \"{texto}\"")

            # 1. RECUPERAR LA VENTANA DE CONTEXTO DE REDIS EN RAM (sub-milisegundo)
            clave_contexto = f"contexto:{chat_id}"
            ventana_actual = r.lrange(clave_contexto, 0, -1)

            print(f"  Contexto recuperado de RAM ({len(ventana_actual)} mensajes):")
            for idx, msg in enumerate(ventana_actual, 1):
                print(f"     ({idx}) {msg}")

            # 2. INFERENCIA DEL MODELO (BERT + LoRA)
            t_inicio = time.time()
            nivel_pred, probs = clasificador_reglas_demostracion(ventana_actual)
            # Simulamos el tiempo de inferencia de una red neuronal pequeña (ej: 40ms)
            time.sleep(0.04)
            duracion_ms = (time.time() - t_inicio) * 1000

            nombre_riesgo, desc_riesgo = NIVELES_RIESGO[nivel_pred]

            print(f"  Analisis: {nombre_riesgo} (Procesado en {duracion_ms:.1f}ms)")
            print(f"  Probabilidades: Bajo={probs['Bajo']*100:.1f}% | Medio={probs['Medio']*100:.1f}% | Alto={probs['Alto']*100:.1f}%")

            # 3. SI HAY RIESGO, EMITIR ALERTA VIA REDIS PUB/SUB
            if nivel_pred >= 1:
                alerta_payload = {
                    "tipo": "ALERTA_GROOMING",
                    "nivel": nivel_pred,
                    "nombre_nivel": nombre_riesgo,
                    "chat_id": chat_id,
                    "emisor_sospechoso": emisor,
                    "ultimo_mensaje": texto,
                    "ventana_analizada": ventana_actual,
                    "timestamp": time.time()
                }

                # Publicar al canal de Redis para que el backend o moderador reaccione
                r.publish(canal_alertas, json.dumps(alerta_payload))

                # Guardar en un historial de alertas en Redis
                r.lpush(f"alertas:{chat_id}", json.dumps(alerta_payload))

                if nivel_pred == 2:
                    print(f"  >>> [PELIGRO CRITICO] ALERTA PUBLICADA A '{canal_alertas}' <<<")
                    print(f"  Accion sugerida: Notificar a tutor y solicitar intervencion inmediata.")
                else:
                    print(f"  >>> [ADVERTENCIA] ALERTA PUBLICADA A '{canal_alertas}' (Monitoreo activo)")

            else:
                print(f"  [ESTADO] Conversacion normal. No se emitio alerta.")

    except KeyboardInterrupt:
        print("\n[WORKER] Deteniendo worker de PLN. Hasta luego!")

if __name__ == "__main__":
    iniciar_worker()
