import sys
import os

# Agregar la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import models, models_auditoria
from backend.database.db import engine, engine_auditoria

def init_db():
    print("=== INICIALIZANDO TABLAS EN LA BASE DE DATOS ===")
    
    # 1. Base Operacional
    print("[1] Creando tablas en animoon_operacional...")
    models.Base.metadata.create_all(bind=engine)
    print("    [OK] Tablas operacionales creadas.")
    
    # Migraciones rápidas para tablas existentes
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE sesion ADD COLUMN IF NOT EXISTS shared_secret_b64 VARCHAR(255);"))
            conn.commit()
    except Exception as e:
        print(f"    [!] Advertencia en migración: {e}")
    
    # 2. Base de Auditoria
    print("[2] Creando tablas en animoon_auditoria...")
    models_auditoria.BaseAuditoria.metadata.create_all(bind=engine_auditoria)
    print("    [OK] Tablas de auditoría creadas.")
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # 3. Seed de Catálogo
    print("[3] Poblando catálogos iniciales...")
    try:
        minijuegos_seed = [
            models.Minijuego(id="minijuego_1", nombre="Repara a Moonie", descripcion="Minijuego de trivia y conceptos básicos sobre seguridad en internet."),
            models.Minijuego(id="minijuego_2", nombre="Reconecta a Moonie", descripcion="Conecta cada mensaje con sus destinos y aprende a compartir información de forma segura."),
            models.Minijuego(id="minijuego_3", nombre="Los oídos de Moonie", descripcion="Minijuego de lectura de chats: identifica cuándo Moonie debe estar tranquilo y cuándo debe ponerse en alerta.")
        ]
        
        insertados = 0
        for m in minijuegos_seed:
            existe = db.query(models.Minijuego).filter(models.Minijuego.id == m.id).first()
            if not existe:
                db.add(m)
                insertados += 1
            else:
                if existe.nombre != m.nombre or existe.descripcion != m.descripcion:
                    existe.nombre = m.nombre
                    existe.descripcion = m.descripcion
                
        db.commit()
        if insertados > 0:
            print(f"    [OK] Se insertaron {insertados} minijuegos en el catálogo.")
        else:
            print("    [OK] Catálogo de MINIJUEGOS verificado y actualizado.")
    except Exception as e:
        print(f"    [!] Error al poblar catálogo: {e}")
    finally:
        db.close()

    print("\n¡Base de datos lista para pruebas!")


if __name__ == "__main__":
    init_db()
