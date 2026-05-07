from pydantic import BaseModel, EmailStr, field_validator
from typing import Annotated
from datetime import datetime
from uuid import UUID
from app.schemas.common import Pagination


#DTO PARA CREAR UN USUARIO
class UserRegisterDTO(BaseModel):
    name: str
    last_name1: str
    last_name2: str | None = None
    email: EmailStr
    phone_number : str | None = None
    password : str
    title: str | None = None

    @field_validator("password")
    @classmethod
    def password_max_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password cannot be more 72 characters")
        return v

#DTO de la respuesta de la API del cliente

class UserResponseDTO(BaseModel):
    id: UUID
    name: str
    last_name1: str
    last_name2: str | None = None
    email: str
    phone_number: str | None = None
    title: str | None = None
    rol: str
    status: bool
    user_image: str | None = None

    model_config = {"from_attributes": True}

#DTO DEL LOGIN
class UserLoginDTO(BaseModel):
    email : EmailStr
    password : str

#DTO DE LA RESPUESTA DEL TOKEN
class TokenResponseDTO(BaseModel):
    access_token : str
    token_type: str = "bearer"

#DTO DE LOS FILTROS ESPERADOS EN UN GET
class UserFilterDTO(Pagination):
    name : str | None = None
    email : str | None = None
    rol : str | None = None
    status : bool | None = None

#DTO PARA ACTUALIZAR INFORMACION BASICA DEL USUARIO
class UserUpdateDTO(BaseModel):
    name: str | None = None
    last_name1: str | None = None
    last_name2: str | None = None
    phone_number : str | None = None
    title: str | None = None
    description: str | None = None

#DTO PARA SOLICITAR RECUPERACION DE CONTRASEÑA
class ForgotPasswordDTO(BaseModel):
    email: EmailStr

#DTO PARA CAMBIAR LA CONTRASEÑA CON TOKEN
class ResetPasswordDTO(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_max_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password cannot be more than 72 characters")
        return v