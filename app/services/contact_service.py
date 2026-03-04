from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID, uuid4
import uuid
from app.schemas.contact import ContactCreateDTO, ContactResponseDTO
from app.services.storage_service import sv_upload_file
from app.enums.storage_folder import StorageFolderEnum
from app.models.Contact import Contact

#FUNCION PARA CREAR UN CONTACTO

def sv_create_contact(
        user_id : UUID,
        data: ContactCreateDTO,
        db : Session,
        file: UploadFile | None = None
) -> ContactResponseDTO:
    image_url = None
    if file:
        image_url = sv_upload_file(file, StorageFolderEnum.contact, user_id)

    contact = Contact(
        id = uuid4(),
        user_id = user_id,
        name = data.name,
        link = data.link,
        image = image_url,
        create_at = datetime.now()
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ContactResponseDTO.model_validate(contact)

# FUNCION PARA TRAER TODOS LOS CONTACTOS DE UN USUARIO FILTRADO