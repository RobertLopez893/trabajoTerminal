import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")

# Operacional
DB_NAME_OPERACIONAL = os.getenv("DB_NAME_OPERACIONAL", "animoon_operacional")
SQLALCHEMY_DATABASE_URL_OP = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_OPERACIONAL}"
engine = create_engine(SQLALCHEMY_DATABASE_URL_OP)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Auditoria
DB_NAME_AUDITORIA = os.getenv("DB_NAME_AUDITORIA", "animoon_auditoria")
SQLALCHEMY_DATABASE_URL_AUDIT = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_AUDITORIA}"
engine_auditoria = create_engine(SQLALCHEMY_DATABASE_URL_AUDIT)
SessionLocalAuditoria = sessionmaker(autocommit=False, autoflush=False, bind=engine_auditoria)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_auditoria():
    db_audit = SessionLocalAuditoria()
    try:
        yield db_audit
    finally:
        db_audit.close()
