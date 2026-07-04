# Propuesta de Reestructuración Arquitectónica y Distribución de Roles
**Proyecto:** ANIMOON (Trabajo Terminal)
**Tiempo restante:** ~5 meses
**Estado actual:** Fase de recolección de datos para el modelo PLN. Inicio de implementación general.

---

## 1. Motivación de la Reunión
Dada la naturaleza crítica del tiempo (5 meses) y la complejidad técnica del proyecto (Mundo Virtual + IA + Tiempo Real), es imperativo elegir las herramientas que nos permitan ser más ágiles y distribuir el trabajo de forma equitativa, aprovechando las fortalezas actuales de cada miembro del equipo.

## 2. Propuesta de Evolución del Stack Tecnológico

El diseño conceptual es excelente, pero la implementación práctica requiere ajustes para garantizar la fluidez (meta de ≥30 fps) y la facilidad de desarrollo.

### A) Frontend (Cliente Móvil)
*   **Problema actual:** Construir un "Mundo Virtual" interactivo, mover avatares y hacer minijuegos en vistas nativas de Android (XML/Compose con Kotlin) es extremadamente complejo y poco performante para un equipo pequeño.
*   **Propuesta:** Migrar el desarrollo del cliente móvil a **Godot Engine**.
    *   *Ventajas:* Es el estándar para interfaces gamificadas, muy ligero (ideal para teléfonos de 2GB RAM) y exporta nativamente a Android. Reduce meses de trabajo en físicas y renderizado.

### B) Backend y Base de Datos
*   **Problema actual:** La mensajería en tiempo real y la comunicación con el modelo de Inteligencia Artificial (BERT) requieren un manejo asíncrono muy robusto.
*   **Propuesta:** Unificar el backend en el ecosistema de Python utilizando **FastAPI** y migrar de MySQL a **PostgreSQL**.
    *   *Ventajas:* FastAPI maneja WebSockets nativamente de forma asíncrona (esencial para el chat). Al estar todo en Python, la integración con el modelo BERT es natural y directa. PostgreSQL maneja mejor los metadatos complejos que pueda arrojar la IA.

### C) Entorno de Desarrollo y Despliegue
*   **Propuesta:** Trabajar con desarrollo 100% local (`localhost`) en la primera etapa.
*   Utilizaremos archivos `.env` (variables de entorno) para proteger nuestras contraseñas y llaves criptográficas (las cuales nunca se subirán a GitHub).
*   Esta estructura nos dejará el camino pavimentado para implementar **Docker** (`docker-compose.yml`) fácilmente cuando estemos listos para el despliegue final.

---

## 3. Propuesta de Redistribución de Roles

Para evitar cuellos de botella (el "Bus Factor") y asegurar que el proyecto fluya sin sobrecargar a nadie, se sugiere la siguiente división enfocada en la especialización:

| Miembro | Rol Propuesto | Responsabilidades Principales |
| :--- | :--- | :--- |
| **Silvia** | Líder de Inteligencia Artificial | 100% dedicada al modelo PLN: limpieza del corpus, preprocesamiento, fine-tuning de BERT y pruebas del modelo. |
| **Eduardo** | Líder de Backend | Creación de la API en FastAPI, gestión de endpoints (login, registro) y levantamiento del servidor de WebSockets para el chat. |
| **Moy** | Base de Datos y Diseño UI/UX | Estructurar PostgreSQL. Proveer **todos los assets visuales** (botones, sprites, mapas) para el frontend. Apoyo en lógica de backend. |
| **López** | Líder de Frontend y Criptografía | Construir la app interactiva en Godot (ensamblando los assets de Moy). Programar el núcleo de seguridad matemática (AES-GCM, TLS, Argon2). |

---

## 4. Notas sobre la Base de Datos y Seguridad

Se validó el diseño de la base de datos (`bd_v2.sql`), que implementa de forma excelente el cifrado (`iv_nonce`, `tag`) y la arquitectura Append-Only. Se generó el documento **Servicios de Seguridad V3.md** con las siguientes optimizaciones de grado industrial:
1.  **Application-Layer Encryption (ALE):** Implementaremos un cifrado AES-GCM desde Godot hacia FastAPI, usando un protocolo idéntico al Handshake de TLS 1.3 con intercambio de llaves **ECDHE (X25519)** para asegurar Perfect Forward Secrecy.
2.  **Firmas EdDSA y Refactorización de BD:** Se eliminaron las columnas de `ecdsa_signature` de la base de datos. La firma no se guardará en tablas; en su lugar, el servidor usará la curva más avanzada de la industria **Twisted Edwards (Ed25519)** desde el `.env` para firmar los *Tokens de Sesión (JWT)* en memoria.

## 5. Puntos Adicionales a Discutir en la Reunión
1.  **Enfoque de Privacidad (ZKML + Cifrado Híbrido):** Presentar la propuesta de combinar ZKML con un "sobre criptográfico" para manejar las evidencias de forma ciega:
    *   *Generación de evidencia:* El entorno de inferencia detecta grooming y cifra simétricamente la conversación (AES-256-GCM).
    *   *Protección de llave:* La clave simétrica temporal se cifra asimétricamente usando la llave pública exclusiva del módulo de administradores (ej. curva elíptica).
    *   *Almacenamiento ciego:* La BD guarda la prueba ZKML, el texto cifrado y la llave cifrada. Ante cualquier filtración de la BD, la privacidad de los menores queda intacta.
    *   *Resolución de apelación:* Solo el administrador, al usar su llave privada, desencripta la clave simétrica para revelar la conversación y emitir un veredicto.
2.  **Enfoque y Paradigma de Programación:** Definir el paradigma a utilizar, ya que esto influirá directamente en la decisión final de migrar el frontend (Kotlin vs Godot vs Dart/Flutter).
3.  **Estado del Modelo de IA:** Considerar un posible cambio de modelo base y revisar exhaustivamente el estatus actual del corpus.

## 6. Próximos Pasos (Siguientes 2 Semanas)
1.  **Silvia:** Iniciar experimentación de entrenamiento del modelo.
2.  **Eduardo y Moy:** Levantar el *Hola Mundo* de FastAPI y conectarlo a una base de datos local en PostgreSQL.
3.  **López:** Inicializar la estructura base del proyecto Godot y crear los scripts (Pruebas de Concepto) de Criptografía en Python para asegurar la viabilidad matemática.
