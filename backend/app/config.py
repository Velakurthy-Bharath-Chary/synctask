from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
"""What this file does:

Reads your .env file automatically
Makes the settings available everywhere in the app as settings.DATABASE_URL, settings.SECRET_KEY etc"""