from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# bcrypt is the hashing algorithm for passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Turn plain password into a secure hash."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Check if plain password matches the stored hash."""
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    """Create a JWT token with expiry time."""
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """Read and verify a JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
""""What this file does:

hash_password — converts Cmrec@1234 into something like $2b$12$... before saving to DB
verify_password — checks login password against the hash
create_access_token — creates a JWT token after login
decode_token — reads the token on every request to identify the user"""
