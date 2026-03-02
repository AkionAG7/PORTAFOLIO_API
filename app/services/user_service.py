from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import uuid
from uuid import UUID
from app.core.config import ALGORITHM,SECRET_KEY,TOKEN_EXPIRE
from app.models import User
from app.schemas.User import UserRegisterDTO, UserLoginDTO, UserFilterDTO, UserUpdateDTO
from app.enums.Rol import RolEnum


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
    expire = datetime.now() + timedelta(hours=TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)

#FUNCION PARA REGISTRAR UN USUARIO (CREARLO)
def register_user(data: UserRegisterDTO, db : Session) -> User:
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
    db.refresh(user)
    return user

#FUNCION PARA INICIAR SESION
def login_user(data: UserLoginDTO, db : Session) -> str:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )
    return create_access_token({"sub": user.id, "email" : user.email, "rol" : user.rol})

#FUNCION PARA LISTAR A TODOS LOS USARIOS CON FILTROS OPCIONALES   
def get_all_users(db : Session, filters: UserFilterDTO ) -> dict:
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
        "data": users,
        "metadata":{
            "total": total,
            "skip" : filters.skip,
            "limit": filters.limit
        }
    }

#FUNCION PARA MODIFICAR LA INFORMACION BASICA DEL USUARIO
def update_basic_information(user_id: UUID, data : UserUpdateDTO, db : Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    #ACTUALIZAR LOS CAMPOS QUE SOLO SE MANDARON
    update_data = data.model_dump(exclude_unset=True)#EXCLUDE_UNSET SOLO TOMAS LOS CAMPOS QUESE MADNARON
    for field, value in update_data.items():
        setattr(user, field, value)

    user.update_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user

#FUNCION PARA MODIFICAR EL CORREO
def update_email(user_id: UUID, data: UserLoginDTO, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(data.password, User.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials")
    user.email = data.email
    user.update_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user

#FUNCION PARA ACTUALIZAR EL ROL DE UN USARIO
def update_rol(user_id: UUID, rol: RolEnum, db : Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.rol = rol
    user.update_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user

#FUNCION PARA ACTUALIZAR EL ESTADO DE UN USUAIO
def update_status(user_id : UUID, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.status = not user.status
    user.update_at = datetime.now()
    db.commit()
    db.refresh(user)
    return user