from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import uuid
from uuid import UUID
from app.core.config import ALGORITHM,SECRET_KEY,TOKEN_EXPIRE
from app.models import User
from app.schemas.User import UserRegisterDTO, UserLoginDTO, UserFilterDTO, UserUpdateDTO, UserResponseDTO
from app.schemas.common import MessageResponseDTO
from app.enums.Rol import RolEnum
from app.services.storage_service import sv_delete_file, sv_upload_file
from app.enums.storage_folder import StorageFolderEnum
from app.core.auth import check_own_resource

# CREACION DEL CONNTEXT PARA EL HASH DEL PASSWORD
pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")

#FUNCION PARA HASHEAR EL PASSWORD
def hash_password(password : str) -> str:
    return pwd_context.hash(password)

#FUNCION PARA VERIFICA EL PASSWORD EN EL LOGIN
def verify_password(pwd: str, pwd_hashed : str ) -> bool:
    return pwd_context.verify(pwd, pwd_hashed)

#FUNCION PARA CREAR EL TOKEN
def create_access_token (data : dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=int(TOKEN_EXPIRE))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)

#FUNCION PARA REGISTRAR UN USUARIO (CREARLO)
def register_user(data: UserRegisterDTO, db : Session) -> MessageResponseDTO:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email already used")
    user = User(
        id = str(uuid.uuid4()),
        name = data.name,
        last_name1= data.last_name1,
        last_name2 = data.last_name2,
        email = data.email,
        phone_number = data.phone_number,
        password = hash_password(data.password),
        create_at = datetime.now()
    )
    db.add(user)
    db.commit()
    return MessageResponseDTO(message="User registered successfully")

#FUNCION PARA INICIAR SESION
def login_user(data: UserLoginDTO, db : Session) -> str:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )
    return create_access_token({"sub": str(user.id), "email" : user.email, "rol" : user.rol})

#FUNCION PARA LISTAR A TODOS LOS USARIOS CON FILTROS OPCIONALES   
def sv_get_all_users(filters: UserFilterDTO, db : Session ) -> dict:
    query = db.query(User)
    if filters.name:
        query = query.filter(User.name.ilike(f"%{filters.name}%"))
    if filters.email:
        query = query.filter(User.email.ilike(f"%{filters.email}%"))
    if filters.rol:
        query = query.filter(User.rol == filters.rol)
    if filters.status:
        query = query.filter(User.status == filters.status)

    total = query.count()
    users = query.offset(filters.skip).limit(filters.limit).all()

    return{
        "data": [UserResponseDTO.model_validate(u) for u in users],
        "metadata":{
            "total": total,
            "skip" : filters.skip,
            "limit": filters.limit
        }
    }

#FUNCION PARA MODIFICAR LA INFORMACION BASICA DEL USUARIO
def sv_update_basic_information(user_id: UUID, data : UserUpdateDTO, db : Session, current_user: dict = None) -> MessageResponseDTO:
    if current_user:
        check_own_resource(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    #ACTUALIZAR LOS CAMPOS QUE SOLO SE MANDARON
    update_data = data.model_dump(exclude_unset=True)#EXCLUDE_UNSET SOLO TOMAS LOS CAMPOS QUESE MADNARON
    for field, value in update_data.items():
        setattr(user, field, value)

    user.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="User information updated successfully")

#FUNCION PARA MODIFICAR EL CORREO
def sv_update_email(user_id: UUID, data: UserLoginDTO, db: Session, current_user: dict = None) -> MessageResponseDTO:
    if current_user:
        check_own_resource(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials")
    user.email = data.email
    user.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Email updated successfully")

#FUNCION PARA ACTUALIZAR EL ROL DE UN USARIO
def sv_update_rol(user_id: UUID, rol: RolEnum, db : Session) -> MessageResponseDTO:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.rol = rol
    user.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="User role updated successfully")

#FUNCION PARA ACTUALIZAR EL ESTADO DE UN USUAIO
def sv_update_status(user_id : UUID, db: Session) -> MessageResponseDTO:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.status = not user.status
    user.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="User status updated successfully")

#FUNCION PARA TRAER LA INFORMACION DE UN USUARIO POR ID
def sv_get_user_by_Id(user_id: UUID, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponseDTO.model_validate(user)

#FUNCION PARA CAMBIAR LA IMAGEN DE UN USARIO
def sv_update_user_image(user_id : UUID, file: UploadFile, db: Session, current_user: dict = None) -> MessageResponseDTO:
    if current_user:
        check_own_resource(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    if not file:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "An image is required")

    if user.user_image:
        sv_delete_file(user.user_image)

    user.user_image = sv_upload_file(file, StorageFolderEnum.user, user_id)
    db.commit()
    return MessageResponseDTO(message="User image updated successfully")
