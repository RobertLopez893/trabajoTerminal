from pydantic import BaseModel, constr, Field
from typing import List


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


class ProfileResponse(BaseModel):
    id: str
    nickname: str
    species: str
    color: str
    games_played: int = 0
    highest_score: int = 0


# =========================
# MÓDULO PARENTAL (TUTORES)
# =========================
class ParentRequestCodeResponse(BaseModel):
    message: str
    masked_phone: str
    expires_in_seconds: int = 120
    status: str = "success"


class ParentVerifyCodeRequest(BaseModel):
    codigo: str = Field(..., min_length=6, max_length=6)


class ParentVerifyCodeResponse(BaseModel):
    message: str
    parent_token: str
    expires_in_seconds: int = 900
    status: str = "success"


class ParentAlertItem(BaseModel):
    id: str
    dateLabel: str
    title: str
    summary: str
    is_read: bool = False


class ParentDashboardResponse(BaseModel):
    child_nickname: str
    child_description: str
    alerts: List[ParentAlertItem]


class ParentIncidentMessageItem(BaseModel):
    author: str
    time: str
    text: str
    fromChild: bool


class ParentIncidentDetailResponse(BaseModel):
    id: str
    dateLabel: str
    title: str
    summary: str
    confidence_score: float = 0.0
    fase_detectada: str = ""
    messages: List[ParentIncidentMessageItem]
    guidance: str


# =========================
# MÓDULO DE APELACIONES (ADMIN)
# =========================
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    message: str
    admin_token: str
    expires_in_seconds: int = 86400
    status: str = "success"


class AdminAppealDto(BaseModel):
    id: str
    nickname: str
    date: str
    incident: str
    explanation: str
    evidence: str
    status: str = "PENDING"  # PENDING, IN_REVIEW, APPROVED, REJECTED
    resolution: str = ""
    resolvedAt: int = 0
    resolvedBy: str = ""


class AdminAppealResolveRequest(BaseModel):
    approved: bool
    reason: str = Field(..., min_length=1, max_length=500)


class UserAppealSubmitRequest(BaseModel):
    nickname: str
    justificacion: str = Field(..., min_length=5, max_length=250)



