import sys
import os
from backend.database import models, models_auditoria
from backend.database.db import engine, engine_auditoria

# Agregar la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def init_db():
    print("=== INICIALIZANDO TABLAS EN LA BASE DE DATOS ===")
    
    # 1. Base Operacional
    print("[1] Creando tablas en animoon_operacional...")
    models.Base.metadata.create_all(bind=engine)
    print("    [OK] Tablas operacionales creadas.")
    
    # 2. Base de Auditoria
    print("[2] Creando tablas en animoon_auditoria...")
    models_auditoria.BaseAuditoria.metadata.create_all(bind=engine_auditoria)
    print("    [OK] Tablas de auditoría creadas.")
    
    print("\n¡Base de datos lista para pruebas!")


if __name__ == "__main__":
    init_db()
