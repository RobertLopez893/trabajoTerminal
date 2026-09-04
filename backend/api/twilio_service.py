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
