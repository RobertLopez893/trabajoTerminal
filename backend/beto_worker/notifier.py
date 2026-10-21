"""
=============================================================================
NOTIFICADOR TWILIO SMS (MICROSERVICIO BETO_WORKER)
=============================================================================
Este módulo gestiona el envío de alertas SMS al tutor/padre de familia
en caso de detección preventiva de Grooming.
=============================================================================
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("TwilioNotifier")
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Intentar importar la librería de twilio de manera opcional
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


def enviar_alerta_sms(telefono_destino: str, motivo: str = "Patrones de riesgo detectados") -> bool:
    """
    Envía un SMS preventivo al teléfono del tutor o contacto de emergencia.
    Retorna True si fue enviado exitosamente o simulado, False en caso de error.
    """
    if not telefono_destino:
        logger.warning("[SMS] No se proporcionó un número de teléfono destino.")
        return False

    mensaje_cuerpo = (
        f"[ALERTA ANIMOON] Se ha activado el protocolo de seguridad preventiva en la cuenta "
        f"de su menor protegido debido a: {motivo}. El chat sospechoso fue suspendido inmediatamente."
    )

    if not TWILIO_AVAILABLE:
        logger.warning(f"[SMS MOCK] Librería 'twilio' no instalada. Simulación de SMS hacia {telefono_destino}: {mensaje_cuerpo}")
        return True

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        logger.warning(f"[SMS MOCK] Credenciales de Twilio incompletas en .env. Simulación de SMS hacia {telefono_destino}: {mensaje_cuerpo}")
        return True

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=mensaje_cuerpo,
            from_=TWILIO_PHONE_NUMBER,
            to=telefono_destino
        )
        logger.info(f"[SMS] Alerta Twilio enviada con éxito. SID: {message.sid} a {telefono_destino}")
        return True
    except Exception as e:
        logger.error(f"[SMS ERROR] No se pudo enviar SMS vía Twilio a {telefono_destino}: {e}")
        return False
