from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID, uuid4
import uuid
from app.schemas.contact import ContactCreateDTO, ContactResponseDTO, ContactFilterDTO, ContactUpdateDTO
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

# FUNCION PARA TRAER TODOS LOS CONTACTOS DE UN USUARIO CON FILTRADO
def sv_get_user_contact_filter(user_id : UUID, filter: ContactFilterDTO, db: Session) -> dict:
    query = db.query(Contact).filter(Contact.user_id == user_id)
    if filter.name:
        query = query.filter(Contact.name == filter.name)
    if filter.status:
        query = query.filter(Contact.status == filter.status)
    
    total = query.count()
    contacts = query.offset(filter.skip).limit(filter.limit).all()

    return{
        "data": [ContactResponseDTO.model_validate(c) for c in contacts],
        "metadata":{
            "total": total,
            "skip" : filter.skip,
            "limit": filter.limit
        }
    }

# FUNCION PARA TRAER UN CONTACTO EN ESPECIFICO
def sv_get_contact_by_id(contact_id : UUID, filter: ContactFilterDTO, db: Session) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

#FUNCION PARA MODIFICAR UN CONTACTO
def sv_update_contact(contact_id: UUID, data : ContactUpdateDTO, db : Session) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    # ACTUALIZAR LA INFORMACION
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    contact.update_at = datetime.now()
    db.commit()
    db.refresh(contact)
    return contact

