"""
VehicleIQ JWT Authentication Module
Provides password hashing, JWT token issuance, and FastAPI security dependencies.
"""

import os
from datetime import datetime, timedelta
import logging
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("VehicleIQ.Auth")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vehicleiq_super_secret_jwt_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()

# In-memory user database for dev demo
USER_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@vehicleiq.ai",
        "hashed_password": "pbkdf2:sha256:admin123",
    }
}

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    import hashlib
    salt = "vehicleiq_salt_"
    return "pbkdf2:sha256:" + hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """FastAPI dependency enforcing JWT authentication on protected endpoints."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate JWT credentials")
