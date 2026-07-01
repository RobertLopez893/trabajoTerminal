import os
import sys

# Agregar la raíz del proyecto al sys.path para importar correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.aes.aes_gcm import AESGCMCipher
from security.argon2.argon_hasher import ArgonHasher
from security.eddsa.eddsa_signer import EdDSASigner

def run_tests():
    print("=== INICIANDO PRUEBAS DEL MOTOR CRIPTOGRÁFICO ===\n")

    # 1. Prueba AES-GCM
    print("[1] Probando cifrado AES-256-GCM (ALE / Teléfonos)")
    aes = AESGCMCipher()
    mensaje = "Hola soy un infante en el entorno virtual"
    print(f"    Mensaje original: {mensaje}")
    
    enc_data = aes.encrypt(mensaje)
    print(f"    Ciphertext B64: {enc_data['ciphertext_b64']}")
    print(f"    Nonce B64:      {enc_data['nonce_b64']}")
    print(f"    Tag B64:        {enc_data['tag_b64']}")
    
    dec_mensaje = aes.decrypt(enc_data['ciphertext_b64'], enc_data['nonce_b64'], enc_data['tag_b64'])
    assert mensaje == dec_mensaje, "Error en el descifrado AES"
    print("    [OK] Cifrado y descifrado exitoso.")

    # Prueba de alteración de integridad (cambiando el tag)
    print("    Probando rechazo por manipulación de Tag...")
    bad_tag = enc_data['tag_b64'][:-1] + ('A' if enc_data['tag_b64'][-1] != 'A' else 'B')
    try:
        aes.decrypt(enc_data['ciphertext_b64'], enc_data['nonce_b64'], bad_tag)
        print("    [FAIL] ERROR: El sistema aceptó un Tag manipulado.")
    except ValueError:
        print("    [OK] El sistema rechazó correctamente el mensaje manipulado.\n")

    # 2. Prueba Argon2
    print("[2] Probando Hashing Argon2id (Contraseñas Tutores)")
    hasher = ArgonHasher()
    password = "MiSuperPassword123!"
    hash_data = hasher.hash_password(password)
    print(f"    Hash Generado: {hash_data['argon2id_hash']}")
    
    # Verificar contraseña correcta
    is_valid = hasher.verify_password(hash_data['argon2id_hash'], password)
    assert is_valid, "Error verificando la contraseña correcta."
    print("    [OK] Contraseña correcta verificada.")
    
    # Verificar contraseña incorrecta
    is_valid_bad = hasher.verify_password(hash_data['argon2id_hash'], "PasswordEquivocado")
    assert not is_valid_bad, "Error: El sistema aceptó una contraseña incorrecta."
    print("    [OK] Contraseña incorrecta rechazada.\n")

    # 3. Prueba EdDSA (Ed25519)
    print("[3] Probando Firmas Digitales EdDSA Ed25519 (Tokens JWT)")
    signer = EdDSASigner()
    payload_token = '{"user_id": "12345", "role": "tutor", "exp": 1700000000}'
    firma = signer.sign(payload_token)
    print(f"    Firma (B64): {firma}")
    
    is_signed = signer.verify(payload_token, firma)
    assert is_signed, "Error validando la firma auténtica."
    print("    [OK] Firma verificada con éxito.")
    
    is_signed_bad = signer.verify('{"user_id": "12345", "role": "admin"}', firma)
    assert not is_signed_bad, "Error: El sistema aceptó una firma para datos alterados."
    print("    [OK] Firma rechazada al alterar los datos del payload.\n")

    print("=== TODAS LAS PRUEBAS CRIPTOGRÁFICAS PASARON CON ÉXITO ===")

if __name__ == "__main__":
    run_tests()
