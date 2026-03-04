from fastapi import APIRouter, Depends, File, UploadFile, Form
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.services.contact_service import sv_create_contact, sv_get_contact_by_filter
from app.schemas.contact import ContactCreateDTO, ContactFilterDTO, ContactUpdateDTO

router = APIRouter(prefix="/Contact", tags=["Contact"])

@router.post("/{user_id}", status_code=201)
def create_contact(user_id : UUID, name: str = Form(...),
    link: str = Form(...),
    db : Session = Depends(get_db),
    file : UploadFile | None = File(default=None)
    ):
    data = ContactCreateDTO(name=name, link=link)
    return sv_create_contact(user_id,data, db, file)


@router.get("/{user_id}")
def get_contact_by_filter(user_id : UUID, filter: ContactFilterDTO, db : Session = Depends(get_db) ):
    return sv_get_contact_by_filter(user_id, filter, db)


@router.patch("/{contact_id}")
def get_contact_by_filter(contact_id : UUID, data: ContactUpdateDTO, db : Session = Depends(get_db)):
    return sv_get_contact_by_filter(contact_id, data, db)

