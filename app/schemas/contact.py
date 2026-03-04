from pydantic import BaseModel
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

#DTO DE LOS FILTROS ESPERADOS PARA EL GET DE CONTACTOS
class ContactFilterDTO(Pagination):
    name: str | None = None
    status: bool | None = None

#DTO PARA MODIFICAR LA INFORMACION DE UN CONTACTO

class ContactUpdateDTO(BaseModel):
    name = str | None = None
    link = str | None = None
    image = str | None = None
    status= bool | None = None