from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.ws_manager import ws_manager
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, CommentCreate, CommentOut
from app.services import task_service

router = APIRouter(tags=["Tasks"])


@router.post("/tasks", response_model=TaskOut, status_code=201)
async def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_service.create_task(db, data, current_user.id)

    # Broadcast to all users in this project instantly
    await ws_manager.broadcast_to_project(str(task.project_id), {
        "event": "task_created",
        "task": {
            "id": str(task.id),
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_to": str(task.assigned_to) if task.assigned_to else None,
            "project_id": str(task.project_id),
        },
        "by": current_user.username,
    })
    return task


@router.get("/projects/{project_id}/tasks", response_model=List[TaskOut])
def get_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return task_service.get_tasks(db, project_id, current_user.id)


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return task_service.get_task(db, task_id, current_user.id)


@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_service.update_task(db, task_id, data, current_user.id)

    # Broadcast update to all users in this project
    await ws_manager.broadcast_to_project(str(task.project_id), {
        "event": "task_updated",
        "task": {
            "id": str(task.id),
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_to": str(task.assigned_to) if task.assigned_to else None,
            "project_id": str(task.project_id),
        },
        "by": current_user.username,
    })
    return task


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_service.get_task(db, task_id, current_user.id)
    project_id = task.project_id
    task_service.delete_task(db, task_id, current_user.id)

    # Broadcast deletion to all users in this project
    await ws_manager.broadcast_to_project(str(project_id), {
        "event": "task_deleted",
        "task_id": str(task_id),
        "by": current_user.username,
    })


@router.get("/tasks/{task_id}/logs")
def get_task_logs(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = task_service.get_task_logs(db, task_id, current_user.id)
    return [
        {
            "id": str(log.id),
            "action": log.action.value if hasattr(log.action, 'value') else log.action,
            "user_id": str(log.user_id),
            "old_value": log.old_value,
            "new_value": log.new_value,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.post("/tasks/{task_id}/comments", response_model=CommentOut, status_code=201)
async def create_comment(
    task_id: UUID,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = task_service.create_comment(db, task_id, current_user.id, data.content)
    
    # Get task for project_id
    task = task_service.get_task(db, task_id, current_user.id)
    
    # Broadcast comment to all users in this project
    await ws_manager.broadcast_to_project(str(task.project_id), {
        "event": "comment_added",
        "task_id": str(task_id),
        "comment": {
            "id": str(comment.id),
            "content": comment.content,
            "user_id": str(comment.user_id),
        },
        "by": current_user.username,
    })
    return comment


@router.get("/tasks/{task_id}/comments", response_model=List[CommentOut])
def get_task_comments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return task_service.get_task_comments(db, task_id, current_user.id)