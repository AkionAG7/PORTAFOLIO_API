from datetime import datetime
from fastapi import HTTPException, status
from uuid import UUID, uuid4
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, select, insert, update
from app.schemas.language import CreateLanguageDTO, UpdateLanguageDTO, LanguageResponseDTO, LanguageFiltersDTO, CreateLanguageUserDTO, UserLanguageReponseDTO,UserLanguageFiltersDTO,UpdateLanguageUserDTO
from app.models.Language import Language
from app.models.User_language import UserLanguage
from app.models.User import User


#FUNCION PARA CREAR UN LENGUAGE
def sv_create_lenguage(data:CreateLanguageDTO, db : Session ) -> LanguageResponseDTO:
    normalized_name = data.name.strip().capitalize()
    exist = db.query(Language).filter(func.lower(Language.name) == normalized_name.lower()).first()
    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This language already registered")
    language = Language(
        id = str(uuid.uuid4()),
        name = normalized_name,
        create_at = datetime.now()
    )
    db.add(language)
    db.commit()
    db.refresh(language)
    return language


#FUNCION PARA MODIFICAR UN LENGUAGE
def sv_update_language(language_id : UUID, data: UpdateLanguageDTO, db : Session) -> LanguageResponseDTO:
    normalized_name = data.name.strip().capitalize()
    language = db.query(Language).filter(Language.id == language_id).first()

    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Language not found")
    
    language.name = normalized_name
    language.update_at = datetime.now()

    db.commit()
    db.refresh(language)
    return language


#FUNCION PARA CAMBAIR EL ESTADO DE UN LANGUAGE

def sv_update_status_language(language_id: UUID, db : Session) -> LanguageResponseDTO :
    language = db.query(Language).filter(Language.id == language_id).first()

    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Language not found")
    
    language.status = not language.status
    language.update_at = datetime.now()

    db.commit()
    db.refresh(language)


#FUNION PARA TRAER TODOS LOS LENGUAGES CON FILTROS OPCIONALES

def sv_get_all_languages(filters: LanguageFiltersDTO, db: Session) -> dict:
    query = db.query(Language)
    
    if filters.name:
        query = query.filter(func.lower(Language.name) == filters.name.lower())
    
    if filters.status:
        query = query.filter(Language.status == filters.status)
    
    total = query.count()
    languages = query.offset(filters.skip).limit(filters.limit).all()

    return {
        "data": [LanguageResponseDTO.model_validate(l) for l in languages],
        "metadata": {
            "total" : total,
            "skip" : filters.skip,
            "limit": filters.limit
        }
    }

#FUNCION PARA TRAER UN SOLO LENGUAGE EXACTO
def sv_get_language(language_id : UUID, db : Session) -> LanguageResponseDTO:
    language = db.query(Language).filter(Language.id == language_id).first()
    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return language


#FUNCION PARA ASIGNAR UN IDIOMA A UN USUSARIO

def sv_create_language_user(data : CreateLanguageUserDTO, db : Session) -> UserLanguageReponseDTO:
    #Buscar
    existing = db.execute(
        select(UserLanguage).where(UserLanguage.c.user_id == data.user_id,
                                UserLanguage.c.language_id == data.language_id).first()
    )
    if existing:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This user have already this language")
    #Insertar 

    db.execute(insert(UserLanguage).values(
        user_id = data.user_id,
        language_id = data.language_id,
        level = data.level,
        created_at = datetime.now()
    ))
    
    db.commit()

    return UserLanguageReponseDTO(
        user_id = data.user_id,
        language_id = data.language_id,
        language_name = "Un ejemplo",
        level = data.level
    )

#==================================================================================================================#
#                           FUNCIONES DE RELACIONES DE LENGUAGE Y USUARIO
#==================================================================================================================#

#Funcion para traer todos los idiomas de un usuario con paginacion y filtro

def sv_get_all_user_languages(user_id : UUID, filters : UserLanguageFiltersDTO, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    
    #Busqueda total con querry
    query = (select(UserLanguage, Language).join(Language, UserLanguage.c.language_id == Language.id)
            .where(UserLanguage.c.user_id == user_id))
    
    #Filtros
    if filters.status is not None:
        query = query.where(UserLanguage.c.status == filters.status)
    
    if filters.level is not None:
        query = query.where(UserLanguage.c.level == filters.level)
    
    info = db.execute(query).fetchall()

    total = info.count()
    paginated = info[filters.skip + filters.limit]

    return{
        "data":[UserLanguageReponseDTO(
            user_id = row.user_id,
            language_id = row.language_id,
            language_name = row.name,
            status = row.status
        ) for row in paginated],
        "metadata": {
            "total": total,
            "skipe": filters.skip,
            "limit": filters.limit
        }
    }

#FUNCION PARA TRAER UN LENGUAGE DE UN USUARIO ESPECIFICO

def sv_get_user_lenguage(user_id: UUID, language_id : UUID, db : Session) -> UserLanguageReponseDTO:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    
    language = db.query(Language).filter(User.id == user_id).first()
    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Language not found")
    
    query = (select(UserLanguage, Language).join(Language, UserLanguage.c.language_id == Language.id).
            where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id))
    
    result = db.execute(query).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "This user doesnt have this language registered yet")

    
    return UserLanguageReponseDTO(
        user_id = result.user_id,
        language_id = result.language_id,
        language_name = result.name,
        status = result.status
    )

#FUNCION PARA Cambiar el status del idioma que tiene un usuario

def sv_update_status(user_id : UUID, language_id : UUID, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    
    query = (select(UserLanguage).where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id))
    
    result = db.execute(query).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "This user doesnt have this language registered yet")

    db.execute(update(UserLanguage).where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
            .values(status = not result.status))
    db.commit()
    return {"message": "si se actualizo cambiame mas tarde"}

#CAMBIAR LOS DATOS DEL LENGUAGE QUE TIENE EL USUARIO
def sv_update_data_user_language(user_id : UUID, language_id : UUID, data : UpdateLanguageUserDTO, db: Session):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    
    query = (select(UserLanguage).where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id))
    
    result = db.execute(query).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "This user doesnt have this language registered yet")

    db.execute(update(UserLanguage).where(UserLanguage.c.user_id == user_id, UserLanguage.c.language_id == language_id)
            .values(level = data.level))
    db.commit()
    return {"message": "si se actualizo cambiame mas tarde"}