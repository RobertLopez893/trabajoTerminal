import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/auth"

def run_tutor_simulation():
    print("==========================================================")
    print("🌙 SIMULACIÓN DE REGISTRO EN ANIMOON (VISTA DE TUTOR) 🌙")
    print("==========================================================\n")
    
    print("👨‍👦 [PASO 1] Elige el nombre de tu aventurero.")
    apelativo_nino = ""
    while True:
        apelativo_nino = input("    -> Ingresa el apelativo secreto del niño: ").strip()
        print("    -> Validando en la Base de Datos que nadie más lo use...")
        res1 = requests.post(f"{BASE_URL}/verificar-apelativo", json={"nickname": apelativo_nino})
        
        if res1.status_code == 200:
            print("    ✅ ¡El apelativo está disponible! Podemos continuar.\n")
            break
        elif res1.status_code == 400:
            print(f"    ❌ Ops: {res1.json().get('detail')}. Intenta con otro nombre.\n")
        else:
            print(f"    ❌ Error de conexión: {res1.text}\n")
            sys.exit(1)
            
    time.sleep(0.5)

    print("📱 [PASO 2] Verificación parental requerida.")
    print("    -> Por seguridad, necesitamos enlazar la cuenta a un tutor responsable.")
    telefono_tutor = ""
    while True:
        telefono_tutor = input("    -> Ingresa tu número telefónico (exactamente 10 dígitos): ").strip()
        print("    -> Solicitando código de seguridad vía SMS al backend...")
        res2 = requests.post(f"{BASE_URL}/enviar-codigo-sms", json={
            "nickname": apelativo_nino,
            "telefono": telefono_tutor
        })

        if res2.status_code == 200:
            print("    ✅ ¡Bip bip! Se ha simulado el envío de un SMS a tu celular.\n")
            break
        else:
            print(f"    ❌ Error: asegúrate de poner solo 10 números. (Detalle: {res2.text})\n")
            
    time.sleep(0.5)

    print("🛡️ [PASO 3] Creando la cuenta y personalizando el Avatar.")
    
    while True:
        codigo_recibido = input("    -> Ingresa el código de 6 dígitos recibido por SMS (usa 123456): ").strip()
        password_compartida = input("    -> Ingresa una contraseña segura (Mín. 8 caracteres, 1 Mayus, 1 número, 1 símbolo): ").strip()
        
        print("\n    -> ¡Hora de elegir el traje espacial!")
        print("       Opciones válidas: conejo, zorro, gato, perro")
        especie_elegida = input("    -> Especie elegida: ").strip().lower()
        color_elegido = input("    -> Color del traje: ").strip()

        print("\n    -> Enviando todos los datos seguros al servidor de ANIMOON...")

        payload_final = {
            "nickname": apelativo_nino,
            "telefono": telefono_tutor,
            "codigo_verificacion": codigo_recibido,
            "password": password_compartida,
            "avatar_especie": especie_elegida,
            "avatar_color": color_elegido
        }

        res3 = requests.post(f"{BASE_URL}/registro-final", json=payload_final)

        if res3.status_code == 200:
            print("\n    ✅ ¡CUENTA CREADA EXITOSAMENTE!")
            print("       - El número del tutor ha sido cifrado en la BD con AES-256-GCM.")
            print("       - La contraseña está fuertemente protegida con Argon2.")
            print(f"       - ¡{apelativo_nino} está listo para explorar la luna!\n")
            break
        else:
            # Mostramos el error devuelto por FastAPI (puede ser Pydantic o nuestras validaciones personalizadas)
            error_msg = res3.json().get("detail", res3.text)
            print(f"\n    ❌ Backend rechazó los datos: {error_msg}")
            print("    🔄 Por favor, vuelve a intentar este paso.\n")
            
    print("==========================================================")
    print("🚀 FIN DE LA SIMULACIÓN 🚀")
    print("==========================================================")

if __name__ == "__main__":
    try:
        run_tutor_simulation()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar a la API de ANIMOON.")
        print("Asegúrate de haber encendido el backend usando:")
        print("docker-compose up -d")
