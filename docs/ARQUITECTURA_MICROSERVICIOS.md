# Arquitectura de Microservicios: Separación de API y Servidor de Chat

Este documento explica a todo el equipo la reciente decisión arquitectónica de separar el módulo principal de la API REST y el servidor de WebSockets en dos microservicios independientes dentro de nuestro entorno Docker.

## 1. El Problema que Teníamos
Anteriormente, el archivo `chat_server.py` funcionaba como un script asíncrono aislado (standalone) utilizando la librería `websockets`. Por otro lado, la API REST operaba con FastAPI mediante `uvicorn`.

Si intentábamos combinar ambas cosas en el mismo puerto bajo la sombrilla de FastAPI:
- Podríamos generar cuellos de botella: el tráfico constante del chat en tiempo real competiría por los mismos recursos que las peticiones REST pesadas (registro, login, persistencia).
- Cumplir de forma estricta con los requerimientos de seguridad para el chat (validación manual de TLS 1.3 y Zero-Trust AES-GCM definidos en los PDFs) hubiera resultado muy complejo dentro del framework de FastAPI sin romper otra lógica.

## 2. La Solución: Microservicios en Docker
Hemos actualizado el archivo `docker-compose.yml` para adoptar una arquitectura orientada a **Microservicios**. Ahora tenemos tres contenedores trabajando en conjunto:

1. **`animoon_postgres` (db):** Contenedor de la base de datos PostgreSQL, expuesto localmente en el puerto `5433`.
2. **`animoon_backend` (api):** Contenedor de FastAPI corriendo en el puerto `8000`. Encargado de las operaciones REST, inicio de sesión y validación de usuarios.
3. **`animoon_chat` (chat_server):** NUEVO contenedor corriendo en el puerto `8765`. Dedicado exclusivamente a mantener conexiones WebSockets en tiempo real, garantizando el cifrado de extremo a extremo.

### ¿Por qué es mejor esta arquitectura?
- **Escalabilidad y Tolerancia a Fallos:** Si el servidor de chat se sobrecarga o falla debido a un error en el socket, la API REST sigue funcionando (y viceversa). Esto significa que los usuarios aún pueden iniciar sesión aunque el chat esté caído.
- **Seguridad Aislada:** El microservicio de chat tiene el control total y exclusivo del certificado SSL para aplicar TLS 1.3, mientras que FastAPI queda liberado de esta carga de procesamiento.
- **Modularidad:** El servidor de chat puede conectarse internamente a la misma base de datos (`db`) usando la red de Docker para realizar la lógica de acumulación de mensajes y conexión al modelo NLP sin interrumpir la API principal.

## 3. ¿Cómo ejecutar el nuevo entorno?
Para el equipo de desarrollo local, nada cambia en la ejecución. Simplemente ejecuten:

```bash
# En Windows (PowerShell)
.\start_docker.ps1
```

O usen directamente docker-compose:
```bash
docker-compose up --build -d
```

### Comprobación:
Podrán ver tres contenedores activos (`docker ps`): uno escuchando en el `5433`, otro en el `8000` y el nuevo de chat en el `8765`. 

Cualquier duda sobre el mapeo de los JSON del frontend al chat, revisar la implementación asíncrona dentro de `backend/chat/chat_server.py`.
