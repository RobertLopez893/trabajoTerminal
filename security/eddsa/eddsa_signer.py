import os
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from dotenv import load_dotenv

load_dotenv()

class EdDSASigner:
    """
    Motor criptográfico para firmas digitales usando Twisted Edwards Curves (Ed25519).
    Utilizado para firmar los Tokens de Sesión (JWT) de manera inmutable y ultrarrápida.
    Inmune a fallos de entropía y sesgos de canal lateral (State-of-the-Art).
    """

    def __init__(self, pem_key: str = None):
        # Lee la llave privada desde los parámetros o del .env
        pem_str = pem_key or os.getenv("EDDSA_PRIVATE_KEY_PEM")
        if not pem_str:
            raise ValueError("No se encontró la llave EDDSA_PRIVATE_KEY_PEM")
        
        # Como los saltos de línea están escapados en el .env, los restauramos
        pem_str = pem_str.replace('\\n', '\n')
        
        # Cargar la llave privada
        self.private_key = serialization.load_pem_private_key(
            pem_str.encode('utf-8'),
            password=None
        )
        # Derivar la llave pública para validaciones locales
        self.public_key = self.private_key.public_key()

    def sign(self, data: str) -> str:
        """
        Firma una cadena de texto (ej. el payload de un token).
        Retorna la firma codificada en Base64.
        Nota: Ed25519 no requiere especificar un algoritmo de hash adicional (como SHA256), 
        ya lo hace internamente por diseño.
        """
        signature = self.private_key.sign(data.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')

    def verify(self, data: str, signature_b64: str) -> bool:
        """
        Verifica si la firma Base64 corresponde a los datos utilizando la llave pública.
        """
        try:
            signature = base64.b64decode(signature_b64)
            self.public_key.verify(
                signature,
                data.encode('utf-8')
            )
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False
