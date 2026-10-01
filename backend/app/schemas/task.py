from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum
from uuid import UUID


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskCreate(BaseModel):
    project_id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None
    assigned_to: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    is_archived: Optional[bool] = None


class TaskOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    deadline: Optional[datetime]
    project_id: UUID
    assigned_to: Optional[UUID]
    created_by: UUID
    is_archived: bool = False
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: UUID
    task_id: UUID
    user_id: UUID
    content: str
    is_edited: bool = False
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ActivityLogOut(BaseModel):
    id: UUID
    task_id: UUID
    user_id: UUID
    action: str
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True