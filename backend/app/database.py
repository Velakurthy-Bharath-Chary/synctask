"""
Database connection and session management for Supabase PostgreSQL.

Features:
- Optimized connection pooling for PostgreSQL
- Supabase client integration
- Connection health checks
- Proper error handling and logging
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ============================================================================
# ASYNC DATABASE SETUP (Recommended for FastAPI)
# ============================================================================

# Convert PostgreSQL URL to async PostgreSQL URL for asyncpg
database_url = settings.get_database_url()
async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine for async operations
async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "timeout": 10,
        "command_timeout": 30,
        "server_settings": {
            "application_name": "tasksyncer",
            "jit": "off",
        },
    },
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for async database sessions in FastAPI routes.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# SYNC DATABASE SETUP (For background tasks and migrations)
# ============================================================================

sync_engine = create_engine(
    database_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": 10,
        "options": "-c default_transaction_isolation=read_committed",
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False,
)


def get_db() -> AsyncGenerator[Session, None]:
    """
    Dependency for synchronous database sessions.
    Use this for background tasks and CLI commands.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# CONNECTION HEALTH CHECK
# ============================================================================

@event.listens_for(sync_engine.pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Initialize connection with PostgreSQL-specific settings."""
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SET timezone=UTC")
        logger.debug("Connection initialized with UTC timezone")
    finally:
        cursor.close()





# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    Usage:
        asyncio.run(init_db())
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def drop_db() -> None:
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")


def sync_init_db() -> None:
    """Synchronous version of init_db for migrations."""
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database tables created successfully")


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

async def check_db_connection() -> bool:
    """
    Check if the database connection is healthy.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            logger.info("Database connection healthy")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def sync_check_db_connection() -> bool:
    """Synchronous version of connection check."""
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            logger.info("Database connection healthy")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# ============================================================================
# SUPABASE CLIENT INTEGRATION
# ============================================================================

def get_supabase_client():
    """Get Supabase client (lazy load)."""
    try:
        from app.services.supabase_client import db
        return db
    except ImportError:
        logger.warning("Supabase client not available")
        return None


__all__ = [
    "Base",
    "get_db",
    "get_async_db",
    "AsyncSessionLocal",
    "SessionLocal",
    "init_db",
    "drop_db",
    "sync_init_db",
    "check_db_connection",
    "sync_check_db_connection",
    "get_supabase_client",
]        