import requests
import json
import time

BASE_URL = "http://localhost:8000/api/auth"

def run_tests():
    print("=== INICIANDO SIMULACIÓN DEL FRONTEND (REGISTRO ANIMOON) ===\n")
    
    # 1. Verificar Apelativo (Nickname)
    print("[1] Verificando apelativo 'SpaceExplorer99'...")
    nickname_payload = {"nickname": "SpaceExplorer99"}
    res1 = requests.post(f"{BASE_URL}/verificar-apelativo", json=nickname_payload)
    print(f"    Respuesta: {res1.status_code} - {res1.text}")
    assert res1.status_code == 200, "Error verificando apelativo"
    print("    [OK] Apelativo disponible.\n")
    
    time.sleep(1)
    
    # 2. Enviar Código SMS
    print("[2] Solicitando envío de SMS de activación...")
    sms_payload = {
        "nickname": "SpaceExplorer99",
        "telefono": "5512345678"
    }
    res2 = requests.post(f"{BASE_URL}/enviar-codigo-sms", json=sms_payload)
    print(f"    Respuesta: {res2.status_code} - {res2.text}")
    assert res2.status_code == 200, "Error solicitando SMS"
    print("    [OK] Simulación de SMS exitosa.\n")
    
    time.sleep(1)

    # 3. Registro Final (Creación de Cuenta)
    print("[3] Enviando formulario final de registro con Avatar y Contraseña Segura...")
    register_payload = {
        "nickname": "SpaceExplorer99",
        "telefono": "5512345678",
        "codigo_verificacion": "123456",  # Código quemado en el MVP para pruebas
        "password": "PasswordSeguro123!",
        "avatar_especie": "zorro",
        "avatar_color": "naranja"
    }
    res3 = requests.post(f"{BASE_URL}/registro-final", json=register_payload)
    print(f"    Respuesta: {res3.status_code} - {res3.text}")
    assert res3.status_code == 200, f"Error en registro final: {res3.text}"
    print("    [OK] Cuenta creada y guardada en BD exitosamente.\n")

    # 4. Probar duplicidad
    print("[4] Intentando registrar el mismo apelativo de nuevo...")
    res4 = requests.post(f"{BASE_URL}/verificar-apelativo", json=nickname_payload)
    print(f"    Respuesta: {res4.status_code} - {res4.text}")
    assert res4.status_code == 400, "El sistema debió rechazar el apelativo duplicado"
    print("    [OK] Sistema validó duplicidad correctamente.\n")
    
    print("=== TODAS LAS PRUEBAS DE REGISTRO PASARON CON ÉXITO ===")

if __name__ == "__main__":
    try:
        run_tests()
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar a la API. ¿Está corriendo el servidor FastAPI en el puerto 8000?")
