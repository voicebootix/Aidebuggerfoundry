"""
Authentication API Router - UPDATED
Production-ready authentication with asyncpg database operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Optional
import asyncpg
from datetime import datetime

from app.database.db import get_db
from app.database.models import *
from app.utils.auth_utils import (
    get_current_user, create_access_token, verify_password, 
    get_password_hash, get_user_by_email, create_user
)
from app.utils.security_validator import SecurityValidator
from app.utils.logger import get_logger

router = APIRouter(tags=["Authentication"])
logger = get_logger("authentication_api")
security_validator = SecurityValidator()

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    request: UserRegistrationRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Register new user account with asyncpg database operations"""
    
    try:
        # Validate input security
        security_issues = await security_validator.validate_input(request.email)
        if security_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security validation failed: {security_issues[0].description}"
            )
        
        # Check if user already exists
        existing_user = await get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = await create_user(db, request.email, request.full_name, request.password)
        
        # Generate access token
        access_token = create_access_token(data={"sub": new_user['email']})
        
        logger.info(f"New user registered: {new_user['email']}")
        
        return UserRegistrationResponse(
            user_id=new_user['id'],
            email=new_user['email'],
            full_name=new_user['full_name'],
            access_token=access_token,
            token_type="bearer",
            message="Registration successful! Welcome to AI Debugger Factory!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: asyncpg.Connection = Depends(get_db)
):
    """User login with asyncpg database operations"""
    
    try:
        # Get user from database
        user = await get_user_by_email(db, form_data.username)
        
        if not user or not verify_password(form_data.password, user['hashed_password']):
            logger.warning(f"Failed login attempt: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user['email']})
        
        logger.info(f"User logged in: {user['email']}")
        
        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user['id'],
            email=user['email'],
            full_name=user['full_name'],
            is_verified=user['is_verified']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: Dict = Depends(get_optional_current_user)
):
    """Get current user profile"""
    
    return UserProfileResponse(
        user_id=current_user['id'],
        email=current_user['email'],
        full_name=current_user['full_name'],
        is_verified=current_user['is_verified'],
        member_since=current_user['created_at'].isoformat(),
        total_projects=0,  # Would be calculated from database
        total_revenue=0.0,  # Would be calculated from revenue sharing
        account_status="active"
    )
