from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.schemas.User import UserRegisterDTO, UserLoginDTO, UserResponseDTO, TokenResponseDTO, ForgotPasswordDTO, ResetPasswordDTO
from app.schemas.common import MessageResponseDTO
from app.services.user_service import register_user as svregister_user, login_user as svlogin_user, sv_forgot_password, sv_reset_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=MessageResponseDTO, status_code=201)
def register_user(data: UserRegisterDTO, db: Session = Depends(get_db)):
    return svregister_user(data, db)

@router.post("/login", response_model=TokenResponseDTO)
def login_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    data = UserLoginDTO(email=form.username, password=form.password)
    token = svlogin_user(data, db)
    return {"access_token": token}

@router.post("/forgot-password", response_model=MessageResponseDTO)
def forgot_password(data: ForgotPasswordDTO, db: Session = Depends(get_db)):
    return sv_forgot_password(data, db)

@router.post("/reset-password", response_model=MessageResponseDTO)
def reset_password(data: ResetPasswordDTO, db: Session = Depends(get_db)):
    return sv_reset_password(data, db)
