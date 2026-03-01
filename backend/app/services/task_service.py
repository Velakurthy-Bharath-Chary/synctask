from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.task import Task, ActivityLog
from app.models.project import ProjectMember
from app.schemas.task import TaskCreate, TaskUpdate

def _verify_membership(db: Session, project_id: int, user_id: int):
    """Check if user is a member of the project."""
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this project")

def _log_activity(db: Session, task_id: int, user_id: int, action: str):
    """Record every change made to a task."""
    log = ActivityLog(task_id=task_id, user_id=user_id, action=action)
    db.add(log)

def create_task(db: Session, project_id: int, data: TaskCreate, user_id: int) -> Task:
    _verify_membership(db, project_id, user_id)

    task = Task(
        **data.model_dump(),
        project_id=project_id,
        created_by=user_id,
    )
    db.add(task)
    db.flush()  # Get task.id

    # Log the creation
    _log_activity(db, task.id, user_id, f"Task created: '{task.title}'")
    db.commit()
    db.refresh(task)
    return task

def get_tasks(db: Session, project_id: int, user_id: int) -> list:
    _verify_membership(db, project_id, user_id)
    return db.query(Task).filter(Task.project_id == project_id).all()

def get_task(db: Session, task_id: int, user_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)
    return task

def update_task(db: Session, task_id: int, data: TaskUpdate, user_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)

    # Track what changed
    changes = []
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        old_value = getattr(task, field)
        if old_value != value:
            changes.append(f"{field}: '{old_value}' → '{value}'")
            setattr(task, field, value)

    # Log the changes
    if changes:
        _log_activity(db, task.id, user_id, "; ".join(changes))

    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int, user_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)

    db.delete(task)
    db.commit()

def get_task_logs(db: Session, task_id: int, user_id: int) -> list:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _verify_membership(db, task.project_id, user_id)
    return db.query(ActivityLog).filter(ActivityLog.task_id == task_id)\
        .order_by(ActivityLog.created_at.desc()).all()
"""What this file does:
FunctionJob_verify_membershipChecks user belongs to project before ANY operation_log_activityRecords every change to a task automaticallycreate_taskCreates task + logs creation in one transactionget_tasksReturns all tasks for a projectget_taskReturns one taskupdate_taskUpdates task + logs exactly what changeddelete_taskDeletes taskget_task_logsReturns full history of changes for a task"""