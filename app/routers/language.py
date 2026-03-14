from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.depends_db import get_db
from app.core.auth import get_current_user, require_admin
from app.schemas.language import (
    CreateLanguageDTO, UpdateLanguageDTO, LanguageResponseDTO,
    LanguageFiltersDTO, CreateLanguageUserDTO, UserLanguageReponseDTO,
    UserLanguageFiltersDTO, UpdateLanguageUserDTO
)
from app.services.language_service import (
    sv_create_lenguage, sv_update_language, sv_update_status_language,
    sv_get_all_languages, sv_get_language,
    sv_create_language_user, sv_get_all_user_languages, sv_get_user_language,
    sv_update_status_user_language, sv_update_data_user_language
)

router = APIRouter(prefix="/language", tags=["Language"])


# ──────────────────────────────────────────────────────────────
#  LANGUAGE CATALOG CRUD  (write operations require admin)
# ──────────────────────────────────────────────────────────────

@router.post("", status_code=201, response_model=LanguageResponseDTO)
def create_language(data: CreateLanguageDTO, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return sv_create_lenguage(data, db)


@router.get("", response_model=dict)
def get_all_languages(filters: LanguageFiltersDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_all_languages(filters, db)


@router.get("/{language_id}", response_model=LanguageResponseDTO)
def get_language(language_id: UUID, db: Session = Depends(get_db)):
    return sv_get_language(language_id, db)


@router.patch("/{language_id}", response_model=LanguageResponseDTO)
def update_language(language_id: UUID, data: UpdateLanguageDTO, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return sv_update_language(language_id, data, db)


@router.patch("/{language_id}/status", response_model=LanguageResponseDTO)
def update_status_language(language_id: UUID, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return sv_update_status_language(language_id, db)


# ──────────────────────────────────────────────────────────────
#  USER-LANGUAGE RELATIONS  (authenticated, own resource)
# ──────────────────────────────────────────────────────────────

@router.post("/user", status_code=201, response_model=UserLanguageReponseDTO)
def create_language_user(data: CreateLanguageUserDTO, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return sv_create_language_user(data, db, current_user)


@router.get("/user/{user_id}", response_model=dict)
def get_all_user_languages(user_id: UUID, filters: UserLanguageFiltersDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_all_user_languages(user_id, filters, db)


@router.get("/user/{user_id}/{language_id}", response_model=UserLanguageReponseDTO)
def get_user_language(user_id: UUID, language_id: UUID, db: Session = Depends(get_db)):
    return sv_get_user_language(user_id, language_id, db)


@router.patch("/user/{user_id}/{language_id}/status", response_model=UserLanguageReponseDTO)
def update_status_user_language(user_id: UUID, language_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return sv_update_status_user_language(user_id, language_id, db, current_user)


@router.patch("/user/{user_id}/{language_id}", response_model=UserLanguageReponseDTO)
def update_data_user_language(user_id: UUID, language_id: UUID, data: UpdateLanguageUserDTO, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return sv_update_data_user_language(user_id, language_id, data, db, current_user)
