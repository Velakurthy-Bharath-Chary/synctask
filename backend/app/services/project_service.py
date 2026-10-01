import re
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.project import Project, ProjectMember, ProjectRole
from app.schemas.project import ProjectCreate, ProjectUpdate


def _generate_slug(name: str) -> str:
    """Generate URL-friendly slug from project name."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def create_project(db: Session, data: ProjectCreate, owner_id: UUID) -> Project:
    # Generate slug from name if not provided
    slug = data.slug if data.slug else _generate_slug(data.name)
    
    # Check if slug already exists
    existing = db.query(Project).filter(Project.slug == slug).first()
    if existing:
        # Append a number to make it unique
        import uuid
        slug = f"{slug}-{str(uuid.uuid4())[:8]}"
    
    project = Project(
        name=data.name,
        description=data.description,
        slug=slug,
        owner_id=owner_id
    )
    db.add(project)
    db.flush()  # Get project.id before commit

    # Auto-add owner as admin member
    member = ProjectMember(project_id=project.id, user_id=owner_id, role=ProjectRole.admin)
    db.add(member)
    db.commit()
    db.refresh(project)
    return project


def get_user_projects(db: Session, user_id: UUID) -> list:
    """Get all projects where the user is a member."""
    memberships = db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()
    project_ids = [m.project_id for m in memberships]
    return db.query(Project).filter(
        Project.id.in_(project_ids),
        Project.is_archived == False
    ).all()


def get_project(db: Session, project_id: UUID, user_id: UUID) -> Project:
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


def join_project(db: Session, project_id: UUID, user_id: UUID, role: ProjectRole = ProjectRole.member) -> ProjectMember:
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

    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_project(db: Session, project_id: UUID, data: ProjectUpdate, user_id: UUID) -> Project:
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


def delete_project(db: Session, project_id: UUID, user_id: UUID):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the owner can delete this project")

    # Soft delete by archiving
    project.is_archived = True
    db.commit()


def get_all_projects(db: Session) -> list:
    """List all non-archived projects for browsing."""
    return db.query(Project).filter(Project.is_archived == False).all()