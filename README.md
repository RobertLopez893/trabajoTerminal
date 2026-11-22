<div align="center">
  <img src="animoon/app/src/main/res/drawable/logo_animoon.png" alt="Animoon Logo" width="190" />
  
  # Animoon 🌙
  **Protecting smiles in every virtual connection**
  
  *A Virtual Environment Prototype with Anti-Grooming Artificial Intelligence*

  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Kotlin](https://img.shields.io/badge/Kotlin-Android_SDK_26+-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white)](https://kotlinlang.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15_Alpine-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![Redis](https://img.shields.io/badge/Redis-7_Alpine-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
  [![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![BETO](https://img.shields.io/badge/NLP-BETO_ONNX-FFAA00?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased)
</div>

<br>

> **Terminal Work Project No. 2026 - B109** (Trabajo Terminal)  
> *Escuela Superior de Cómputo (ESCOM) — Instituto Politécnico Nacional (IPN)*  
> *B.S. in Computer Systems Engineering*

---

## ✨ Discover Animoon

**Animoon** is a comprehensive digital platform designed for children aged 6 to 13 to interact, play, and socialize in a safe, monitored virtual environment. The project pairs a native Android mobile application with a containerized microservices backend powered by an **intelligent Artificial Intelligence (AI) guardian**.

Unlike conventional moderation systems that rely on static blacklists of prohibited keywords, Animoon features a **Natural Language Processing (NLP)** model based on **BETO (Spanish BERT)**, optimized with **ONNX Runtime**. The system analyzes conversational context and intent in real time, detecting and neutralizing online child grooming patterns at early stages without persistently storing children's chat histories on disk.

---

## 🎯 Our Objectives

- 🛡️ **Child-Safe Environment:** Provide a playful, interactive experience featuring customizable avatars, an explorable 2D virtual world, and educational minigames focused on child cybersecurity awareness.
- 🧠 **Real-Time Semantic Detection:** Analyze conversational streaming flows using sliding windows and accelerated inference to detect grooming behaviors such as manipulation, isolation, request of private data, or meeting invitations.
- 🚨 **Proactive Containment Protocol:** Instantly isolate and suspend the predator, protect the child's emotional wellbeing through a gentle *Safe Exit* screen, and promptly notify legal guardians via SMS.
- 📜 **Forensic Integrity & Privacy by Design:** Enforce strict child privacy standards (100% ephemeral chats) while preserving cryptographically immutable evidence in a dedicated audit database.

---

## 🚀 Key Features & System Modules

### 1. 🔒 Parental Registration & Consent
* Mandatory parental verification via **SMS One-Time Password (OTP)** powered by **Twilio**.
* Password hashing and salting using the modern, memory-hard **Argon2id** algorithm.
* Symmetric encryption of sensitive guardian phone numbers with **AES-256-GCM**.
* Explicit parental consent and integrated **Privacy Policy** acknowledgment.

### 2. 🔑 Authentication & Session Management
* Stateless authentication based on **JSON Web Tokens (JWT)** with active session revocation.
* Real-time detection of banned or suspended accounts with login prevention and direct access to the appeals channel.

### 3. 🌙 Interactive 2D Virtual World
* Thematic lunar zones to explore (**Main Village**, **Craters**, and **Dark Side**) with precise collision bounds (`WorldBoundsValidator`).
* Dynamic movement featuring custom walking animations and real-time room-isolated multiplayer presence.
* Smooth zone transitions with loading screens and assisted returns.

### 4. 💬 100% Ephemeral & Secure Chat
* Real-time communication via **WebSockets** over secure **TLS 1.3** transport.
* End-to-end message encryption with **AES-256-GCM**.
* **100% Ephemeral Rooms:** Messages reside solely in volatile memory / temporary buffers during active sessions and are destroyed upon exiting the room, leaving zero disk footprint of children's chats.
* Real-time chat invitations and discreet bubble notification alerts.

### 5. 🤖 Proactive AI Moderation (BETO Worker Microservice)
* Continuous streaming inference driven by **Redis** queues (`queue:beto_jobs`).
* Contextual sliding-window analysis powered by **BETO** optimized into **ONNX** format for ultra-low latency CPU inference.
* Heuristic semantic attribution to accurately distinguish the child victim from the predator.
* Processing threshold set to sliding windows of **10 messages** for timely threat detection.

### 6. ⚡ Emergency Containment Protocol
* **Surgical Suspension:** Immediate predator WebSocket severance with close code `4003` and permanent account suspension (`is_banned = True`).
* **Child-Friendly Safe Exit:** Supportive exit screen featuring the friendly mascot *Moonie*, preventing panic or revictimization.
* **Instant SMS Alert:** Real-time SMS dispatch to the guardian's mobile phone via Twilio detailing the security intervention.
* **Cryptographic Chain of Custody:** Automatic forensic event registration in an isolated audit database (`animoon_auditoria`) containing **AES-256-GCM** encrypted evidence sealed with **SHA-256 integrity hashes**.

### 7. 🎮 Educational Cybersecurity Minigames
* **Minigame 1 (Cybersecurity Trivia):** Interactive questions reinforcing safe internet habits and online risk awareness.
* **Minigame 2 (Cable Board / Message Sorting):** Hands-on classification mechanic teaching children to distinguish safe messages from social engineering or grooming attempts.
* **Minigame 3 (Lunar Reflex Challenge):** Dynamic decision-making minigame centered on digital safety choices.
* Backend persistence and display of player scores and achievements directly on the user profile.

### 8. 👨‍👩‍👧 Parents' Portal & Appeals System
* **Parent Dashboard:** Protected area for guardians to review security incident history, child account status, and digital safety guidance.
* **Appeals System:** Formal dispute mechanism allowing users or parents to submit sanction appeals for administrative review.

---

## 🛠️ Technology Arsenal

<div align="center">

| Component | Technologies | System Purpose |
| :--- | :--- | :--- |
| **📱 Mobile Frontend** | **Native Android, Kotlin, Coroutines, Jetpack** | Mobile app, 2D world rendering, animations, touch controls, and API consumption. |
| **🌐 Core REST API** | **Python 3.11+, FastAPI, Uvicorn, Pydantic** | Registration, authentication, profiles, minigames, parents' portal, and appeals. |
| **⚡ Live Chat Server** | **Asynchronous Python (`websockets`), TLS 1.3** | Persistent real-time connections, payload encryption, and message queuing. |
| **🧠 AI / NLP Engine** | **BETO (Spanish BERT), PyTorch, ONNX Runtime** | High-performance Spanish semantic inference for grooming detection. |
| **⚙️ Async Worker** | **Python Microservice (BETO Worker)** | Non-blocking BRPOP Redis consumer for processing conversation blocks. |
| **🗄️ Operational DB** | **PostgreSQL 15 Alpine (SQLAlchemy)** | Persistence of users, sessions, avatars, minigame scores, and analysis blocks. |
| **📜 Forensic Audit DB** | **PostgreSQL 15 Alpine (Isolated)** | Immutable audit trail with SHA-256 hashes and AES-GCM encrypted evidence. |
| **📬 Broker & Cache** | **Redis 7 Alpine** | Inference task queues (`queue:beto_jobs`), pub/sub alert channels, and session cache. |
| **🛡️ Cryptography & Security** | **Argon2id, AES-256-GCM, SHA-256, JWT, TLS 1.3** | Password hashing, E2E chat encryption, log tamper-evidence, and session tokens. |
| **📲 SMS Notifications** | **Twilio Messages & Verify API** | Registration OTP codes and critical security SMS alerts to legal guardians. |
| **🐳 Containers & DevOps** | **Docker, Docker Compose, AWS EC2** | Reproducible multi-container orchestration and cloud staging deployment. |
| **📈 Methodology & Quality** | **Scrumban, ISO/IEC 12207, Pytest, Benchmarks** | Standardized software lifecycle, 48 comprehensive automated tests, and stress tests. |

</div>

---

## 🏛️ Microservices Architecture

The system operates under a modular microservices pattern orchestrated in Docker containers to guarantee high concurrency, fault tolerance, and security boundary isolation:

```text
                               ┌──────────────────────────────────────────────────┐
                               │             ANIMOON MOBILE CLIENT                │
                               │            (Native Android - Kotlin)             │
                               └─────────┬──────────────────────────────┬─────────┘
                                         │ HTTPS (Port 8000)            │ WSS / TLS 1.3 (Port 8765)
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
                    │      │   (BRPOP Queues & Pub/Sub)│                      │
                    │      └─────────────┬─────────────┘                      │
                    │                    │ Enqueued Blocks                    │
                    │                    ▼                                    │
                    │      ┌───────────────────────────┐                      │
                    │      │    animoon_beto_worker    │                      │
                    │      │   (BETO ONNX Inference)   │                      │
                    │      └──────┬─────────────┬──────┘                      │
                    │             │             │                             │
                    │             ▼             ▼                             │
                    │   ┌────────────────┐ ┌────────────────┐                 │
                    │   │animoon_postgres│ │animoon_postgres│                 │
                    │   │ (Operational)  │ │    (Audit)     │                 │
                    │   └────────────────┘ └────────────────┘                 │
                    │             │                                           │
                    │             ▼ Critical SMS Alert                        │
                    │     ┌────────────────┐                                  │
                    │     │   Twilio API   │ ──────► Legal Guardian's Phone   │
                    │     └────────────────┘                                  │
                    └─────────────────────────────────────────────────────────┘
```

---

## ⚙️ How Real-Time Protection Works

1. **Supervised Registration:** The guardian registers the child and inputs their mobile phone number. The system verifies ownership via an SMS OTP, hashing the password with **Argon2id** and encrypting the guardian's phone number with **AES-256-GCM**.
2. **Exploration & Play:** The child navigates the 2D world, plays minigames, and initiates ephemeral chat sessions with peers over secure WebSockets.
3. **Streaming Ingestion:** Messages flow encrypted into server memory. Upon accumulating a sliding window of **10 messages**, the chat server packages an analysis block into Redis queue `queue:beto_jobs`.
4. **Asynchronous Inference:** The `beto_worker` consumes the block via BRPOP and executes the **BETO ONNX** pipeline. Normal, safe interactions proceed seamlessly without latency.
5. **Containment Protocol Triggered (Upon Grooming Detection):**
   * **Predator Severance:** An event is broadcast on Redis `channel:grooming_alerts`. The chat server drops the predator's WebSocket with code `4003` and flags their account as banned (`is_banned = True`).
   * **Child Safe Exit:** The victim receives a `SAFE_EXIT` payload that renders a reassuring, friendly interface with Moonie explaining that the room closed, avoiding distress.
   * **Parent SMS Alert:** The worker decrypts the guardian's phone number and dispatches an immediate SMS alert through Twilio.
   * **Forensic Audit Record:** A tamper-evident record is logged in `animoon_auditoria` with AES-GCM encrypted evidence and a cryptographic **SHA-256** hash for chain-of-custody verification.

---

## 🚀 Installation & Execution Guide

Running the platform locally requires **Docker Desktop**, **Python 3.10+**, and **Android Studio**.

### 1. Clone the Repository & Configure Environment Keys
```bash
# Generate cryptographic environment keys (.env) automatically
python setup_keys.py
```
Ensure you configure your Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VERIFY_SERVICE_SID`) in the generated `.env` file to enable real SMS delivery.

### 2. Launch the Backend with Docker Compose

Interactive scripts are provided to automatically detect your local IP address, update the Android configuration files (`local.properties` and `build.gradle.kts`), and spin up all 5 Docker containers:

**On Windows (PowerShell):**
```powershell
.\start_docker.ps1
```

**On Linux / macOS / Git Bash:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

#### Exposed Backend Ports:
* `8000`: FastAPI REST API (`animoon_backend`).
* `8765`: WebSocket Secure Chat Server (`animoon_chat`).
* `5433`: PostgreSQL Operational & Audit Database (`animoon_postgres` mapped to internal 5432).
* `6379`: Redis Message Broker (`animoon_redis`).

> **Testing on Physical Devices:** When running the mobile app on a real Android phone or tablet instead of an emulator, ensure the device is connected to the same local Wi-Fi network and that your **operating system firewall permits inbound connections on ports `8000` and `8765`**.

### 3. Build & Run the Android Application
1. Open the `animoon/` directory in **Android Studio**.
2. Click **Sync Project with Gradle Files** (elephant icon 🐘).
3. Select your emulator or physical Android device (connected via USB debugging).
4. Click **Run 'app'** (▶️) to build and install.

*(Pre-built production APKs are also available in the repository root: `Animoon_Final_Release.apk` and `Animoon_release_1_2.apk`).*

---

## 🧪 Validation, Testing & Results

The platform has been audited through an exhaustive quality assurance regimen:

- **Automated Comprehensive Test Harness (`ejecutar_pruebas_integrales.py`):**
  - **48 automated test cases** spanning all **12 functional modules**.
  - Evaluated across 7 software dimensions: *Functionality*, *Concurrency*, *Security*, *Performance*, *Data Integrity*, *Child Usability*, and *Resilience*.
  - **100.0% Certified Compliance** achieved in the official test report ([test_compliance_report.json](file:///c:/Users/lopez/Desktop/Tareas%20ESCOM/Trabajo%20Terminal/test_compliance_report.json)).

- **Concurrency & Stress Benchmarking (`backend/tests/benchmarks/`):**
  - Stress testing simulating **up to 100 concurrent chat rooms** over WebSockets with TLS 1.3 and AES-256-GCM encryption.
  - Sub-second containment reaction times (< 200 ms) from threat identification to connection drop.
  - Automated 300 DPI publication charts capturing throughput, latency percentiles, and security timing.

- **Field Testing with Schoolchildren (Colegio Thales de Mileto):**
  - Empirical usability sessions with elementary students validating vocabulary comprehension, 2D navigation intuitiveness, cybersecurity minigame engagement, and positive reception of the Moonie character.

---

## 📈 Development Roadmap (ISO/IEC 12207 Lifecycle)

- [x] **Iteration 0: Conceptual Design & Formulation** — Requirements engineering, use cases, Zero-Trust security model, and child UX design.
- [x] **Iteration 1: AI & NLP Core** — Synthetic Spanish corpus generation, BETO fine-tuning, and ONNX Runtime quantization/compression.
- [x] **Iteration 2: Authentication, Registration & Cryptography** — Twilio SMS OTP verification, Argon2id hashing, AES-256-GCM encryption, JWT sessions, and Privacy Policy.
- [x] **Iteration 3: 2D Virtual Environment & Social Dynamics** — Lunar exploration zones, collision detection, WebSocket ephemeral chat, and 3 interactive minigames.
- [x] **Iteration 4: Security Pipeline & Microservices Integration** — Async BETO worker, Redis Pub/Sub events, Safe Exit protocol, guardian SMS alerts, parents' portal, and appeals module.
- [x] **Final Validation & Verification Phase** — 100% compliance certified across 48 automated test cases, concurrency benchmarks, and real-world school field trials.

---

## 👨‍💻 Development Team

Developed as a degree requirement for obtaining the title of **Computer Systems Engineer** at the **Escuela Superior de Cómputo (ESCOM)** of the **Instituto Politécnico Nacional (IPN)**.

### Authors:
* 🌟 **González Martínez Silvia** — *sgonzalezm1902@alumno.ipn.mx*
* 🌟 **López Chávez Moisés** — *mlopezc2105@alumno.ipn.mx*
* 🌟 **López Reyes José Roberto** — *jlopezr1911@alumno.ipn.mx*
* 🌟 **Serrano Gayosso José Eduardo** — *jserranog1900@alumno.ipn.mx*

### Project Directors:
* 🎓 **M. en C. Ariel López Rojas** — *arilopez@ipn.mx*
* 🎓 **Dra. en C. Olga Kolesnikova** — *kolesnikova@cic.ipn.mx*  
  *(Doctora en Ciencias de la Computación)*

<br>

<div align="center">
  <i>"Technology in the service of those we love most."</i> <br>
  <b>Escuela Superior de Cómputo — Instituto Politécnico Nacional</b>
</div>
