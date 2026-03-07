from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.depends_db import get_db
from app.schemas.User import UserFilterDTO, UserResponseDTO, UserUpdateDTO, UserLoginDTO
from app.services.user_service import sv_get_all_users, sv_update_basic_information, sv_update_email, sv_update_rol, sv_update_status, sv_get_user_by_Id
from uuid import UUID
from app.enums.Rol import RolEnum

router = APIRouter(prefix="/users", tags=["Users"])

#ENDPOINT DEL GET ALL CON FILTROS
@router.get("/")
def get_all_users(filters: UserFilterDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_all_users(filters, db)

#ENDPOINT PARA ACTUALIZAR LOS DATOS BASICOS
@router.patch("/{user_id}", response_model= UserResponseDTO)
def update_basic_information(
    user_id: UUID, data: UserUpdateDTO, db: Session = Depends(get_db)
):
    return sv_update_basic_information(user_id, data, db)

#ENDPOINT PARA ACTUALIZAR EL EMAIL
@router.patch("/{user_id}/email", response_model= UserLoginDTO)
def update_email(
    user_id: UUID, data: UserLoginDTO, db: Session = Depends(get_db)
):
    return sv_update_email(user_id, data, db)

#ENDPOINT PARA ACTUALIZAR EL ROL DEL USUARIO
@router.patch("/{user_id}/rol", response_model=UserResponseDTO)
def update_rol(user_id: UUID, rol : RolEnum, db: Session = Depends(get_db)):
    return sv_update_rol(user_id, rol, db)

#ENDPOINT PARA ACTUALIZAR EL ESTADO DEL USUARIO
@router.patch("/{user_id}/status", response_model= UserResponseDTO)
def update_status(user_id : UUID, db: Session = Depends(get_db)):
    return sv_update_status(user_id, db)

#ENDPOINT PARA TRAER UN USUARIO POR SU ID
@router.get("/{user_id}", response_model= UserResponseDTO)
def get_user_by_Id( user_id : UUID, db: Session = Depends(get_db)):
    return sv_get_user_by_Id(user_id, db)