"""
Authentication Utilities for AI Debugger Factory
Complete JWT authentication system with password hashing
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg

from app.config import settings
from app.database.db import get_db
from app.utils.logger import get_logger

logger = get_logger("auth_utils")

# Security configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRATION_HOURS * 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password processing failed"
        )

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token creation failed"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: asyncpg.Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception
    
    try:
        # Fetch user from database using asyncpg
        user = await db.fetchrow(
            "SELECT id, email, full_name, is_active, is_verified, created_at FROM users WHERE email = $1",
            email
        )
        
        if user is None:
            logger.warning(f"User not found for email: {email}")
            raise credentials_exception
        
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Convert to dict for compatibility
        return dict(user)
        
    except Exception as e:
        logger.error(f"Database error in get_current_user: {e}")
        raise credentials_exception

def validate_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_user_by_email(db: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from database"""
    try:
        user = await db.fetchrow(
            "SELECT id, email, full_name, hashed_password, is_active, is_verified, created_at FROM users WHERE email = $1",
            email
        )
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Database error in get_user_by_email: {e}")
        return None

async def create_user(db: asyncpg.Connection, email: str, full_name: str, password: str) -> Dict[str, Any]:
    """Create new user in database"""
    try:
        hashed_password = get_password_hash(password)
        
        user = await db.fetchrow(
            """
            INSERT INTO users (email, full_name, hashed_password, is_active, is_verified)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, email, full_name, is_active, is_verified, created_at
            """,
            email, full_name, hashed_password, True, False
        )
        
        logger.info(f"Created new user: {email}")
        return dict(user)
        
    except Exception as e:
        logger.error(f"Database error in create_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )