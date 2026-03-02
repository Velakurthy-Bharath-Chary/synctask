from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, projects, tasks, analytics, websocket
# Import models so SQLAlchemy creates all tables on startup
from app.models import user, project, task  # noqa: F401

# Create all database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SyncTask API",
    description="Distributed Collaborative Task Manager",
    version="1.0.0"
)

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(analytics.router)
app.include_router(websocket.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "SyncTask API"}
"""

**What this file does:**

This is the **entry point** of the entire backend — it ties everything together:
```
1. Creates all DB tables on startup
2. Sets up CORS so React can talk to FastAPI
3. Registers all routers:
   - /auth
   - /projects
   - /tasks
   - /analytics
   - /ws
4. Adds a /health endpoint to check if server is running
```

---

## Now Let's Start the Backend Server!

In your terminal type:
```
uvicorn app.main:app --reload --port 8000
"""