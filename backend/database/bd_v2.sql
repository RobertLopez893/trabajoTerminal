CREATE DATABASE IF NOT EXISTS animoon_operacional CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE animoon_operacional;

CREATE TABLE USUARIO (
    id VARCHAR(36) PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL UNIQUE,
    telefono_cifrado VARCHAR(255) NOT NULL,
    telefono_iv_nonce VARCHAR(255) NOT NULL,
    telefono_tag VARCHAR(255) NOT NULL,
    argon2id_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    ban_expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE VERIFICATION_TOKEN (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id) ON DELETE CASCADE
);

CREATE TABLE AVATAR (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL UNIQUE,
    avatar_config_json JSON NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id) ON DELETE CASCADE
);

CREATE TABLE SESION (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    ecdhe_public_key_ephemeral TEXT NOT NULL,
    shared_secret_b64 VARCHAR(255) NULL,
    session_token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id) ON DELETE CASCADE
);

CREATE TABLE SALA (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE MINIJUEGO (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE USUARIO_MINIJUEGO (
    usuario_id VARCHAR(36) NOT NULL,
    minijuego_id VARCHAR(36) NOT NULL,
    nivel_max_alcanzado INT DEFAULT 1,
    record_puntaje INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, minijuego_id),
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id) ON DELETE CASCADE,
    FOREIGN KEY (minijuego_id) REFERENCES MINIJUEGO(id) ON DELETE CASCADE
);

CREATE TABLE CHAT (
    id VARCHAR(36) PRIMARY KEY,
    usuario_a_id VARCHAR(36) NOT NULL,
    usuario_b_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_a_id) REFERENCES USUARIO(id),
    FOREIGN KEY (usuario_b_id) REFERENCES USUARIO(id)
);

CREATE TABLE MENSAJE (
    id VARCHAR(36) PRIMARY KEY,
    chat_id VARCHAR(36) NOT NULL,
    emisor_usuario_id VARCHAR(36) NOT NULL,
    contenido_cifrado_aes_gcm TEXT NOT NULL,
    iv_nonce VARCHAR(255) NOT NULL,
    aes_gcm_tag VARCHAR(255) NOT NULL,
    orden_global INT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES CHAT(id) ON DELETE CASCADE,
    FOREIGN KEY (emisor_usuario_id) REFERENCES USUARIO(id)
);

CREATE TABLE BLOQUE_ANALISIS (
    id VARCHAR(36) PRIMARY KEY,
    chat_id VARCHAR(36) NOT NULL,
    numero_bloque INT NOT NULL,
    total_mensajes INT DEFAULT 10,
    estado VARCHAR(50) NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    grooming_detectado BOOLEAN DEFAULT FALSE,
    agresor_usuario_id VARCHAR(36) NULL,
    fase_detectada VARCHAR(100) NULL,
    modelo_version VARCHAR(50) NOT NULL,
    analizado_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES CHAT(id),
    FOREIGN KEY (agresor_usuario_id) REFERENCES USUARIO(id)
);

CREATE TABLE APELACION (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    bloque_id VARCHAR(36) NOT NULL,
    justificacion TEXT NOT NULL,
    estado ENUM('PENDIENTE', 'ACEPTADA', 'RECHAZADA') DEFAULT 'PENDIENTE',
    notas_admin_cifradas TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id),
    FOREIGN KEY (bloque_id) REFERENCES BLOQUE_ANALISIS(id)
);

CREATE DATABASE IF NOT EXISTS animoon_auditoria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE animoon_auditoria;

CREATE TABLE LOG_AUDITORIA (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id_ref VARCHAR(36) NOT NULL,
    bloque_id_ref VARCHAR(36) NULL,
    tipo_evento VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    evidencia_cifrada TEXT NULL,
    iv_nonce VARCHAR(255) NULL,
    tag_autenticacion VARCHAR(255) NULL,
    hash_integridad VARCHAR(255) NOT NULL,
    timestamp_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ALERTA_USUARIO (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_receptor_id_ref VARCHAR(36) NOT NULL,
    usuario_victima_id_ref VARCHAR(36) NOT NULL,
    log_id_ref BIGINT UNSIGNED NOT NULL,
    estado ENUM('ENVIADA', 'ENTREGADA', 'LEIDA', 'FALLIDA') DEFAULT 'ENVIADA',
    enviada_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leida_at TIMESTAMP NULL,
    FOREIGN KEY (log_id_ref) REFERENCES LOG_AUDITORIA(id)
);

CREATE USER 'auditoria_svc'@'localhost' IDENTIFIED BY 'P4$$w0rd_776';

GRANT INSERT, SELECT ON animoon_auditoria.* TO 'auditoria_svc'@'localhost';
FLUSH PRIVILEGES;
