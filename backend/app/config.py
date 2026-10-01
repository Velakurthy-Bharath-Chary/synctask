from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Database Configuration - supports either DATABASE_URL or individual params
    DATABASE_URL: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    
    # Supabase (optional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None
    
    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "*"]
    
    # Database pooling
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600

    class Config:
        env_file = ".env"

    def get_database_url(self) -> str:
        """Build DATABASE_URL from individual params or return existing one."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.DB_USER and self.DB_PASSWORD and self.DB_HOST:
            # URL-encode the password to handle special characters
            encoded_password = quote_plus(self.DB_PASSWORD)
            return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        raise ValueError("Either DATABASE_URL or (DB_USER, DB_PASSWORD, DB_HOST) must be set")

settings = Settings()