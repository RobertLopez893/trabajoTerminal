# 🚀 Práctica y Guía de Integración de Redis con Animoon y Modelo PLN

Este módulo contiene la explicación práctica y el código funcional para entender cómo conectar el **Servidor de Chat de Animoon** con el **Modelo de Procesamiento de Lenguaje Natural (PLN / Detección de Grooming)** utilizando **Redis**.

---

## 🧐 ¿Por qué te dijeron que debes usar Redis?

En tu proyecto existen dos componentes clave:
1. **Chat Server (`backend/chat/chat_server.py`)**: Maneja conexiones WebSockets en tiempo real con cifrado AES-GCM. Necesita entregar mensajes en milisegundos sin latencia perceptible.
2. **Modelo de PLN (`proyecto_pln/test.py` con BERT + LoRA)**: Analiza el texto para detectar grooming o riesgo infantil en ventanas de contexto de 5 mensajes. Las redes neuronales profundas consumen CPU/GPU y tardan entre 40ms y 500ms por inferencia.

### Los problemas de conectarlos directamente (sin Redis):
* ⚠️ **Bloqueo del chat (Lag severo)**: Si ejecutas la red neuronal directamente en el evento del WebSocket, el chat se congelará mientras BERT procesa.
* ⚠️ **Sobrecarga en PostgreSQL**: Tu modelo necesita los últimos 5 mensajes (`VENTANA = 5`) de la sala para entender el contexto. Consultar PostgreSQL con `SELECT ... ORDER BY timestamp DESC LIMIT 5` en cada mensaje genera una sobrecarga enorme de lectura en disco.

### Las soluciones que aporta Redis:
* ⚡ **1. Memoria de Ultra Alta Velocidad (RAM)**: Redis guarda y recupera datos en submilisegundos (< 1 ms).
* ⚡ **2. Buffer de Contexto en RAM (`RPUSH` + `LTRIM`)**: Mantiene exactamente los últimos 5 mensajes de cada chat en memoria. Cuando llega el 6to mensaje, el 1ero se descarta automáticamente.
* ⚡ **3. Cola de Mensajes Asíncrona (Productor - Consumidor)**: El Chat Server entrega el mensaje al usuario de inmediato y "avienta" una copia a una cola de Redis (`LPUSH`). Un proceso independiente ("Worker") extrae las tareas (`BRPOP`) y las analiza sin tocar al chat.
* ⚡ **4. Alertas en Tiempo Real (`Pub/Sub`)**: Si el Worker detecta peligro crítico (Nivel 2), publica una alerta inmediata a un canal de Redis (`canal_alertas_grooming`) para que el backend suspenda la sala o alerte a un tutor.

---

## 🏗️ Arquitectura del Flujo de Datos

```
[ Usuario A ]                     [ Usuario B ]
      │                                 ▲
      │ (1. Envía mensaje por WS)       │ (2. Entrega inmediata sin lag)
      ▼                                 │
 ┌──────────────────────────────────────────┐
 │        Animoon Chat Server               │
 │        (backend/chat/chat_server.py)     │
 └────────────────────┬─────────────────────┘
                      │ (3. Actualiza buffer & encola tarea)
                      ▼
 ┌──────────────────────────────────────────┐
 │             REDIS (En RAM)               │
 │  - contexto:{chat_id} (últimos 5 msgs)   │
 │  - cola_mensajes_nlp (Lista FIFO)        │
 │  - canal_alertas_grooming (Pub/Sub)      │
 └────────────────────┬─────────────────────┘
                      │ (4. BRPOP: Despierta cuando hay tareas)
                      ▼
 ┌──────────────────────────────────────────┐
 │         Worker de PLN (NLP Model)        │
 │         - Lee ventana de 5 msgs de RAM   │
 │         - Ejecuta BERT + LoRA            │
 │         - Si riesgo >= 1: emite alerta   │
 └──────────────────────────────────────────┘
```

---

## 🛠️ Cómo tener Redis funcionando

El contenedor de Redis ya fue iniciado mediante Docker:
```bash
docker run -d --name animoon_redis -p 6379:6379 redis:alpine
```

Para agregarlo definitivamente al `docker-compose.yml` de Animoon:
```yaml
services:
  # ... servicios existentes (db, api, chat_server) ...
  
  redis:
    image: redis:alpine
    container_name: animoon_redis
    restart: always
    ports:
      - "6379:6379"
```

---

## 🧪 Prácticas Incluidas

Para ejecutar estos scripts, asegúrate de activar tu entorno virtual:
```powershell
cd "c:\Users\lopez\Desktop\Tareas ESCOM\Trabajo Terminal\trabajoTerminal"
.\venv\Scripts\Activate.ps1
```

### 1. `01_conceptos_basicos.py`
Aprende las 3 operaciones clave de Redis explicadas paso a paso:
```powershell
python .\practica_redis\01_conceptos_basicos.py
```

### 2. `02_productor_chat.py` y `03_consumidor_nlp_worker.py` (Dos terminales)
Simulación interactiva cliente-servidor:
* **Terminal 1**: Ejecuta el Worker:
  ```powershell
  python .\practica_redis\03_consumidor_nlp_worker.py
  ```
* **Terminal 2**: Ejecuta el Chat simulador:
  ```powershell
  python .\practica_redis\02_productor_chat.py
  ```
  *(Elige la opción 1 para enviar una conversación sospechosa o la opción 3 para escribir tú mismo).*

### 3. `04_demo_completa.py` (Demostración automática "Todo en Uno")
Ejecuta tanto el Chat, el Worker y el Monitor de Alertas en hilos concurrentes en una sola pantalla:
```powershell
python .\practica_redis\04_demo_completa.py
```
