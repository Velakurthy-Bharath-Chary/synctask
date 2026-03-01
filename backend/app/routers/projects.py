from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
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
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.get_project(db, project_id, current_user.id)

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_service.update_project(db, project_id, data, current_user.id)

@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_service.delete_project(db, project_id, current_user.id)

@router.post("/join", status_code=200)
def join_project(
    data: JoinProject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_service.join_project(db, data.project_id, current_user.id)
    return {"message": "Joined project successfully"}
"""What this file does:
EndpointJobPOST /projectsCreate a new projectGET /projectsGet my projectsGET /projects/allBrowse all projectsGET /projects/{id}Get one projectPUT /projects/{id}Update a projectDELETE /projects/{id}Delete a projectPOST /projects/joinJoin a project
Notice every route has current_user: User = Depends(get_current_user) — this means every route is protected, only logged in users can access them!

"""