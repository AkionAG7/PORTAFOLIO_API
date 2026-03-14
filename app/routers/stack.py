from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.depends_db import get_db
from app.core.auth import get_current_user, require_admin
from app.schemas.stack import (
    CreateStackDTO, UpdateStackDTO, StackResponseDTO, StackFiltersDTO,
    CreateUserStackDTO, UserStackResponseDTO, UserStackFiltersDTO
)
from app.services.stack_service import (
    sv_create_stack, sv_update_stack, sv_update_status_stack,
    sv_get_all_stacks, sv_get_stack,
    sv_create_user_stack, sv_get_all_user_stacks, sv_get_user_stack,
    sv_update_status_user_stack
)

router = APIRouter(prefix="/stack", tags=["Stack"])


# ──────────────────────────────────────────────────────────────
#  STACK CATALOG CRUD 
# ──────────────────────────────────────────────────────────────

#ENDPOINT PARA CREAR UN STACK
@router.post("", status_code=201, response_model=StackResponseDTO)
def create_stack(data: CreateStackDTO, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return sv_create_stack(data, db)


#ENDPOINT PARA TRAER TODOS LOS STACKS
@router.get("", response_model=dict)
def get_all_stacks(filters: StackFiltersDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_all_stacks(filters, db)

#ENDPOINT PARA UN STACK
@router.get("/{stack_id}", response_model=StackResponseDTO)
def get_stack(stack_id: UUID, db: Session = Depends(get_db)):
    return sv_get_stack(stack_id, db)

#ENDPOINT PARA ACTUALIZAR LA INFORMACION PRINCIPAL DE STACK
@router.patch("/{stack_id}", response_model=StackResponseDTO)
def update_stack(stack_id: UUID, data: UpdateStackDTO, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return sv_update_stack(stack_id, data, db)

#ENDPOINT PARA ACTUALIZAR EL ESTADO DE UN STACK
@router.patch("/{stack_id}/status", response_model=StackResponseDTO)
def update_status_stack(stack_id: UUID, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return sv_update_status_stack(stack_id, db)


# ──────────────────────────────────────────────────────────────
#  USER-STACK RELATIONS
# ──────────────────────────────────────────────────────────────

#ENDPOINT PARA AÑADIRLE UN STACK A UN USUARIO
@router.post("/user", status_code=201, response_model=UserStackResponseDTO)
def create_user_stack(data: CreateUserStackDTO, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return sv_create_user_stack(data, current_user, db)

#ENDPOINT PARA TRAER TODOS LOS STACKS DE UN USUARIO
@router.get("/user/{user_id}", response_model=dict)
def get_all_user_stacks(user_id: UUID, filters: UserStackFiltersDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_all_user_stacks(user_id, filters, db)

#ENDPOINT PARA TRAER LA INFORMACOIN DE UN STACK EN ESPECIFICO DE UN USUARIO
@router.get("/user/{user_id}/{stack_id}", response_model=UserStackResponseDTO)
def get_user_stack(user_id: UUID, stack_id: UUID, db: Session = Depends(get_db)):
    return sv_get_user_stack(user_id, stack_id, db)

# FUNCION PARA MODIFICAR EL ESTADO DE UN STACK DE UN USUARIO
@router.patch("/user/{user_id}/{stack_id}/status", response_model=UserStackResponseDTO)
def update_status_user_stack(user_id: UUID, stack_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return sv_update_status_user_stack(user_id, stack_id, current_user, db)
