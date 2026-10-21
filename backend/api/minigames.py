import json
import random
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import schemas, models
from backend.database.db import get_db
from backend.api.deps import get_current_user

router = APIRouter(prefix="/api/minijuegos", tags=["minijuegos"])


GAME3_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "game3_conversaciones.json"


class Game3MensajeOut(BaseModel):
    emisor: str
    texto: str


class Game3ConversacionOut(BaseModel):
    id: str
    contacto: str
    riesgo: bool
    mensajes: List[Game3MensajeOut]
    retroalimentacion: str


class Game3PartidaOut(BaseModel):
    conversaciones: List[Game3ConversacionOut]


def _cargar_conversaciones_game3() -> List[dict]:
    try:
        with open(GAME3_DATA_FILE, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="No se pudo leer el banco de conversaciones.")

    conversaciones = datos.get("conversaciones", [])
    if not conversaciones:
        raise HTTPException(status_code=500, detail="El banco de conversaciones está vacío.")
    return conversaciones


def _armar_partida_game3(conversaciones: List[dict], cantidad: int) -> List[dict]:
    con_riesgo = [c for c in conversaciones if c.get("riesgo")]
    seguras = [c for c in conversaciones if not c.get("riesgo")]

    cantidad = min(cantidad, len(conversaciones))
    minimo_riesgo = min(2, len(con_riesgo), cantidad)
    maximo_riesgo = min(3, len(con_riesgo), cantidad)
    if maximo_riesgo < minimo_riesgo:
        maximo_riesgo = minimo_riesgo

    cantidad_riesgo = random.randint(minimo_riesgo, maximo_riesgo)
    cantidad_seguras = cantidad - cantidad_riesgo

    if cantidad_seguras > len(seguras):
        cantidad_seguras = len(seguras)
        cantidad_riesgo = cantidad - cantidad_seguras

    elegidas = random.sample(con_riesgo, cantidad_riesgo) + random.sample(seguras, cantidad_seguras)
    random.shuffle(elegidas)
    return elegidas


@router.get("/minijuego-3/conversaciones", response_model=Game3PartidaOut)
def obtener_conversaciones_game3(
    cantidad: int = Query(5, ge=1, le=10),
    current_user: models.Usuario = Depends(get_current_user)
):
    conversaciones = _cargar_conversaciones_game3()
    return {"conversaciones": _armar_partida_game3(conversaciones, cantidad)}


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
