import os
import base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class ECDHEManager:
    """
    Gestor criptográfico para el Intercambio de Claves de Curva Elíptica (ECDHE)
    usando la curva X25519.
    """
    
    @staticmethod
    def generate_keypair():
        """
        Genera un par de llaves efímeras X25519 para la sesión actual.
        Retorna la llave privada (objeto) y la llave pública codificada en Base64.
        """
        private_key = x25519.X25519PrivateKey.generate()
        
        # Extraer los bytes crudos (32 bytes) de la llave pública
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        public_key_b64 = base64.b64encode(public_bytes).decode('utf-8')
        
        return private_key, public_key_b64
        
    @staticmethod
    def compute_shared_secret(server_private_key: x25519.X25519PrivateKey, client_public_key_b64: str) -> str:
        """
        Calcula el secreto compartido (Shared Secret) usando la llave privada del servidor
        y la llave pública del cliente. Aplica HKDF para derivar una llave AES-256 segura.
        Retorna el secreto derivado en Base64.
        """
        try:
            # Decodificar llave pública del cliente
            client_public_bytes = base64.b64decode(client_public_key_b64)
            if len(client_public_bytes) != 32:
                raise ValueError("La llave pública X25519 debe ser de exactamente 32 bytes.")
                
            client_public_key = x25519.X25519PublicKey.from_public_bytes(client_public_bytes)
            
            # Intercambio Diffie-Hellman (Shared Secret de 32 bytes)
            shared_secret = server_private_key.exchange(client_public_key)
            
            # Aplicar HKDF para estirar/derivar una llave fuerte para AES-256 (32 bytes)
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'animoon-session-key',
            ).derive(shared_secret)
            
            return base64.b64encode(derived_key).decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"Fallo al calcular el secreto compartido ECDHE: {str(e)}")
