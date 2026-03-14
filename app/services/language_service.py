from datetime import datetime
from fastapi import HTTPException, status
from uuid import UUID
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, select, insert, update
from app.schemas.language import (
    CreateLanguageDTO, UpdateLanguageDTO, LanguageResponseDTO,
    LanguageFiltersDTO, CreateLanguageUserDTO, UserLanguageReponseDTO,
    UserLanguageFiltersDTO, UpdateLanguageUserDTO
)
from app.models.Language import Language
from app.models.User_language import UserLanguage
from app.models.User import User
from app.core.auth import check_own_resource


# ──────────────────────────────────────────────────────────────
#  LANGUAGE CRUD
# ──────────────────────────────────────────────────────────────

def sv_create_lenguage(data: CreateLanguageDTO, db: Session) -> LanguageResponseDTO:
    normalized_name = data.name.strip().capitalize()
    exist = db.query(Language).filter(func.lower(Language.name) == normalized_name.lower()).first()
    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This language is already registered")

    language = Language(
        id=str(uuid.uuid4()),
        name=normalized_name,
        create_at=datetime.now()
    )
    db.add(language)
    db.commit()
    db.refresh(language)
    return language


def sv_update_language(language_id: UUID, data: UpdateLanguageDTO, db: Session) -> LanguageResponseDTO:
    normalized_name = data.name.strip().capitalize()
    language = db.query(Language).filter(Language.id == language_id).first()

    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")

    language.name = normalized_name
    language.update_at = datetime.now()
    db.commit()
    db.refresh(language)
    return language


def sv_update_status_language(language_id: UUID, db: Session) -> LanguageResponseDTO:
    language = db.query(Language).filter(Language.id == language_id).first()

    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")

    language.status = not language.status
    language.update_at = datetime.now()
    db.commit()
    db.refresh(language)
    return language


def sv_get_all_languages(filters: LanguageFiltersDTO, db: Session) -> dict:
    query = db.query(Language)

    if filters.name:
        query = query.filter(func.lower(Language.name) == filters.name.lower())

    if filters.status is not None:
        query = query.filter(Language.status == filters.status)

    total = query.count()
    languages = query.offset(filters.skip).limit(filters.limit).all()

    return {
        "data": [LanguageResponseDTO.model_validate(l) for l in languages],
        "metadata": {
            "total": total,
            "skip": filters.skip,
            "limit": filters.limit
        }
    }


def sv_get_language(language_id: UUID, db: Session) -> LanguageResponseDTO:
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return language


# ──────────────────────────────────────────────────────────────
#  USER-LANGUAGE RELATIONS
# ──────────────────────────────────────────────────────────────

# Explicit column selection avoids ambiguity when UserLanguage and Language both have a 'status' column
_USER_LANGUAGE_COLS = (
    UserLanguage.c.user_id,
    UserLanguage.c.language_id,
    UserLanguage.c.level,
    UserLanguage.c.status,
    Language.name.label("language_name"),
)


def sv_create_language_user(data: CreateLanguageUserDTO, db: Session, current_user: dict = None) -> UserLanguageReponseDTO:
    if current_user:
        check_own_resource(data.user_id, current_user)
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    language = db.query(Language).filter(Language.id == data.language_id).first()
    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")

    existing = db.execute(
        select(UserLanguage).where(
            UserLanguage.c.user_id == data.user_id,
            UserLanguage.c.language_id == data.language_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user already has this language")

    db.execute(insert(UserLanguage).values(
        user_id=data.user_id,
        language_id=data.language_id,
        level=data.level,
        created_at=datetime.now()
    ))
    db.commit()

    return UserLanguageReponseDTO(
        user_id=data.user_id,
        language_id=data.language_id,
        language_name=language.name,
        level=data.level,
        status=True
    )


def sv_get_all_user_languages(user_id: UUID, filters: UserLanguageFiltersDTO, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    query = (
        select(*_USER_LANGUAGE_COLS)
        .join(Language, UserLanguage.c.language_id == Language.id)
        .where(UserLanguage.c.user_id == user_id)
    )

    if filters.status is not None:
        query = query.where(UserLanguage.c.status == filters.status)

    if filters.level is not None:
        query = query.where(UserLanguage.c.level == filters.level)

    rows = db.execute(query).fetchall()
    total = len(rows)
    paginated = rows[filters.skip: filters.skip + filters.limit]

    return {
        "data": [UserLanguageReponseDTO(
            user_id=row.user_id,
            language_id=row.language_id,
            language_name=row.language_name,
            level=row.level,
            status=row.status
        ) for row in paginated],
        "metadata": {
            "total": total,
            "skip": filters.skip,
            "limit": filters.limit
        }
    }


def sv_get_user_language(user_id: UUID, language_id: UUID, db: Session) -> UserLanguageReponseDTO:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = db.execute(
        select(*_USER_LANGUAGE_COLS)
        .join(Language, UserLanguage.c.language_id == Language.id)
        .where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
    ).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have this language registered")

    return UserLanguageReponseDTO(
        user_id=result.user_id,
        language_id=result.language_id,
        language_name=result.language_name,
        level=result.level,
        status=result.status
    )


def sv_update_status_user_language(user_id: UUID, language_id: UUID, db: Session, current_user: dict = None) -> UserLanguageReponseDTO:
    if current_user:
        check_own_resource(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = db.execute(
        select(*_USER_LANGUAGE_COLS)
        .join(Language, UserLanguage.c.language_id == Language.id)
        .where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
    ).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have this language registered")

    new_status = not result.status
    db.execute(
        update(UserLanguage)
        .where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
        .values(status=new_status, updated_at=datetime.now())
    )
    db.commit()

    return UserLanguageReponseDTO(
        user_id=user_id,
        language_id=language_id,
        language_name=result.language_name,
        level=result.level,
        status=new_status
    )


def sv_update_data_user_language(user_id: UUID, language_id: UUID, data: UpdateLanguageUserDTO, db: Session, current_user: dict = None) -> UserLanguageReponseDTO:
    if current_user:
        check_own_resource(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = db.execute(
        select(*_USER_LANGUAGE_COLS)
        .join(Language, UserLanguage.c.language_id == Language.id)
        .where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
    ).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have this language registered")

    db.execute(
        update(UserLanguage)
        .where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
        .values(level=data.level, updated_at=datetime.now())
    )
    db.commit()

    return UserLanguageReponseDTO(
        user_id=user_id,
        language_id=language_id,
        language_name=result.language_name,
        level=data.level,
        status=result.status
    )
