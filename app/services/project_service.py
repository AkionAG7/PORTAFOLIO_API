from datetime import datetime
from fastapi import HTTPException, status, UploadFile
from uuid import UUID, uuid4
from typing import List
from sqlalchemy.orm import Session
from app.schemas.project import (
    CreateProjectDTO, UpdateProjectDTO, ProjectResponseDTO, ProjectFiltersDTO
)
from app.schemas.common import MessageResponseDTO
from app.models.Project import Project
from app.services.storage_service import sv_upload_file, sv_delete_file
from app.enums.storage_folder import StorageFolderEnum
from app.core.auth import check_own_resource

#FUNCION PARA CREAR UN UN PROYECTO
def sv_create_project(
    user_id: UUID,
    data: CreateProjectDTO,
    current_user: dict,
    db: Session,
    files: List[UploadFile] | None = None
) -> MessageResponseDTO:
    check_own_resource(user_id, current_user)
    image_urls = []
    if files:
        for file in files:
            url = sv_upload_file(file, StorageFolderEnum.project, user_id)
            image_urls.append(url)
    project = Project(
        id=uuid4(),
        user_id=user_id,
        name=data.name,
        description=data.description,
        repository_link=data.repository_link,
        deploy_link=data.deploy_link,
        image_link=image_urls if image_urls else None,
        create_at=datetime.now()
    )
    db.add(project)
    db.commit()
    return MessageResponseDTO(message="Project created successfully")

#FUNCION PARA TRAER TODOS LOS PROYECTOS DE UN USUARIO
def sv_get_user_projects(user_id: UUID, filters: ProjectFiltersDTO, db: Session) -> dict:
    query = db.query(Project).filter(Project.user_id == user_id)
    if filters.name:
        query = query.filter(Project.name.ilike(f"%{filters.name}%"))
    if filters.status is not None:
        query = query.filter(Project.status == filters.status)
    total = query.count()
    projects = query.offset(filters.skip).limit(filters.limit).all()
    return {
        "data": [ProjectResponseDTO.model_validate(p) for p in projects],
        "metadata": {"total": total, "skip": filters.skip, "limit": filters.limit}
    }

#FUNCION PARA TARER UN PROYECTO DE UN USUARIO
def sv_get_project(project_id: UUID, db: Session) -> ProjectResponseDTO:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponseDTO.model_validate(project)

#FUNCION PARA ACTUALIZAR UN PROYECTO
def sv_update_project(project_id: UUID, data: UpdateProjectDTO, current_user: dict, db: Session) -> MessageResponseDTO:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    check_own_resource(project.user_id, current_user)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    project.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Project updated successfully")

#FUNCION PARA AÑADIR IMAGENES DE UN PROYECTO
def sv_upload_project_images(
    project_id: UUID,
    user_id: UUID,
    current_user: dict,
    files: List[UploadFile],
    db: Session
) -> MessageResponseDTO:
    check_own_resource(user_id, current_user)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if str(project.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This project doesn't belong to this user")
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one file is required")
    new_urls = [sv_upload_file(f, StorageFolderEnum.project, user_id) for f in files]
    current_images = list(project.image_link) if project.image_link else []
    project.image_link = current_images + new_urls
    project.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Project images uploaded successfully")

#FUNCION PARA ELIMINAR LAS IMAGENESS DE UN PROYECTO
def sv_delete_project_image(
    project_id: UUID,
    user_id: UUID,
    image_url: str,
    current_user: dict,
    db: Session
) -> MessageResponseDTO:
    check_own_resource(user_id, current_user)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if str(project.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This project doesn't belong to this user")
    if not project.image_link or image_url not in project.image_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found in this project")
    sv_delete_file(image_url)
    project.image_link = [url for url in project.image_link if url != image_url]
    project.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Project image deleted successfully")

#FUNCION PARA CAMBIAR EL ESTADO DE UN PROYECTO
def sv_update_status_project(project_id: UUID, current_user: dict, db: Session) -> MessageResponseDTO:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    check_own_resource(project.user_id, current_user)
    project.status = not project.status
    project.update_at = datetime.now()
    db.commit()
    return MessageResponseDTO(message="Project status updated successfully")
