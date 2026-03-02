from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.schemas.User import UserRegisterDTO, UserLoginDTO, UserResponseDTO, TokenResponseDTO
from app.services.user_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponseDTO, status_code=201)
def register_user(data: UserRegisterDTO, db: Session = Depends(get_db)):
    return register_user(data,db)

@router.post("/login", response_model=TokenResponseDTO)
def login_user(data: UserLoginDTO, db: Session = Depends(get_db)):
    token = login_user(data, db)
    return{"acces_token": token}
