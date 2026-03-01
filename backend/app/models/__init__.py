from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.task import Task, ActivityLog
"""**What this file does:**
- Imports all models in one place
- This is important — when `main.py` runs `create_all()`, it needs to know about ALL models to create the tables in PostgreSQL
"""