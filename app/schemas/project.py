from pydantic import BaseModel
from uuid import UUID
from typing import List
from app.schemas.common import Pagination


class CreateProjectDTO(BaseModel):
    name: str
    description: str
    repository_link: str | None = None
    deploy_link: str | None = None


class UpdateProjectDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    repository_link: str | None = None
    deploy_link: str | None = None


class ProjectFiltersDTO(Pagination):
    name: str | None = None
    status: bool | None = None


class ProjectResponseDTO(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    repository_link: str | None = None
    deploy_link: str | None = None
    image_link: List[str] | None = None
    status: bool

    model_config = {"from_attributes": True}


class DeleteProjectImageDTO(BaseModel):
    image_url: str
