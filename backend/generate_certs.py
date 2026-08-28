import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_self_signed_cert(cert_path="server.crt", key_path="server.key"):
    """
    Genera una llave privada RSA de 2048 bits y un certificado auto-firmado
    válido por 1 año para 'localhost'. Los guarda en formato PEM.
    """
    print(f"Generando llave privada de 2048 bits...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    print("Generando certificado auto-firmado...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CDMX"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Gustavo A. Madero"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ESCOM IPN"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    # El certificado es válido desde hoy hasta dentro de 365 días
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        now
    ).not_valid_after(
        now + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    print(f"Guardando llave privada en: {key_path}")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print(f"Guardando certificado en: {cert_path}")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("¡Certificados generados con éxito!")


if __name__ == "__main__":
    # Obtener el directorio donde se ubica este script para guardar los archivos allí
    base_dir = os.path.dirname(os.path.abspath(__file__))
    c_path = os.path.join(base_dir, "server.crt")
    k_path = os.path.join(base_dir, "server.key")
    generate_self_signed_cert(c_path, k_path)
