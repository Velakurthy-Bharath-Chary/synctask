from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.ws_manager import ws_manager
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, JoinProject
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.create_project(db, data, current_user.id)


@router.get("", response_model=List[ProjectOut])
def list_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.get_user_projects(db, current_user.id)


@router.get("/all", response_model=List[ProjectOut])
def list_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.get_all_projects(db)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.get_project(db, project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = project_service.update_project(db, project_id, data, current_user.id)
    await ws_manager.broadcast_to_project(str(project_id), {
        "event": "project_updated",
        "project": {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "is_archived": project.is_archived,
        },
        "by": current_user.username,
    })
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = project_service.get_project(db, project_id, current_user.id)
    project_name = project.name
    project_service.delete_project(db, project_id, current_user.id)
    await ws_manager.broadcast_to_project(str(project_id), {
        "event": "project_deleted",
        "project_id": str(project_id),
        "project_name": project_name,
        "by": current_user.username,
    })


@router.post("/join", status_code=200)
async def join_project(
    data: JoinProject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_service.join_project(db, data.project_id, current_user.id, data.role)
    await ws_manager.broadcast_to_project(str(data.project_id), {
        "event": "member_joined",
        "project_id": str(data.project_id),
        "member": {
            "id": str(current_user.id),
            "username": current_user.username,
            "role": data.role.value,
        },
        "by": current_user.username,
    })
    return {"message": "Joined project successfully"}
