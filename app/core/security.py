# core/security.py
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from passlib.context import CryptContext
from .config import settings

# Use Argon2 first (new hashes) but keep bcrypt in schemes so old hashes still verify.
# Passlib will create new hashes using the first scheme in the list (argon2).
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        return user_id
    except jwt.JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored hash. Works for both bcrypt and argon2 hashes.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash the provided password. New hashes will use Argon2 (since it's first in schemes).
    """
    return pwd_context.hash(password)

def needs_rehash(hashed_password: str) -> bool:
    """
    Return True if the given hash should be rehashed according to current policy (e.g. upgrade from bcrypt -> argon2).
    Use this after successful verification to migrate hashes.
    """
    return pwd_context.needs_update(hashed_password)
