from fastapi import APIRouter, Depends, File, UploadFile, Form
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.services.contact_service import sv_create_contact, sv_get_user_contact_filter, sv_update_contact, sv_get_contact_by_id, sv_update_image_contact, sv_update_status
from app.schemas.contact import ContactCreateDTO, ContactFilterDTO, ContactUpdateDTO, ContactResponseDTO

router = APIRouter(prefix="/Contact", tags=["Contact"])

#ENDPOINT PARA CREAR UN CONTACTO
@router.post("/{user_id}", status_code=201)
def create_contact(user_id : UUID, name: str = Form(...),
    link: str = Form(...),
    db : Session = Depends(get_db),
    file : UploadFile | None = File(default=None)
    ):
    data = ContactCreateDTO(name=name, link=link)
    return sv_create_contact(user_id,data, db, file)

#ENDPOINT PARA OBTENER TODOS LOS CONTACTOS DE UN USARIO CON FILTRO
@router.get("/{user_id}/user")
def get_contact_by_filter(user_id : UUID, filter: ContactFilterDTO, db : Session = Depends(get_db) ):
    return sv_get_user_contact_filter(user_id, filter, db)

#ENDPOINT PARA OBENTER UN CONTACTO EN ESPECIFICO
@router.get("/{contact_id}", response_model= ContactResponseDTO)
def get_contact_by_filter(contact_id : UUID, db : Session = Depends(get_db) ):
    return sv_get_contact_by_id(contact_id, db)

#ENDPOINT PARA ACTUALIZAR UN CONTACTO 
@router.patch("/{contact_id}", response_model= ContactResponseDTO)
def update_contact(contact_id : UUID, data: ContactUpdateDTO, db : Session = Depends(get_db)):
    return sv_update_contact(contact_id, data, db)

#ENDPOINT PARA ACTUALIZAR LA IMAGEN DE UN CONTACTO
@router.patch("/{contact_id}/{user_id}/image", response_model=ContactResponseDTO)
def update_image_contact(contact_id : UUID, user_id : UUID, file: UploadFile, db: Session = Depends(get_db)):
    return sv_update_image_contact(contact_id, user_id, file, db )

#ENDPOINT PARA ACTUALIZAR EL ESTADO DE UN CONTACTO
@router.patch("/{contac_id}/status")
def update_status(contact_id : UUID, db : Session = Depends(get_db)):
    return sv_update_status(contact_id, db)
