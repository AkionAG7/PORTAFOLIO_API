from fastapi import APIRouter, Depends, File, UploadFile, Form
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.services.contact_service import sv_create_contact
from app.schemas.contact import ContactCreateDTO

router = APIRouter(prefix="/Contact", tags=["Contact"])

@router.post("/{user_id}", status_code=201)
def create_contact(user_id : UUID, name: str = Form(...),
    link: str = Form(...),
    db : Session = Depends(get_db),
    file : UploadFile | None = File(default=None)
    ):
    data = ContactCreateDTO(name=name, link=link)
    return sv_create_contact(user_id,data, db, file)
