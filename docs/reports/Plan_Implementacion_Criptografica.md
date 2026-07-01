# Motor Criptográfico ANIMOON - Plan de Implementación Actualizado

Este documento detalla la arquitectura definitiva, los acuerdos tomados y el plan de acción para construir el núcleo de seguridad de ANIMOON de forma local.

## Acuerdos Arquitectónicos

1. **Entorno Local y Secretos:** Todo el desarrollo inicial se realizará en `localhost`. Las llaves maestras, contraseñas y parámetros de criptografía se almacenarán en un archivo `.env` (que estará en `.gitignore`), sentando las bases para una futura contenerización (Docker).
2. **Cifrado Doble (TLS + ALE):** Se implementará *Application-Layer Encryption (ALE)* utilizando AES-256-GCM entre el cliente (Godot) y el backend (FastAPI). Esto crea un cifrado robusto que funciona en paralelo y por debajo de la capa TLS 1.3 de la red, asegurando la privacidad incluso ante fallas de infraestructura o proxies inversos.
3. **Firmas ECDSA:** Se utilizará criptografía de curva elíptica asimétrica para firmar los *Tokens de Sesión (JWT)* emitidos tras la validación de los tutores, descartando la firma directa de códigos numéricos de SMS.

## Cambios Propuestos

Implementaremos el motor criptográfico inicial en las carpetas raíz correspondientes en Python.

### Entorno y Configuración
- `requirements.txt`: Dependencias `cryptography`, `argon2-cffi`, `python-dotenv`.
- `.env.example`: Plantilla base para las variables de entorno maestras.

### Motor de Criptografía Backend (Python)
- `security/aes/aes_gcm.py`: Clase utilitaria en Python para cifrar y descifrar usando AES-256-GCM leyendo las variables del `.env`. Retornará el texto cifrado, el nonce y el Tag de Autenticación.
- `security/argon2/argon_hasher.py`: Implementación de Argon2id para el hasheo seguro de contraseñas de los tutores, incluyendo verificación contra texto plano.
- `security/ecdsa/ecdsa_signer.py`: Generación de pares de llaves de curva elíptica (SECP256R1) para firmar y validar Tokens de Sesión.

## Plan de Verificación

1. **Scripts Unitarios Locales:** Se creará un script principal de prueba (`security/test_crypto.py`) que:
   - Levante las variables del `.env`.
   - Cifre un mensaje simulado (AES-GCM).
   - Hashee y verifique una contraseña (Argon2).
   - Firme y verifique un token (ECDSA).
   - Compruebe que alterar un solo bit del mensaje o del Tag de Autenticación genere un rechazo criptográfico inmediato.
