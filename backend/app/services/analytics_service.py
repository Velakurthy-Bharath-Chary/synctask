from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.task import Task, TaskStatus
from app.models.user import User

def get_project_analytics(db: Session, project_id: int) -> dict:
    # Get all tasks for this project
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    total = len(tasks)

    # Count tasks by status
    status_counts = {
        "TODO": 0,
        "IN_PROGRESS": 0,
        "DONE": 0,
    }
    
    # Count tasks by priority
    priority_counts = {
        "LOW": 0, 
        "MEDIUM": 0, 
        "HIGH": 0
    }

    for task in tasks:
        status_counts[task.status.value] += 1
        priority_counts[task.priority.value] += 1

    # Calculate completion percentage
    completion_rate = round((status_counts["DONE"] / total * 100), 1) if total > 0 else 0

    # Count completed tasks per member
    member_productivity = db.query(
        User.username,
        func.count(Task.id).label("task_count")
    ).join(Task, Task.assigned_to == User.id)\
     .filter(Task.project_id == project_id, Task.status == TaskStatus.DONE)\
     .group_by(User.username).all()

    return {
        "total_tasks": total,
        "status_breakdown": status_counts,
        "priority_breakdown": priority_counts,
        "completion_rate": completion_rate,
        "member_productivity": [
            {"username": row.username, "completed_tasks": row.task_count}
            for row in member_productivity
        ],
    }
"""What this file does:
DataDescriptiontotal_tasksTotal number of tasks in projectstatus_breakdownHow many TODO, IN_PROGRESS, DONEpriority_breakdownHow many LOW, MEDIUM, HIGHcompletion_ratePercentage of tasks completedmember_productivityHow many tasks each member completed
This data powers the charts on the Analytics page in the frontend!"""