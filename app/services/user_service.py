from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import uuid
import os
from app.core.config import ALGORITHM,SECRET_KEY,TOKEN_EXPIRE
from app.models import User
from app.schemas.User import UserRegisterDTO, UserLoginDTO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")

def hash_password(password : str) -> str:
    return pwd_context.hash(password)

def verify_password(pwd: str, pwd_hashed : str ) -> bool:
    return pwd_context.verify(pwd, pwd_hashed)

def create_access_token (data : dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)

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

def login_user(data: UserLoginDTO, db : Session) -> str:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )
    return create_access_token({"sub": user.id, "email" : user.email, "rol" : user.rol})
