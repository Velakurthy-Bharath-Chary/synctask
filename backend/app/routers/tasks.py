from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.ws_manager import ws_manager
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services import task_service

router = APIRouter(tags=["Tasks"])

@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=201)
async def create_task(
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_service.create_task(db, project_id, data, current_user.id)

    # Broadcast to all users in this project instantly
    await ws_manager.broadcast_to_project(project_id, {
        "event": "task_created",
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_to": task.assigned_to,
            "project_id": task.project_id,
        },
        "by": current_user.username,
    })
    return task

@router.get("/projects/{project_id}/tasks", response_model=List[TaskOut])
def get_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return task_service.get_tasks(db, project_id, current_user.id)

@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_service.update_task(db, task_id, data, current_user.id)

    # Broadcast update to all users in this project
    await ws_manager.broadcast_to_project(task.project_id, {
        "event": "task_updated",
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_to": task.assigned_to,
            "project_id": task.project_id,
        },
        "by": current_user.username,
    })
    return task

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_service.get_task(db, task_id, current_user.id)
    project_id = task.project_id
    task_service.delete_task(db, task_id, current_user.id)

    # Broadcast deletion to all users in this project
    await ws_manager.broadcast_to_project(project_id, {
        "event": "task_deleted",
        "task_id": task_id,
        "by": current_user.username,
    })

@router.get("/tasks/{task_id}/logs")
def get_task_logs(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = task_service.get_task_logs(db, task_id, current_user.id)
    return [
        {
            "id": log.id,
            "action": log.action,
            "user_id": log.user_id,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
"""

**What makes this router special:**

Every task operation does TWO things:
```
1. Saves to database  ← normal API
        +
2. Broadcasts to ALL connected users via WebSocket ← real time!"""
"""So when User A updates a task, User B sees it instantly without refreshing!"""