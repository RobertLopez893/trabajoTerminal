from pydantic import BaseModel, constr, Field


class NicknameCheckRequest(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=50)


class LoginRequest(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=50)
    password: str = Field(...)
    client_ecdhe_public_key: str = Field(..., description="Llave pública efímera X25519 del cliente en Base64")


class SmsSendRequest(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=50)
    telefono: constr(pattern=r'^\d{10}$')


class FinalRegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=50)
    telefono: constr(pattern=r'^\d{10}$')
    codigo_verificacion: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=8)
    avatar_especie: str = Field(..., description="conejo, zorro, gato, perro")
    avatar_color: str = Field(...)


class DefaultResponse(BaseModel):
    message: str
    status: str = "success"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    message: str
    status: str = "success"
    server_ecdhe_public_key: str = Field(default="", description="Llave pública efímera X25519 del servidor en Base64")

class MinijuegoScoreRequest(BaseModel):
    minijuego_id: str = Field(..., description="ID del minijuego (ej. minijuego_1)")
    puntaje: int = Field(..., description="Puntos obtenidos en la partida")
    nivel_max_alcanzado: int = Field(default=1, description="Nivel máximo superado")
