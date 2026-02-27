from pydantic import BaseModel, EmailStr
from typing import Annotated
from datetime import datetime
from uuid import UUID


#DTO PARA CREAR UN USUARIO
class UserRegisterDTO(BaseModel):
    name: str
    last_name1: str
    last_name2: str | None = None
    email: EmailStr
    phone_number = str | None = None
    password = str
    title: str
    create_at : datetime | None = datetime.now()

#DTO de la respuesta de la API del cliente

class UserResponseDTO(BaseModel):
    id: UUID
    name: str
    last_name1: str
    last_name2: str | None = None
    email: str
    title: str
    rol: str

    model_config = {"from_attributes": True}


class UserLoginDTO(BaseModel):
    email : EmailStr
    password : str

class TokenResponseDTO(BaseModel):
    access_token : str
    token_type: str = "bearer"