from fastapi import APIRouter, Depends, File, UploadFile, Form
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.core.auth import get_current_user
from app.services.contact_service import sv_create_contact, sv_get_user_contact_filter, sv_update_contact, sv_get_contact_by_id, sv_update_image_contact, sv_update_status
from app.schemas.contact import ContactCreateDTO, ContactFilterDTO, ContactUpdateDTO, ContactResponseDTO
from app.schemas.common import MessageResponseDTO

router = APIRouter(prefix="/Contact", tags=["Contact"])


#ENDPOINT PARA CREAR UN CONTACTO (propio usuario o admin)
@router.post("/{user_id}", status_code=201, response_model=MessageResponseDTO)
def create_contact(
    user_id: UUID,
    name: str = Form(...),
    link: str = Form(...),
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    data = ContactCreateDTO(name=name, link=link)
    return sv_create_contact(user_id, data, db, file, current_user)


#ENDPOINT PARA OBTENER TODOS LOS CONTACTOS DE UN USUARIO CON FILTRO (publico)
@router.get("/{user_id}/user")
def get_contact_by_filter(user_id: UUID, filter: ContactFilterDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_user_contact_filter(user_id, filter, db)


#ENDPOINT PARA OBTENER UN CONTACTO EN ESPECIFICO (publico)
@router.get("/{contact_id}", response_model=ContactResponseDTO)
def get_contact_by_id(contact_id: UUID, db: Session = Depends(get_db)):
    return sv_get_contact_by_id(contact_id, db)


#ENDPOINT PARA ACTUALIZAR UN CONTACTO (propio usuario o admin)
@router.patch("/{contact_id}", response_model=MessageResponseDTO)
def update_contact(
    contact_id: UUID,
    data: ContactUpdateDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return sv_update_contact(contact_id, data, db, current_user)


#ENDPOINT PARA ACTUALIZAR LA IMAGEN DE UN CONTACTO (propio usuario o admin)
@router.patch("/{contact_id}/{user_id}/image", response_model=MessageResponseDTO)
def update_image_contact(
    contact_id: UUID,
    user_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return sv_update_image_contact(contact_id, user_id, file, db, current_user)


#ENDPOINT PARA ACTUALIZAR EL ESTADO DE UN CONTACTO (propio usuario o admin)
@router.patch("/{contact_id}/status", response_model=MessageResponseDTO)
def update_status(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return sv_update_status(contact_id, db, current_user)
