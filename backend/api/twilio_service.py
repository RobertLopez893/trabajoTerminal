import os
from twilio.rest import Client

def get_twilio_client():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    return Client(account_sid, auth_token)

def send_verification_sms(phone_number: str) -> bool:
    try:
        if not phone_number.startswith('+'):
            phone_number = '+52' + phone_number
            
        client = get_twilio_client()
        service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')
        
        verification = client.verify.v2.services(service_sid).verifications.create(
            to=phone_number,
            channel='sms'
        )
        print(f'Twilio Verify SMS enviado: {verification.status}')
        return True
    except Exception as e:
        print(f'Error con Twilio Verify: {e}')
        return False

def check_verification_code(phone_number: str, code: str) -> bool:
    try:
        if not phone_number.startswith('+'):
            phone_number = '+52' + phone_number
            
        client = get_twilio_client()
        service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')
        
        verification_check = client.verify.v2.services(service_sid).verification_checks.create(
            to=phone_number,
            code=code
        )
        return verification_check.status == 'approved'
    except Exception as e:
        print(f'Error validando código con Twilio Verify: {e}')
        return False


def send_notification_sms(phone_number: str, message: str) -> bool:
    """
    Envía un SMS informativo directo al tutor (usado para alertas y resolución de apelaciones).
    """
    try:
        if not phone_number.startswith('+'):
            phone_number = '+52' + phone_number

        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        if not from_number:
            print(f"[SMS SIMULADO - Notificación a {phone_number}]: {message}")
            return True

        client = get_twilio_client()
        msg = client.messages.create(
            body=message,
            to=phone_number,
            from_=from_number
        )
        print(f"Twilio Notification SMS enviado: {msg.sid}")
        return True
    except Exception as e:
        print(f"Error enviando SMS de notificación con Twilio: {e}")
        return False

