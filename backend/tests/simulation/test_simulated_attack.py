"""
Prueba Automatizada de Ataque Simulado de Grooming (Fase 5 - Animoon)
Ejecuta la simulación de ataque y verifica todas las capas de defensa activas:
1. Conexión WebSocket segura TLS 1.3
2. Transmisión cifrada AES-256-GCM
3. Acumulación y corte de bloque en Redis / PostgreSQL
4. Inferencia en caliente del Worker BETO
5. Suspensión de cuenta del agresor en PostgreSQL
6. Registro inmutable en animoon_auditoria (evidencia cifrada + hash SHA-256)
7. Alerta SMS para el tutor
8. Pub/Sub en tiempo real: expulsión de agresor y SAFE_EXIT para la víctima
"""

import sys
import asyncio
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.dirname(CURRENT_DIR)
BACKEND_DIR = os.path.dirname(TESTS_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

sys.path.append(PROJECT_ROOT)

from backend.tests.simulation.simulator import ejecutar_simulacion

async def main():
    print("\n" + "█" * 80)
    print("   PRUEBA INTEGRAL DE ATAQUE SIMULADO DE GROOMING (FASE 5)")
    print("█" * 80 + "\n")

    resultado = await ejecutar_simulacion(nombre_escenario="grooming")
    
    if resultado["exito"]:
        print(">>> RESULTADO FINAL: PROTOCOLO DE DEFENSA ACTIVA FUNCIONÓ AL 100% <<<")
        sys.exit(0)
    else:
        print(">>> RESULTADO FINAL: HUBO FALLOS EN LA CONTENCIÓN DEL ATAQUE <<<")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
