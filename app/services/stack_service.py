from datetime import datetime
from fastapi import HTTPException, status
from uuid import UUID
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func, select, insert, update, delete
from app.schemas.stack import (
    CreateStackDTO, UpdateStackDTO, StackResponseDTO,
    StackFiltersDTO, CreateUserStackDTO, UserStackResponseDTO,
    UserStackFiltersDTO
)
from app.schemas.common import MessageResponseDTO
from app.models.Stack import Stack
from app.models.User_stack import UserStack
from app.models.User import User
from app.core.auth import check_own_resource


_USER_STACK_COLS = (
    UserStack.c.user_id,
    UserStack.c.stack_id,
    UserStack.c.status,
    Stack.name.label("stack_name"),
)


# ──────────────────────────────────────────────────────────────
#  STACK CATALOG CRUD
# ──────────────────────────────────────────────────────────────

#FUNCION PARA CREAR UN STACK TECNOLOGICO
def sv_create_stack(data: CreateStackDTO, db: Session) -> MessageResponseDTO:
    normalized_name = data.name.strip().capitalize()
    exist = db.query(Stack).filter(func.lower(Stack.name) == normalized_name.lower()).first()
    if exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This stack is already registered")
    stack = Stack(
        id=str(uuid.uuid4()),
        name=normalized_name,
        create_at=datetime.now()
    )
    db.add(stack)
    db.commit()
    return MessageResponseDTO(message="Stack created successfully")

#FUNCION PARA ACTUALIZAR LA INFORMACION DE UN STACK
def sv_update_stack(stack_id: UUID, data: UpdateStackDTO, db: Session) -> MessageResponseDTO:
    normalized_name = data.name.strip().capitalize()
    stack = db.query(Stack).filter(Stack.id == stack_id).first()
    if not stack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
    stack.name = normalized_name
    stack.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Stack updated successfully")

#FUNCION PARA ACTUALIZAR EL STATUS DE UN STACK
def sv_update_status_stack(stack_id: UUID, db: Session) -> MessageResponseDTO:
    stack = db.query(Stack).filter(Stack.id == stack_id).first()
    if not stack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
    stack.status = not stack.status
    stack.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Stack status updated successfully")

#FUNCION PARA OBTENER TODOS LOS STACKS CON FILTROS OPCIONALES
def sv_get_all_stacks(filters: StackFiltersDTO, db: Session) -> dict:
    query = db.query(Stack)
    if filters.name:
        query = query.filter(func.lower(Stack.name).ilike(f"%{filters.name.lower()}%"))
    if filters.status is not None:
        query = query.filter(Stack.status == filters.status)
    total = query.count()
    stacks = query.offset(filters.skip).limit(filters.limit).all()
    return {
        "data": [StackResponseDTO.model_validate(s) for s in stacks],
        "metadata": {"total": total, "skip": filters.skip, "limit": filters.limit}
    }

#FUNCION PARA OBTENER UN STACK SPECIFICO
def sv_get_stack(stack_id: UUID, db: Session) -> StackResponseDTO:
    stack = db.query(Stack).filter(Stack.id == stack_id).first()
    if not stack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
    return stack


# ──────────────────────────────────────────────────────────────
#  USER-STACK RELATIONS
# ──────────────────────────────────────────────────────────────

#FUNCION PARA ASIGNAR UN STACK A UN USER
def sv_create_user_stack(data: CreateUserStackDTO, current_user: dict, db: Session) -> MessageResponseDTO:
    check_own_resource(data.user_id, current_user)
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    stack = db.query(Stack).filter(Stack.id == data.stack_id).first()
    if not stack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
    existing = db.execute(
        select(UserStack).where(
            UserStack.c.user_id == data.user_id,
            UserStack.c.stack_id == data.stack_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user already has this stack")
    db.execute(insert(UserStack).values(user_id=data.user_id, stack_id=data.stack_id))
    db.commit()
    return MessageResponseDTO(message="Stack assigned to user successfully")

#FUNCION PARA OBTENER TODOS LOS STACKS QUE TIENE UN USUARIO CON FILTRO OPCIONAL
def sv_get_all_user_stacks(user_id: UUID, filters: UserStackFiltersDTO, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    query = (
        select(*_USER_STACK_COLS)
        .join(Stack, UserStack.c.stack_id == Stack.id)
        .where(UserStack.c.user_id == user_id)
    )
    if filters.status is not None:
        query = query.where(UserStack.c.status == filters.status)
    rows = db.execute(query).fetchall()
    total = len(rows)
    paginated = rows[filters.skip: filters.skip + filters.limit]
    return {
        "data": [UserStackResponseDTO(
            user_id=row.user_id,
            stack_id=row.stack_id,
            stack_name=row.stack_name,
            status=row.status
        ) for row in paginated],
        "metadata": {"total": total, "skip": filters.skip, "limit": filters.limit}
    }

#FUNCION PARA OBTENER UN STACK DE UN USUARIO
def sv_get_user_stack(user_id: UUID, stack_id: UUID, db: Session) -> UserStackResponseDTO:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = db.execute(
        select(*_USER_STACK_COLS)
        .join(Stack, UserStack.c.stack_id == Stack.id)
        .where(UserStack.c.user_id == user_id, UserStack.c.stack_id == stack_id)
    ).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have this stack registered")
    return UserStackResponseDTO(
        user_id=result.user_id,
        stack_id=result.stack_id,
        stack_name=result.stack_name,
        status=result.status
    )

#FUNCION PARA CAMBIAR EL STATUS DEL STACK DE UN USUARIO
def sv_update_status_user_stack(user_id: UUID, stack_id: UUID, current_user: dict, db: Session) -> MessageResponseDTO:
    check_own_resource(user_id, current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = db.execute(
        select(*_USER_STACK_COLS)
        .join(Stack, UserStack.c.stack_id == Stack.id)
        .where(UserStack.c.user_id == user_id, UserStack.c.stack_id == stack_id)
    ).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user doesn't have this stack registered")
    db.execute(
        update(UserStack)
        .where(UserStack.c.user_id == user_id, UserStack.c.stack_id == stack_id)
        .values(status=not result.status)
    )
    db.commit()
    return MessageResponseDTO(message="User stack status updated successfully")