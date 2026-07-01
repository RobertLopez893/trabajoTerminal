import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class ArgonHasher:
    """
    Motor criptográfico para hashear contraseñas usando Argon2id.
    Este algoritmo es resistente a ataques de fuerza bruta y ataques por GPU.
    """
    
    def __init__(self):
        # Configuramos Argon2id con parámetros recomendados de la OWASP
        self.ph = PasswordHasher(
            time_cost=2,       # Número de iteraciones
            memory_cost=65536, # 64 MB
            parallelism=4,     # Número de hilos
            hash_len=32,       # Longitud del hash resultante
            salt_len=16        # Longitud de la sal
        )

    def hash_password(self, password: str) -> dict:
        """
        Genera un hash Argon2id para una contraseña plana.
        Retorna el hash completo (que ya incluye el salt de forma interna según el estándar)
        y opcionalmente la sal extraída por si la BD requiere guardarla separada.
        """
        hash_str = self.ph.hash(password)
        # El string de Argon2 incluye todo: $argon2id$v=19$m=65536,t=2,p=4$salt$hash
        
        # Extraer el salt en base64 de la cadena si la BD lo pide separado (el 4to parámetro)
        parts = hash_str.split('$')
        salt_b64 = parts[4] if len(parts) > 4 else ""

        return {
            "argon2id_hash": hash_str,
            "salt": salt_b64
        }

    def verify_password(self, hash_str: str, plain_password: str) -> bool:
        """
        Verifica si la contraseña plana coincide con el hash almacenado.
        """
        try:
            return self.ph.verify(hash_str, plain_password)
        except VerifyMismatchError:
            return False
