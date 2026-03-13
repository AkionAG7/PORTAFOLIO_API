from pydantic import BaseModel
from uuid import UUID
from app.schemas.common import Pagination


class CreateLanguageDTO(BaseModel):
    name: str


class UpdateLanguageDTO(BaseModel):
    name: str


class LanguageFiltersDTO(Pagination):
    name: str | None = None
    status: bool | None = None


class LanguageResponseDTO(BaseModel):
    id: UUID
    name: str
    status: bool

    model_config = {"from_attributes": True}


class CreateLanguageUserDTO(BaseModel):
    user_id: UUID
    language_id: UUID
    level: str


class UserLanguageReponseDTO(BaseModel):
    user_id: UUID
    language_id: UUID
    language_name: str
    level: str | None = None
    status: bool

    model_config = {"from_attributes": True}


class UserLanguageFiltersDTO(Pagination):
    status: bool | None = None
    level: str | None = None


class UpdateLanguageUserDTO(BaseModel):
    level: str
