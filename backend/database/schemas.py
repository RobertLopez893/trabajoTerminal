from pydantic import BaseModel, constr, Field


class NicknameCheckRequest(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=50)


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
