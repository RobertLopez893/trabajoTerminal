from sqlalchemy import Column, String, TIMESTAMP, BigInteger, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

BaseAuditoria = declarative_base()

class LogAuditoria(BaseAuditoria):
    __tablename__ = "log_auditoria"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    usuario_id_ref = Column(String(36), nullable=False)
    bloque_id_ref = Column(String(36), nullable=True)
    tipo_evento = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    evidencia_cifrada = Column(Text, nullable=True)
    iv_nonce = Column(String(255), nullable=True)
    tag_autenticacion = Column(String(255), nullable=True)
    hash_integridad = Column(String(255), nullable=False)
    timestamp_evento = Column(TIMESTAMP, server_default=func.now())


class AlertaUsuario(BaseAuditoria):
    __tablename__ = "alerta_usuario"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    usuario_receptor_id_ref = Column(String(36), nullable=False)
    usuario_victima_id_ref = Column(String(36), nullable=False)
    log_id_ref = Column(BigInteger, ForeignKey("log_auditoria.id"), nullable=False)
    estado = Column(String(50), default='ENVIADA')
    enviada_at = Column(TIMESTAMP, server_default=func.now())
    leida_at = Column(TIMESTAMP, nullable=True)
