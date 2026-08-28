from sqlalchemy import Column, String, Boolean, TIMESTAMP, Integer, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .db import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(String(36), primary_key=True, index=True)
    nickname = Column(String(50), unique=True, nullable=False, index=True)
    telefono_cifrado = Column(String(255), nullable=False)
    telefono_iv_nonce = Column(String(255), nullable=False)
    telefono_tag = Column(String(255), nullable=False)
    argon2id_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    ban_expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class VerificationToken(Base):
    __tablename__ = "verification_token"

    id = Column(String(36), primary_key=True, index=True)
    usuario_id = Column(String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Avatar(Base):
    __tablename__ = "avatar"

    id = Column(String(36), primary_key=True, index=True)
    usuario_id = Column(String(36), ForeignKey("usuario.id", ondelete="CASCADE"), unique=True, nullable=False)
    avatar_config_json = Column(JSONB, nullable=False)


class Sesion(Base):
    __tablename__ = "sesion"

    id = Column(String(36), primary_key=True, index=True)
    usuario_id = Column(String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    ecdhe_public_key_ephemeral = Column(Text, nullable=False)
    session_token_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    is_active = Column(Boolean, default=True)


class Sala(Base):
    __tablename__ = "sala"

    id = Column(String(36), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)


class Minijuego(Base):
    __tablename__ = "minijuego"

    id = Column(String(36), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)


class UsuarioMinijuego(Base):
    __tablename__ = "usuario_minijuego"

    usuario_id = Column(String(36), ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True)
    minijuego_id = Column(String(36), ForeignKey("minijuego.id", ondelete="CASCADE"), primary_key=True)
    nivel_max_alcanzado = Column(Integer, default=1)
    record_puntaje = Column(Integer, default=0)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Chat(Base):
    __tablename__ = "chat"

    id = Column(String(36), primary_key=True, index=True)
    usuario_a_id = Column(String(36), ForeignKey("usuario.id"), nullable=False)
    usuario_b_id = Column(String(36), ForeignKey("usuario.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Mensaje(Base):
    __tablename__ = "mensaje"

    id = Column(String(36), primary_key=True, index=True)
    chat_id = Column(String(36), ForeignKey("chat.id", ondelete="CASCADE"), nullable=False)
    emisor_usuario_id = Column(String(36), ForeignKey("usuario.id"), nullable=False)
    contenido_cifrado_aes_gcm = Column(Text, nullable=False)
    iv_nonce = Column(String(255), nullable=False)
    aes_gcm_tag = Column(String(255), nullable=False)
    orden_global = Column(Integer, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=func.now())


class BloqueAnalisis(Base):
    __tablename__ = "bloque_analisis"

    id = Column(String(36), primary_key=True, index=True)
    chat_id = Column(String(36), ForeignKey("chat.id"), nullable=False)
    numero_bloque = Column(Integer, nullable=False)
    total_mensajes = Column(Integer, default=10)
    estado = Column(String(50), nullable=False)
    confidence_score = Column(Float, default=0.0)
    grooming_detectado = Column(Boolean, default=False)
    agresor_usuario_id = Column(String(36), ForeignKey("usuario.id"), nullable=True)
    fase_detectada = Column(String(100), nullable=True)
    modelo_version = Column(String(50), nullable=False)
    analizado_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Apelacion(Base):
    __tablename__ = "apelacion"

    id = Column(String(36), primary_key=True, index=True)
    usuario_id = Column(String(36), ForeignKey("usuario.id"), nullable=False)
    bloque_id = Column(String(36), ForeignKey("bloque_analisis.id"), nullable=False)
    justificacion = Column(Text, nullable=False)
    estado = Column(String(50), default='PENDIENTE') 
    notas_admin_cifradas = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
