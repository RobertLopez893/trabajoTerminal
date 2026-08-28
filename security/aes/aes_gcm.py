import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()


class AESGCMCipher:
    def __init__(self, hex_key: str = None):
        # Si no se provee llave, lee del .env
        key_str = hex_key or os.getenv("AES_MASTER_KEY")
        if not key_str:
            raise ValueError("No se encontró la llave maestra AES_MASTER_KEY")
        
        # La llave debe ser de 32 bytes
        self.key = bytes.fromhex(key_str)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> dict:
        # Generar un Nonce criptográficamente seguro de 12 bytes
        nonce = os.urandom(12)
        
        # El método encrypt de AESGCM adjunta automáticamente el Tag de 16 bytes al final del ciphertext
        # data = ciphertext + tag
        data = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        
        # Separar el ciphertext del tag
        ciphertext = data[:-16]
        tag = data[-16:]

        return {
            "ciphertext_b64": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce_b64": base64.b64encode(nonce).decode('utf-8'),
            "tag_b64": base64.b64encode(tag).decode('utf-8')
        }

    def decrypt(self, ciphertext_b64: str, nonce_b64: str, tag_b64: str) -> str:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        tag = base64.b64decode(tag_b64)

        # AESGCM.decrypt espera que la data sea ciphertext + tag concatenados
        data = ciphertext + tag
        
        try:
            plaintext = self.aesgcm.decrypt(nonce, data, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Fallo de integridad o llave incorrecta: {e}")
