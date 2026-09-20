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
            models.Minijuego(id="minijuego_1", nombre="Reparando a Moonie", descripcion="Minijuego de trivia y conceptos básicos sobre seguridad en internet."),
            models.Minijuego(id="minijuego_2", nombre="Minijuego 2", descripcion="Pendiente por definir."),
            models.Minijuego(id="minijuego_3", nombre="Minijuego 3", descripcion="Pendiente por definir."),
            models.Minijuego(id="minijuego_4", nombre="Minijuego 4", descripcion="Pendiente por definir.")
        ]
        
        insertados = 0
        for m in minijuegos_seed:
            existe = db.query(models.Minijuego).filter(models.Minijuego.id == m.id).first()
            if not existe:
                db.add(m)
                insertados += 1
                
        if insertados > 0:
            db.commit()
            print(f"    [OK] Se insertaron {insertados} minijuegos en el catálogo.")
        else:
            print("    [OK] El catálogo de MINIJUEGOS ya estaba poblado.")
    except Exception as e:
        print(f"    [!] Error al poblar catálogo: {e}")
    finally:
        db.close()

    print("\n¡Base de datos lista para pruebas!")


if __name__ == "__main__":
    init_db()
