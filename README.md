<div align="center">
  <img src="animoon/app/src/main/res/drawable/logo_animoon.png" alt="Animoon Logo" width="190" />
  
  # Animoon 🌙
  **Protegiendo sonrisas en cada conexión virtual**
  
  *Un Prototipo de Entorno Virtual Anti-Grooming con Inteligencia Artificial*

  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Kotlin](https://img.shields.io/badge/Kotlin-Android_SDK_26+-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white)](https://kotlinlang.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15_Alpine-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![Redis](https://img.shields.io/badge/Redis-7_Alpine-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
  [![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![BETO](https://img.shields.io/badge/NLP-BETO_ONNX-FFAA00?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased)
</div>

<br>

> **Trabajo Terminal No. 2026 - B109**  
> *Escuela Superior de Cómputo (ESCOM) — Instituto Politécnico Nacional (IPN)*  
> *Ingeniería en Sistemas Computacionales*

---

## ✨ Descubre Animoon

**Animoon** es una plataforma integral diseñada para que niños de 6 a 13 años puedan interactuar, jugar y socializar en un entorno virtual seguro y controlado. El proyecto combina una aplicación móvil nativa para Android con una arquitectura de microservicios en el backend y un **guardián inteligente de Inteligencia Artificial (IA)**.

A diferencia de los enfoques tradicionales basados en listas estáticas de palabras prohibidas, Animoon incorpora un modelo de **Procesamiento de Lenguaje Natural (PLN)** basado en **BETO (Spanish BERT)** y optimizado con **ONNX Runtime**. El sistema analiza el contexto semántico y las intenciones en conversaciones en tiempo real, neutralizando patrones de acoso infantil (*grooming*) en etapas tempranas sin almacenar historiales de chat en disco de manera persistente.

---

## 🎯 Nuestros Objetivos

- 🛡️ **Entorno Seguro para Menores:** Ofrecer una experiencia lúdica e interactiva con avatares, un mundo virtual 2D explorable y minijuegos educativos orientados a la ciberseguridad infantil.
- 🧠 **Detección Semántica en Tiempo Real:** Analizar flujos de conversación mediante ventanas deslizantes con inferencia acelerada para detectar intenciones de manipulación, aislamiento, solicitud de datos privados o encuentros.
- 🚨 **Protocolo Inmediato de Contención:** Aislar y suspender al agresor de manera instantánea, proteger la experiencia emocional de la víctima mediante una pantalla amigable de salida (*Safe Exit*) y notificar de inmediato a los tutores legales vía SMS.
- 📜 **Validez Pericial y Privacidad:** Cumplir con principios estrictos de privacidad infantil (chats efímeros) al tiempo que se preserva evidencia criptográficamente inmutable en una base de datos de auditoría dedicada.

---

## 🚀 Características y Módulos Principales

### 1. 🔒 Registro y Consentimiento Parental
* Verificación obligatoria de tutor legal mediante código de un solo uso (**OTP vía SMS**) integrado con **Twilio**.
* Hashing y salting de contraseñas con el estándar de alta seguridad **Argon2id**.
* Cifrado simétrico de datos sensibles (números de teléfono de tutores) con **AES-256-GCM**.
* Consentimiento informado y visualización integrada del **Aviso de Privacidad**.

### 2. 🔑 Autenticación y Gestión de Sesiones
* Autenticación basada en **JSON Web Tokens (JWT)** con revocación activa de sesiones.
* Detección automática de cuentas suspendidas o sancionadas con bloqueo de acceso y canal directo de información.

### 3. 🌙 Mundo Virtual 2D Interactivo
* Exploración de escenarios lunares temáticos (**Aldea Principal**, **Cráteres** y **Lado Oscuro**) con delimitación precisa de colisiones (`WorldBoundsValidator`).
* Movimiento dinámico con animaciones de caminata y sincronización multijugador por salas en tiempo real.
* Transiciones fluidas entre zonas con pantallas de carga y retorno asistido.

### 4. 💬 Chat Social 100% Efímero y Seguro
* Comunicación en tiempo real a través de **WebSockets** sobre transporte seguro **TLS 1.3**.
* Cifrado de mensajes de extremo a extremo con **AES-256-GCM**.
* **Salas 100% efímeras:** Los mensajes conviven únicamente en memoria volátil/búfer temporal durante la sesión y se destruyen al cerrarse la sala, garantizando la privacidad de los menores.
* Sistema de invitaciones y notificaciones de chat discretas en tiempo real.

### 5. 🤖 Moderación Proactiva con IA (Microservicio BETO Worker)
* Inferencia continua en streaming mediante colas de mensajería en **Redis** (`queue:beto_jobs`).
* Análisis de ventanas contextuales con modelo **BETO** optimizado a formato **ONNX** para inferencia de latencia mínima en CPU.
* Algoritmo de atribución semántica para discernir fehacientemente quién es el menor y quién es el agresor.
* Búfer de corte a **10 mensajes** para evaluación continua y oportuna.

### 6. ⚡ Protocolo de Emergencia y Contención
* **Suspensión Quirúrgica:** Expulsión inmediata del agresor del WebSocket con código de desconexión `4003` y marcado permanente (`is_banned = True`).
* **Salida Segura (Safe Exit):** Pantalla amigable para el menor protagonizada por la mascota *Moonie*, previniendo revictimización o estrés.
* **Alerta SMS Inmediata:** Notificación por SMS al teléfono móvil del tutor con descripción del incidente vía Twilio.
* **Cadena de Custodia Criptográfica:** Registro automático en base de datos independiente de auditoría (`animoon_auditoria`) con evidencia cifrada con **AES-256-GCM** y sellada con **hash SHA-256**.

### 7. 🎮 Minijuegos Educativos de Ciberseguridad
* **Minijuego 1 (Trivia Cibersegura):** Preguntas interactivas sobre identificación de riesgos en línea y hábitos seguros en internet.
* **Minijuego 2 (Cable Board / Clasificación):** Mecánica interactiva para diferenciar mensajes confiables de intentos de persuasión o engaño.
* **Minijuego 3 (Reto Lunar):** Reto dinámico de reacción y toma de decisiones seguras.
* Persistencia y visualización de puntuaciones y estadísticas en el perfil del jugador.

### 8. 👨‍👩‍👧 Portal de Padres y Sistema de Apelaciones
* **Panel de Padres:** Acceso protegido para consultar el historial de incidentes, estado de la cuenta del menor y recomendaciones preventivas.
* **Módulo de Apelaciones:** Formulario formal para que usuarios o tutores puedan apelar suspensiones, permitiendo la revisión administrativa de casos.

---

## 🛠️ Arsenal Tecnológico

<div align="center">

| Componente | Tecnologías Utilizadas | Propósito en el Sistema |
| :--- | :--- | :--- |
| **📱 Frontend Móvil** | **Android Nativo, Kotlin, Coroutines, Jetpack** | Aplicación móvil, renderizado 2D, animaciones, controles táctiles y consumo de APIs. |
| **🌐 API REST Principal** | **Python 3.11+, FastAPI, Uvicorn, Pydantic** | Registro, autenticación, perfiles, minijuegos, portal parental y apelaciones. |
| **⚡ Servidor de Chat** | **Python asíncrono (`websockets`), TLS 1.3** | Conexiones persistentes en tiempo real, cifrado y encolado de mensajes. |
| **🧠 Motor IA / NLP** | **BETO (Spanish BERT), PyTorch, ONNX Runtime** | Inferencia ultrarrápida en español para detección semántica de grooming. |
| **⚙️ Worker Asíncrono** | **Microservicio BETO Worker en Python** | Consumidor BRPOP en Redis para análisis no bloqueante de bloques de chat. |
| **🗄️ Base de Datos Operacional** | **PostgreSQL 15 Alpine (SQLAlchemy)** | Persistencia de usuarios, sesiones, avatares, puntuaciones y bloques. |
| **📜 Base de Datos de Auditoría** | **PostgreSQL 15 Alpine (Aislada)** | Registro pericial inmutable con hashes SHA-256 y evidencia cifrada con AES-GCM. |
| **📬 Broker y Caché** | **Redis 7 Alpine** | Colas de inferencia (`queue:beto_jobs`), pub/sub de eventos y caché de presencia. |
| **🛡️ Criptografía y Seguridad** | **Argon2id, AES-256-GCM, SHA-256, JWT, TLS 1.3** | Protección de contraseñas, cifrado E2E de chats, integridad de logs y tokens. |
| **📲 Notificaciones SMS** | **Twilio Messages & Verify API** | Envío de códigos OTP de registro y alertas de seguridad críticas a tutores. |
| **🐳 Contenedores y DevOps** | **Docker, Docker Compose, AWS EC2** | Orquestación reproducible de 5 microservicios y despliegue en la nube. |
| **📈 Metodología y Calidad** | **Scrumban, ISO/IEC 12207, Pytest, Benchmarks** | Ciclo de vida estandarizado, 48 pruebas integrales y pruebas de estrés. |

</div>

---

## 🏛️ Arquitectura de Microservicios

El sistema opera bajo un desacoplamiento modular en contenedores Docker para garantizar alta concurrencia, tolerancia a fallos y aislamiento de seguridad:

```text
                               ┌──────────────────────────────────────────────────┐
                               │           APLICACIÓN MÓVIL ANIMOON               │
                               │          (Android Nativo en Kotlin)              │
                               └─────────┬──────────────────────────────┬─────────┘
                                         │ HTTPS (Puerto 8000)          │ WSS / TLS 1.3 (Puerto 8765)
                                         ▼                              ▼
                          ┌────────────────────────────┐  ┌────────────────────────────┐
                          │     animoon_backend        │  │        animoon_chat        │
                          │   (FastAPI REST Server)    │  │  (WebSocket Chat Server)   │
                          └──────────────┬─────────────┘  └─────────────┬──────────────┘
                                         │                              │
                    ┌────────────────────┼──────────────────────────────┴─────┐
                    │                    ▼                                    │
                    │      ┌───────────────────────────┐                      │
                    │      │       animoon_redis       │                      │
                    │      │ (Colas BRPOP y Pub/Sub)   │                      │
                    │      └─────────────┬─────────────┘                      │
                    │                    │ Encolado de Bloques                │
                    │                    ▼                                    │
                    │      ┌───────────────────────────┐                      │
                    │      │    animoon_beto_worker    │                      │
                    │      │  (Inferencia BETO ONNX)   │                      │
                    │      └──────┬─────────────┬──────┘                      │
                    │             │             │                             │
                    │             ▼             ▼                             │
                    │   ┌────────────────┐ ┌────────────────┐                 │
                    │   │animoon_postgres│ │animoon_postgres│                 │
                    │   │ (Operacional)  │ │  (Auditoría)   │                 │
                    │   └────────────────┘ └────────────────┘                 │
                    │             │                                           │
                    │             ▼ Alerta Crítica SMS                        │
                    │     ┌────────────────┐                                  │
                    │     │   Twilio API   │ ──────► Celular del Tutor         │
                    │     └────────────────┘                                  │
                    └─────────────────────────────────────────────────────────┘
```

---

## ⚙️ ¿Cómo funciona la protección en caliente?

1. **Registro Supervisado:** El tutor registra al menor e ingresa su número celular. El sistema valida el número mediante un código SMS OTP y almacena las credenciales con **Argon2id** y el teléfono cifrado con **AES-256-GCM**.
2. **Interacción y Juego:** El menor explora el mundo 2D, juega minijuegos e inicia salas de chat efímeras con otros jugadores mediante WebSockets.
3. **Monitoreo en Streaming:** Conforme los mensajes fluyen cifrados, el servidor de chat los acumula en memoria. Al alcanzar una ventana de **10 mensajes**, empaqueta un bloque y lo inserta en la cola `queue:beto_jobs` de Redis.
4. **Inferencia Asíncrona:** El microservicio `beto_worker` extrae el bloque mediante BRPOP y ejecuta el modelo **BETO ONNX**. Si los mensajes son seguros, el diálogo continúa sin interrupciones.
5. **Activación del Protocolo de Contención (Ante Grooming):**
   * **Expulsión:** Se publica en el canal Redis `channel:grooming_alerts`. El servidor de chat cierra de inmediato la conexión del agresor con código `4003` y marca su cuenta como baneada (`is_banned = True`).
   * **Salida Segura:** La víctima recibe el evento `SAFE_EXIT` que despliega una interfaz amigable con la mascota Moonie explicando la salida sin alarmismos.
   * **Alerta SMS:** El worker descifra el teléfono del tutor de la víctima y despacha un SMS de alerta automática vía Twilio.
   * **Auditoría Pericial:** Se genera un registro inmutable en `animoon_auditoria` con la evidencia cifrada con AES-GCM y su hash de integridad **SHA-256**.

---

## 🚀 Guía de Instalación y Ejecución

Para ejecutar la plataforma localmente se requieren **Docker Desktop**, **Python 3.10+** y **Android Studio**.

### 1. Clonar el repositorio y configurar variables de entorno
```bash
# Generar llaves criptográficas (.env) de forma automática
python setup_keys.py
```
Asegúrate de configurar en el archivo `.env` tus credenciales de Twilio (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VERIFY_SERVICE_SID`) para el envío real de SMS.

### 2. Iniciar el Backend con Docker Compose

Hemos creado scripts automatizados que detectan la dirección IP de tu máquina en la red local, actualizan automáticamente la configuración de Android (`local.properties` y `build.gradle.kts`) y levantan los 5 contenedores de Docker:

**En Windows (PowerShell):**
```powershell
.\start_docker.ps1
```

**En Linux / Mac / Git Bash:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

#### Puertos del Backend Expuestos:
* `8000`: API REST de FastAPI (`animoon_backend`).
* `8765`: Servidor WebSockets para Chat Seguro (`animoon_chat`).
* `5433`: PostgreSQL Operacional y Auditoría (`animoon_postgres` mapeado a 5432 interno).
* `6379`: Redis Broker (`animoon_redis`).

> **Nota para Pruebas en Dispositivos Físicos:** Si pruebas la app desde un teléfono o tableta real en lugar de un emulador, asegúrate de que el dispositivo esté en la misma red Wi-Fi y de que el **Firewall de tu sistema operativo permita el tráfico entrante en los puertos `8000` y `8765`**.

### 3. Compilar y Ejecutar la App de Android
1. Abre el proyecto ubicado en la carpeta `animoon/` con **Android Studio**.
2. Haz clic en **Sync Project with Gradle Files** (ícono del elefante 🐘).
3. Selecciona tu emulador o dispositivo físico conectado por depuración USB.
4. Presiona **Run 'app'** (▶️) para compilar e instalar.

*(También se incluyen ejecutables compilados directamente en la raíz del proyecto: `Animoon_Final_Release.apk` y `Animoon_release_1_2.apk`).*

---

## 🧪 Validación, Pruebas y Resultados

El proyecto cuenta con una exhaustiva batería de validación y control de calidad:

- **Batería de Pruebas Integrales Automatizadas (`ejecutar_pruebas_integrales.py`):**
  - **48 casos de prueba automatizados** ejecutados sobre los **12 módulos funcionales**.
  - Evaluación sobre 7 dimensiones de software: *Funcionalidad*, *Concurrencia*, *Seguridad*, *Rendimiento*, *Integridad de Datos*, *Usabilidad Infantil* y *Resiliencia*.
  - **100.0% de Cumplimiento Certificado** en el reporte oficial (`test_compliance_report.json`).

- **Benchmarking de Carga y Concurrencia (`backend/tests/benchmarks/`):**
  - Pruebas de estrés progresivo simulando **hasta 100 salas de chat concurrentes** sobre WebSockets y TLS 1.3 con cifrado AES-256-GCM.
  - Tiempos de reacción y corte de seguridad del protocolo de contención en un rango sub-segundo (< 200 ms).
  - Generación automatizada de reportes y gráficas de latencia, throughput y tiempo de seguridad a 300 DPI.

- **Pruebas de Campo con Menores (Colegio Thales de Mileto):**
  - Sesiones de evaluación con estudiantes de nivel básico validando la comprensión del lenguaje, navegación intuitiva en el mundo 2D, asimilación pedagógica de los minijuegos y aceptación del personaje Moonie.

---

## 📈 Ruta de Desarrollo (Ciclo ISO/IEC 12207)

- [x] **Iteración 0: Formulación y Diseño Conceptual** — Levantamiento de requerimientos, casos de uso, arquitectura de seguridad Zero-Trust y diseño UX infantil.
- [x] **Iteración 1: Inteligencia Artificial y PLN** — Creación de corpus sintético en español, entrenamiento y compresión de BETO con ONNX Runtime.
- [x] **Iteración 2: Autenticación, Registro y Criptografía** — Verificación SMS con Twilio, hashing Argon2id, cifrado AES-256-GCM, tokens JWT y Aviso de Privacidad.
- [x] **Iteración 3: Entorno Virtual 2D y Dinámicas Sociales** — Creación de escenarios lunares, sistema de colisiones, chat efímero sobre WebSockets y 3 minijuegos interactivos.
- [x] **Iteración 4: Integración del Pipeline de Seguridad y Microservicios** — Worker BETO asíncrono, canal Pub/Sub en Redis, protocolo Safe Exit, SMS al tutor, portal parental y módulo de apelaciones.
- [x] **Fase de Validación y Cierre** — Certificación del 100% de la batería de pruebas integrales, benchmarking de concurrencia y pruebas de campo en colegio.

---

## 👨‍💻 Equipo de Desarrollo

Proyecto desarrollado como requisito para la obtención del título de **Ingeniero en Sistemas Computacionales** en la **Escuela Superior de Cómputo (ESCOM)** del **Instituto Politécnico Nacional (IPN)**.

### Integrantes:
* 🌟 **González Martínez Silvia** — *sgonzalezm1902@alumno.ipn.mx*
* 🌟 **López Chávez Moisés** — *mlopezc2105@alumno.ipn.mx*
* 🌟 **López Reyes José Roberto** — *jlopezr1911@alumno.ipn.mx*
* 🌟 **Serrano Gayosso José Eduardo** — *jserranog1900@alumno.ipn.mx*

### Director del Proyecto:
* 🎓 **M. en C. López Rojas Ariel** — *arilopez@ipn.mx*

<br>

<div align="center">
  <i>"La tecnología al servicio de los que más queremos."</i> <br>
  <b>Escuela Superior de Cómputo — Instituto Politécnico Nacional</b>
</div>
