from pydantic import BaseModel
from uuid import UUID
from app.schemas.common import Pagination

class CreateLanguageDTO:
    name: str

class UpdateLanguageDTO (CreateLanguageDTO):
    pass

class LanguageFiltersDTO(Pagination):
    name: str | None = None
    status: bool | None = None 


class CreateLanguageUserDTO:
    user_id : UUID
    language_id : UUID
    level: str


class LanguageResponseDTO:
    id: UUID
    name: str

class UserLanguageReponseDTO:
    user_id: UUID
    language_id: UUID
    language_name: str
    status: bool

class UserLanguageFiltersDTO(Pagination):
    status : bool | None = None
    level : str | None = None

    model_config = {"from_attributes": True}

class UpdateLanguageUserDTO:
    level : str