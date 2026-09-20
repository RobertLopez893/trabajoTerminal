from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.auth import router as auth_router
from backend.api.chat import router as chat_router
from backend.api.environment import router as env_router
from backend.api.minigames import router as minigames_router

# Crear tablas en Postgres si no existen
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ANIMOON API",
    description="API REST para el proyecto Animoon (Módulo de Registro y Autenticación)",
    version="1.0.0"
)

# Permitir llamadas desde la app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(env_router)
app.include_router(minigames_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API REST de Animoon 🌙"}
