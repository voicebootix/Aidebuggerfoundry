"""
Emergency Authentication Fix for AI Debugger Factory
Fixed version with proper optional authentication support
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
from app.database.db import get_db
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger("auth_utils")

# Security setup
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'fallback-secret-key')
ALGORITHM = getattr(settings, 'JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'JWT_EXPIRATION_HOURS', 24) * 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # CRITICAL: auto_error=False for optional auth

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: asyncpg.Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Get current authenticated user - REQUIRES authentication"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        user = await db.fetchrow(
            "SELECT id, email, full_name, is_active, is_verified, created_at FROM users WHERE email = $1",
            email
        )
        
        if user is None:
            raise credentials_exception
        
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return dict(user)
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise credentials_exception

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: asyncpg.Connection = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """Get current user if token is provided, else return None for guest access"""
    if not credentials:
        return None

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        # Invalid token = guest mode
        return None

    try:
        user = await db.fetchrow(
            "SELECT id, email, full_name, is_active, is_verified, created_at FROM users WHERE email = $1",
            email
        )
        
        if user and user['is_active']:
            return dict(user)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Database error in optional auth: {e}")
        return None

# Helper functions for asyncpg operations
async def get_user_by_email(db: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        user = await db.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None

async def create_user(db: asyncpg.Connection, email: str, full_name: str, password: str) -> Dict[str, Any]:
    """Create new user"""
    try:
        hashed_password = get_password_hash(password)
        user = await db.fetchrow(
            """
            INSERT INTO users (email, full_name, hashed_password, is_active, is_verified, created_at)
            VALUES ($1, $2, $3, TRUE, FALSE, NOW())
            RETURNING id, email, full_name, is_active, is_verified, created_at
            """,
            email, full_name, hashed_password
        )
        return dict(user)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )