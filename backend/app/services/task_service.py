from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.task import Task, ActivityLog, Comment, ActivityAction
from app.models.project import ProjectMember
from app.schemas.task import TaskCreate, TaskUpdate


def _verify_membership(db: Session, project_id: UUID, user_id: UUID):
    """Check if user is a member of the project."""
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this project")


def _log_activity(db: Session, task_id: UUID, user_id: UUID, action: ActivityAction, 
                  old_value: dict = None, new_value: dict = None, metadata: dict = None):
    """Record every change made to a task."""
    log = ActivityLog(
        task_id=task_id,
        user_id=user_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        metadata=metadata
    )
    db.add(log)


def create_task(db: Session, data: TaskCreate, user_id: UUID) -> Task:
    _verify_membership(db, data.project_id, user_id)

    task_data = data.model_dump()
    task = Task(
        **task_data,
        created_by=user_id,
    )
    db.add(task)
    db.flush()  # Get task.id

    # Log the creation
    _log_activity(
        db, task.id, user_id, ActivityAction.TASK_CREATED,
        new_value={"title": task.title, "status": task.status.value}
    )
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, project_id: UUID, user_id: UUID) -> list:
    _verify_membership(db, project_id, user_id)
    return db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_archived == False
    ).all()


def get_task(db: Session, task_id: UUID, user_id: UUID) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)
    return task


def update_task(db: Session, task_id: UUID, data: TaskUpdate, user_id: UUID) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)

    # Track what changed
    update_data = data.model_dump(exclude_unset=True)
    old_values = {}
    new_values = {}

    for field, value in update_data.items():
        old_value = getattr(task, field)
        if hasattr(old_value, 'value'):  # Handle Enum
            old_value = old_value.value
        if hasattr(value, 'value'):
            value_str = value.value
        else:
            value_str = str(value) if value is not None else None
        
        if old_value != value:
            old_values[field] = str(old_value) if old_value is not None else None
            new_values[field] = value_str
            setattr(task, field, value)

    # Log the changes
    if old_values:
        action = ActivityAction.TASK_UPDATED
        if 'status' in new_values:
            action = ActivityAction.STATUS_CHANGED
        elif 'priority' in new_values:
            action = ActivityAction.PRIORITY_CHANGED
        elif 'assigned_to' in new_values:
            action = ActivityAction.TASK_ASSIGNED
        elif 'deadline' in new_values:
            action = ActivityAction.DEADLINE_SET
        
        _log_activity(db, task.id, user_id, action, old_value=old_values, new_value=new_values)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: UUID, user_id: UUID):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)

    # Soft delete
    task.is_archived = True
    db.commit()


def get_task_logs(db: Session, task_id: UUID, user_id: UUID) -> list:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)
    return db.query(ActivityLog).filter(ActivityLog.task_id == task_id)\
        .order_by(ActivityLog.created_at.desc()).all()


def create_comment(db: Session, task_id: UUID, user_id: UUID, content: str) -> Comment:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)

    comment = Comment(task_id=task_id, user_id=user_id, content=content)
    db.add(comment)
    
    # Log the comment
    _log_activity(
        db, task_id, user_id, ActivityAction.COMMENT_ADDED,
        new_value={"content": content[:100]}  # Truncate for log
    )
    
    db.commit()
    db.refresh(comment)
    return comment


def get_task_comments(db: Session, task_id: UUID, user_id: UUID) -> list:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)
    return db.query(Comment).filter(Comment.task_id == task_id)\
        .order_by(Comment.created_at.desc()).all()