import os
import secrets
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Generar llave AES de 32 bytes (256 bits)
aes_key = secrets.token_hex(32)

# Generar llave privada Ed25519 (Twisted Edwards Curve)
private_key = ed25519.Ed25519PrivateKey.generate()
pem_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
pem_str = pem_bytes.decode('utf-8').replace('\n', '\\n') # Reemplazamos saltos para que quede en una sola linea en el .env

# Escribir el .env
with open('.env', 'w') as f:
    f.write(f'AES_MASTER_KEY={aes_key}\n')
    f.write(f'EDDSA_PRIVATE_KEY_PEM="{pem_str}"\n')

print("¡Archivo .env generado con éxito con llaves Ed25519!")
