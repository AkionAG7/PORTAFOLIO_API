from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.schemas.common import Pagination

class ContactCreateDTO(BaseModel):
    name: str
    link : str
    image : str | None = None


class ContactResponseDTO(BaseModel):
    id: UUID
    user_id : UUID
    name: str
    link : str
    image: str | None = None
    status: bool

    model_config = {'from_attributes' : True}

#DTO DE LOS FILTROS ESPERADOS EN UN GET
class ContactFilterDTO(Pagination):
    name: str | None = None
    status: bool | None = None