from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    member = "member"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.member

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    """What this file does:

UserCreate — validates data when registering a new user
UserLogin — validates data when logging in
UserOut — what we send back to the frontend (notice no password!)
Token — the response after successful login containing the JWT"""
"""Base.metadata.create_all(bind=engine)
```

This tells SQLAlchemy **"create all tables in PostgreSQL"**.

But SQLAlchemy can only create tables it **knows about**. By importing all models in `__init__.py`, we make sure SQLAlchemy sees ALL of them before creating tables.

---

## Simple analogy:
```
SQLAlchemy says: "What tables should I create?"

__init__.py says: "Here are ALL the models:
                  - User
                  - Project
                  - ProjectMember  
                  - Task
                  - ActivityLog"

SQLAlchemy says: Got it, creating all 5 tables!"""