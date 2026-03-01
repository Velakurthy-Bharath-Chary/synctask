from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserOut

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectMemberOut(BaseModel):
    id: int
    user: UserOut
    joined_at: datetime

    class Config:
        from_attributes = True

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    members: List[ProjectMemberOut] = []

    class Config:
        from_attributes = True

class JoinProject(BaseModel):
    project_id: int
"""What this file does:

ProjectCreate — data needed to create a project (just name and description)
ProjectOut — what we send back, includes the full members list
JoinProject — just needs a project_id to join a project"""    