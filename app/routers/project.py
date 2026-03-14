from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.core.depends_db import get_db
from app.core.auth import get_current_user
from app.schemas.project import (
    UpdateProjectDTO, ProjectResponseDTO, ProjectFiltersDTO, DeleteProjectImageDTO
)
from app.services.project_service import (
    sv_create_project, sv_get_user_projects, sv_get_project,
    sv_update_project, sv_upload_project_images,
    sv_delete_project_image, sv_update_status_project
)
from app.schemas.project import CreateProjectDTO

router = APIRouter(prefix="/project", tags=["Project"])


# ──────────────────────────────────────────────────────────────
#  PROJECT CRUD
# ──────────────────────────────────────────────────────────────

#ENDPOINT PARA CREAR UN PROYECTO
@router.post("/{user_id}", status_code=201, response_model=ProjectResponseDTO)
def create_project(
    user_id: UUID,
    name: str = Form(...),
    description: str = Form(...),
    repository_link: str | None = Form(default=None),
    deploy_link: str | None = Form(default=None),
    files: List[UploadFile] | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    data = CreateProjectDTO(
        name=name,
        description=description,
        repository_link=repository_link,
        deploy_link=deploy_link
    )
    return sv_create_project(user_id, data, current_user, db, files)


#ENDPOINT PARA TRAER TODOS LOS PROYECTOS DE UN USUARIO
@router.get("/{user_id}/user", response_model=dict)
def get_user_projects(user_id: UUID, filters: ProjectFiltersDTO = Depends(), db: Session = Depends(get_db)):
    return sv_get_user_projects(user_id, filters, db)

#ENDPOINT PARA TRAER TODA LA INFORMACOIN DE UN PROYECTO DE UN USUARIO
@router.get("/{project_id}", response_model=ProjectResponseDTO)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    return sv_get_project(project_id, db)

#ENDPOINT PARA ACTUALIZAR LA INFORMACIÖN BASICA DE UN PROYECTO 
@router.patch("/{project_id}", response_model=ProjectResponseDTO)
def update_project(
    project_id: UUID,
    data: UpdateProjectDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return sv_update_project(project_id, data, current_user, db)

#ENDPOINT PARA CAMBIAR EL ESTADO DE UN PROYECTO
@router.patch("/{project_id}/status", response_model=ProjectResponseDTO)
def update_status_project(project_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return sv_update_status_project(project_id, current_user, db)


# ──────────────────────────────────────────────────────────────
#  PROJECT IMAGES 
# ──────────────────────────────────────────────────────────────

#ENDPOINT PARA AGREGAR IMAGENES AL PROYECTO
@router.post("/{project_id}/{user_id}/images", response_model=ProjectResponseDTO)
def upload_project_images(
    project_id: UUID,
    user_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return sv_upload_project_images(project_id, user_id, current_user, files, db)

#ENDPOINT PARA ELIMINAR IMAGENES DEL PROYECTO
@router.delete("/{project_id}/{user_id}/images", response_model=ProjectResponseDTO)
def delete_project_image(
    project_id: UUID,
    user_id: UUID,
    data: DeleteProjectImageDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return sv_delete_project_image(project_id, user_id, data.image_url, current_user, db)
