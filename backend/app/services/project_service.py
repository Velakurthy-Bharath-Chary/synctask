from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectCreate, ProjectUpdate

def create_project(db: Session, data: ProjectCreate, owner_id: int) -> Project:
    project = Project(name=data.name, description=data.description, owner_id=owner_id)
    db.add(project)
    db.flush()  # Get project.id before commit

    # Auto-add owner as first member
    member = ProjectMember(project_id=project.id, user_id=owner_id)
    db.add(member)
    db.commit()
    db.refresh(project)
    return project

def get_user_projects(db: Session, user_id: int) -> list:
    """Get all projects where the user is a member."""
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
    project_ids = [m.project_id for m in memberships]
    return db.query(Project).filter(Project.id.in_(project_ids)).all()

def get_project(db: Session, project_id: int, user_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check user is a member
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this project")

    return project

def join_project(db: Session, project_id: int, user_id: int) -> ProjectMember:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if already a member
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member")

    member = ProjectMember(project_id=project_id, user_id=user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def update_project(db: Session, project_id: int, data: ProjectUpdate, user_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the owner can update this project")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project_id: int, user_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this project")

    db.delete(project)
    db.commit()

def get_all_projects(db: Session) -> list:
    """List all projects for browsing."""
    return db.query(Project).all()
"""What project_service.py does
Think of this file as the brain for all project operations. Every function does one specific job:

create_project
User clicks "Create Project"
→ Saves project to DB
→ Automatically adds the creator as first member
get_user_projects
User opens Dashboard
→ Finds all projects where this user is a member
→ Returns that list
get_project
User clicks on a project
→ Checks if project exists
→ Checks if user is actually a member
→ If not a member → blocks with 403 error
→ If member → returns project details
join_project
User clicks "Join Project"
→ Checks project exists
→ Checks user isn't already a member
→ Adds them as a member
update_project
User edits project name/description
→ Checks only the OWNER can do this
→ Updates only the fields that changed
delete_project
User deletes a project
→ Checks only the OWNER can do this
→ Deletes project (cascade deletes all tasks too)
get_all_projects
User clicks "Browse Projects"
→ Returns ALL projects so user can join one

Key concept — db.flush() vs db.commit()
db.flush()  → Saves temporarily, gets the ID, but doesn't finalize
db.commit() → Finalizes everything permanently in the database
We use flush() first to get the project.id so we can add the owner as a member in the same transaction."""