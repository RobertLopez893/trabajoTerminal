from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import schemas, models
from backend.database.db import get_db
from backend.api.deps import get_current_user

router = APIRouter(prefix="/api/minijuegos", tags=["minijuegos"])

@router.post("/guardar-puntaje", response_model=schemas.DefaultResponse)
def save_score(
    req: schemas.MinijuegoScoreRequest, 
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    # Verificar que el minijuego existe en el catálogo
    minijuego = db.query(models.Minijuego).filter(models.Minijuego.id == req.minijuego_id).first()
    if not minijuego:
        raise HTTPException(status_code=404, detail="Minijuego no encontrado.")

    # Buscar si ya hay un registro previo
    registro_existente = db.query(models.UsuarioMinijuego).filter(
        models.UsuarioMinijuego.usuario_id == current_user.id,
        models.UsuarioMinijuego.minijuego_id == req.minijuego_id
    ).first()

    if registro_existente:
        # Actualizar si hay un nuevo récord
        if req.puntaje > registro_existente.record_puntaje:
            registro_existente.record_puntaje = req.puntaje
            
        if req.nivel_max_alcanzado > registro_existente.nivel_max_alcanzado:
            registro_existente.nivel_max_alcanzado = req.nivel_max_alcanzado
            
        db.commit()
        return {"message": "Puntaje actualizado correctamente.", "status": "success"}
    else:
        # Insertar primera vez
        nuevo_registro = models.UsuarioMinijuego(
            usuario_id=current_user.id,
            minijuego_id=req.minijuego_id,
            nivel_max_alcanzado=req.nivel_max_alcanzado,
            record_puntaje=req.puntaje
        )
        db.add(nuevo_registro)
        db.commit()
        return {"message": "Puntaje guardado por primera vez.", "status": "success"}
