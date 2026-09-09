import boto3
import os
import logging

logger = logging.getLogger(__name__)


def send_sms_via_aws(phone_number: str, code: str) -> bool:
    try:
        if not phone_number.startswith('+'):
            phone_number = '+52' + phone_number

        client = boto3.client(
            'sns',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        message = f'Animoon: Tu codigo de seguridad es {code}. No lo compartas.'

        response = client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        print(f'SMS enviado exitosamente a {phone_number}. ID: {response['MessageId']}')
        return True
    except Exception as e:
        print(f'Error critico enviando SMS por AWS: {e}')
        return False
