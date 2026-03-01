from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.auth_service import register_user, login_user
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, data)
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, data.email, data.password)

"""
**What this file does:**

Think of routers as **doors** into your app:
```
POST /auth/register  ← Frontend sends username, email, password
                     ← Router validates it
                     ← Calls register_user service
                     ← Returns JWT token

POST /auth/login     ← Frontend sends email, password
                     ← Router validates it
                     ← Calls login_user service
                     ← Returns JWT token
                      The router is kept thin on purpose — it just receives the request and hands it to the service. All logic stays in services! """