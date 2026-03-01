from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Create connection to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our models
class Base(DeclarativeBase):
    pass

def get_db():
    """Give a database session to each request, close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""What this file does:

Connects to your PostgreSQL database
Creates a session factory so every API request gets its own DB connection
get_db() is used by every route to access the database"""        