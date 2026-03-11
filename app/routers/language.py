from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID, uuid4
from app.core.depends_db import get_db
from app.services.language_service import sv_create_lenguage, sv_update_language, sv_update_status_language
from app.schemas.language import CreateLanguageDTO, UpdateLanguageDTO


router = APIRouter(prefix="/language", tags=["Language"])

#ENDPOINT PARA CREAR UN IDIOMA
@router.post("/language", status_code=201)
def create_lenguage(data: CreateLanguageDTO, db : Session = Depends(get_db)):
    return sv_create_lenguage(data, db)

#ENDPOINT PARA ACTUALIZAR UN IDIOMA
@router.patch("{language_id}")
def update_language(language_id : UUID, data: UpdateLanguageDTO, db: Session = Depends(get_db)):
    return sv_update_language(language_id, data, db)

#ENDPOINT PARA CAMBIAR EL ESTADO DE UN LENGUAGE
@router.patch("{language_id}/status")
def update_status_language(language_id : UUID, db : Session = Depends(get_db)):
    return sv_update_status_language(language_id, db)