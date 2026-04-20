from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID, uuid4
from app.schemas.contact import ContactCreateDTO, ContactResponseDTO, ContactFilterDTO, ContactUpdateDTO
from app.schemas.common import MessageResponseDTO
from app.services.storage_service import sv_upload_file, sv_delete_file
from app.enums.storage_folder import StorageFolderEnum
from app.models.Contact import Contact
from app.core.auth import check_own_resource

#FUNCION PARA CREAR UN CONTACTO

def sv_create_contact(
        user_id : UUID,
        data: ContactCreateDTO,
        db : Session,
        file: UploadFile | None = None,
        current_user: dict = None
) -> MessageResponseDTO:
    if current_user:
        check_own_resource(user_id, current_user)
    image_url = None
    if file and file.filename:
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
    return MessageResponseDTO(message="Contact created successfully")

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
def sv_get_contact_by_id(contact_id : UUID, db: Session) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

#FUNCION PARA MODIFICAR UN CONTACTO
def sv_update_contact(contact_id: UUID, data : ContactUpdateDTO, db : Session, current_user: dict = None) -> MessageResponseDTO:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    if current_user:
        check_own_resource(contact.user_id, current_user)

    # ACTUALIZAR LA INFORMACION
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    contact.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Contact updated successfully")

#Funcion para modificar una imagen de un contacto:
def sv_update_image_contact(contact_id : UUID, user_id : UUID, file: UploadFile, db: Session, current_user: dict = None) -> MessageResponseDTO:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    if current_user:
        check_own_resource(user_id, current_user)

    if not file:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="A new image is requiered")

    if contact.image:
        sv_delete_file(contact.image)
    contact.image = sv_upload_file(file, StorageFolderEnum.contact, user_id)
    contact.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Contact image updated successfully")
    

#Funcion para modificar el estado de un contacto
def sv_update_status(contact_id : UUID, db : Session, current_user: dict = None) -> MessageResponseDTO:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Contact not found")
    if current_user:
        check_own_resource(contact.user_id, current_user)

    contact.status = not contact.status
    contact.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Contact status updated successfully")