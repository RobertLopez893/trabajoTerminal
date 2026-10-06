# Análisis del Backend de Animoon V2

## 1. Estado Actual del Backend
He revisado el código de tu backend, el script de base de datos (`bd_v2.sql`) y los documentos de requerimientos. Actualmente, el backend tiene una buena base arquitectónica pero le faltan piezas críticas para cumplir con los requerimientos de la V2.

### ✅ Lo que ya está implementado y en orden:
1. **Base de Datos y Modelos:** Los esquemas SQL (`bd_v2.sql`) y los modelos de SQLAlchemy (`models.py`, `models_auditoria.py`) coinciden y cubren todas las tablas necesarias (Usuarios, Tokens, Chat, Mensajes, Bloques, Apelaciones, Auditoría).
2. **Criptografía (Cifrado doble):** El servidor de WebSockets en `chat_server.py` ya implementa conexiones TLS 1.3 y exige cifrado AES-256-GCM a nivel de aplicación (Zero-Trust).
3. **Estructura API REST:** Tienes los controladores para `auth.py`, `minigames.py`, `environment.py`, etc., lo que da soporte al frontend.

---

## 2. Lo que FALTA implementar (Brechas con los Requerimientos)

### A. Lógica de Acumulación en el Chat (RF-CH-06)
Actualmente, `chat_server.py` descifra el mensaje y lo retransmite, pero **no está guardando los mensajes en la base de datos** (tablas `CHAT` y `MENSAJE`) y, lo más importante, **no está acumulando los mensajes en bloques de 20** para enviarlos al modelo.

### B. Integración de Traducción (RF-SG-02)
El documento de seguridad exige que los mensajes se traduzcan del español al inglés antes de pasarlos al modelo PLN. Esto aún no existe en el código.

### C. Mock del Modelo PLN y Flujo de Moderación (RF-CH-07)
No hay ninguna llamada al modelo de detección de grooming. Cuando se implemente el mock, si este devuelve positivo (grooming detectado), el backend debe:
1. Suspender la cuenta del agresor automáticamente (`is_banned = True`).
2. Generar un registro inmutable en la base de datos de auditoría (`LOG_AUDITORIA`).
3. Disparar un SMS de alerta al tutor (usando `twilio_service.py`).
4. Bloquear la sesión de chat actual.

### D. Duplicidad de WebSockets
Tienes dos implementaciones de chat: 
- `api/chat.py` (usando FastAPI y JWT) 
- `chat/chat_server.py` (servidor puro de websockets con cifrado AES-GCM)
Debemos unificar esto o asegurarnos de que el frontend apunte al correcto (`chat_server.py` parece ser el que tiene la seguridad avanzada exigida en los PDFs).

---

## 3. Plan Sugerido para el Mock del Modelo PLN

Ya que no tienes el modelo real todavía, te propongo crear un servicio interno (ej. `nlp_service.py`) con una clase `NLPMock` que simule el flujo completo:

```python
# backend/api/nlp_mock.py
import random
import asyncio

class NLPMockService:
    async def translate_to_english(self, texts: list[str]) -> list[str]:
        # Simula la latencia de un servicio de traducción (ej. DeepL/Google)
        await asyncio.sleep(0.5)
        return [f"[EN] {text}" for text in texts]
        
    async def analyze_block(self, block_messages: list[str]) -> dict:
        """
        Recibe un bloque de 20 mensajes.
        Devuelve un diccionario con el veredicto simulado.
        """
        # 1. Traducir al inglés (Requerimiento RF-SG-02)
        translated_texts = await self.translate_to_english(block_messages)
        
        # Simula latencia del modelo (máximo 5s según RNF-CH-02)
        await asyncio.sleep(1.5)
        
        # 2. Mock de detección (10% de probabilidad de detectar grooming para pruebas)
        is_grooming = random.random() < 0.10
        confidence = round(random.uniform(0.85, 0.99), 2) if is_grooming else round(random.uniform(0.10, 0.40), 2)
        
        return {
            "grooming_detectado": is_grooming,
            "confidence_score": confidence,
            "fase_detectada": "trust_building" if is_grooming else None,
            "modelo_version": "mock_v1.0"
        }
```

### Próximos pasos recomendados:
1. ¿Te gustaría que agreguemos la lógica para que `chat_server.py` inserte los mensajes en la base de datos y cree el `BLOQUE_ANALISIS`?
2. ¿Quieres que implementemos de una vez el servicio Mock sugerido arriba y conectemos las alertas (ban + SMS)?
