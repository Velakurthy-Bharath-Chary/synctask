from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import get_project_analytics
from app.services.project_service import get_project

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/projects/{project_id}")
def project_analytics(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # First verify user is a member of this project
    get_project(db, project_id, current_user.id)
    
    # Then return analytics data
    return get_project_analytics(db, project_id)