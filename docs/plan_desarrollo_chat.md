# Plan de Trabajo Diario: Sistema de Sesiones y Chat (Lunes a Sábado)

Este plan desglosa las tareas día a día enfocándose en el desarrollo Full Backend, preparando el terreno para el equipo de Inteligencia Artificial y añadiendo interfaces básicas en Kotlin (Android) para que se pueda probar la conexión completa con el servidor en AWS.

## Sobre AWS y Concurrencia
Dado que el servidor de pruebas ya está en AWS (como menciona el README), usaremos el diccionario en memoria de Python para la concurrencia de WebSockets. Mientras la API corra en una sola instancia/contenedor de AWS, esto es lo más eficiente y no requiere infraestructura extra.

## Sobre el equipo de IA
El alcance backend se limitará a guardar los mensajes encriptados y, al llegar a 20, insertarlos en la tabla `bloque_analisis`. El backend no hará la inferencia, simplemente preparará la bandeja de entrada de datos para que el equipo de NLP la procese.

---

## Cronograma Diario (Lunes a Sábado)

### 🔴 Lunes: Bases de Autenticación Segura y Criptografía Híbrida (Backend)
- **Objetivo:** Preparar la emisión de Tokens y registrar la sesión con Perfect Forward Secrecy.
- **Tareas:**
  - Integrar `EdDSASigner` al ecosistema de dependencias de FastAPI (instalación de `PyJWT`).
  - Escribir funciones utilitarias en `jwt_manager.py` para generar el token JWT usando la llave privada (EdDSA) y generar un hash (SHA-256) del token.
  - Actualizar `schemas.py` para que el `LoginRequest` requiera la llave pública efímera X25519 del cliente (`client_ecdhe_public_key`).
  - Modificar `/api/auth/login` para que:
    - Devuelva el JWT firmado.
    - Inserte el registro en la tabla `SESION` vinculando el `usuario_id`, el hash del JWT y la llave ECDHE efímera, cumpliendo con la política de seguridad estricta.

### 🟠 Martes: Control de Accesos y Gestión de Concurrencia (Backend)
- **Objetivo:** Proteger rutas y preparar el gestor de conexiones.
- **Tareas:**
  - Crear la dependencia `get_current_user` en `backend/api/deps.py` para validar el JWT en los HTTP Headers.
  - Crear endpoint `/api/auth/logout`.
  - Crear la estructura de la clase `ConnectionManager` que mantendrá el diccionario de `usuario_id` -> `WebSocket` activos en la memoria de AWS.

### 🟡 Miércoles: Módulo de WebSockets (Backend)
- **Objetivo:** Migrar el chat alpha a la API principal.
- **Tareas:**
  - Crear el endpoint `/ws/chat` en FastAPI.
  - Autenticar la conexión de WebSocket validando el JWT.
  - Integrar la clase `AESGCMCipher` para desencriptar en memoria (Zero-Trust), leer, y volver a rutear el mensaje a su destinatario a través del `ConnectionManager`.
  - Borrar `chat_server.py` obsoleto.

### 🟢 Jueves: Lógica Social - Invitaciones (Backend)
- **Objetivo:** Flujo estricto de petición de chat (como marca la documentación).
- **Tareas:**
  - Crear tabla en MySQL/Postgres si falta detalle en la tabla `chat`.
  - Endpoint `/api/chat/solicitar`: Un usuario pide hablar con otro.
  - Endpoint `/api/chat/aceptar`: El segundo acepta, se crea un `chat_id` y se habilitan los WebSockets para esa sala.

### 🔵 Viernes: Persistencia y Pase a IA (Backend)
- **Objetivo:** Guardar evidencia y preparar datos para el equipo de NLP.
- **Tareas:**
  - Cada mensaje que cruza por WebSockets debe insertarse en la tabla `mensaje` de la base de datos operacional.
  - Crear lógica que cuente mensajes por `chat_id`. Si `(count % 20) == 0`, se genera un insert en `bloque_analisis` (estado "PENDIENTE") para que el modelo de IA lo consuma.

### 🟣 Sábado: Cliente de Pruebas (Frontend - Kotlin)
- **Objetivo:** Interfaces básicas para interactuar con la API en AWS.
- **Tareas:**
  - Añadir en Android Studio una pantalla simple (cuadros, cajas de texto y botones base sin estilizar).
  - Lógica para hacer el Request de Login y almacenar el JWT en `SharedPreferences` o memoria.
  - Vista básica con un WebSocket Client (`OkHttp` u otra librería) para probar el enrutamiento de mensajes cifrados usando la llave AES en Android y visualizar la respuesta.
