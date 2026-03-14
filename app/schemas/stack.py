from pydantic import BaseModel
from uuid import UUID
from app.schemas.common import Pagination


class CreateStackDTO(BaseModel):
    name: str


class UpdateStackDTO(BaseModel):
    name: str


class StackFiltersDTO(Pagination):
    name: str | None = None
    status: bool | None = None


class StackResponseDTO(BaseModel):
    id: UUID
    name: str
    status: bool

    model_config = {"from_attributes": True}


class CreateUserStackDTO(BaseModel):
    user_id: UUID
    stack_id: UUID


class UserStackResponseDTO(BaseModel):
    user_id: UUID
    stack_id: UUID
    stack_name: str
    status: bool

    model_config = {"from_attributes": True}


class UserStackFiltersDTO(Pagination):
    status: bool | None = None
