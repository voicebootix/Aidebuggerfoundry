"""
Authentication API Router
Production-ready authentication and authorization
Enhanced with security features and session management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.database.db import get_db
from app.database.models import *
from app.utils.security_validator import SecurityValidator
from app.utils.logger import get_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger("authentication_api")
security_validator = SecurityValidator()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register new user account
    Enhanced security validation and verification
    """
    
    try:
        # Validate input security
        security_issues = await security_validator.validate_input(request.email)
        if security_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security validation failed: {security_issues[0].description}"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(request.password)
        new_user = User(
            email=request.email,
            full_name=request.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate access token
        access_token = create_access_token(data={"sub": new_user.email})
        
        logger.log_structured("info", "New user registered", {
            "user_id": new_user.id,
            "email": new_user.email
        })
        
        return UserRegistrationResponse(
            user_id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            access_token=access_token,
            token_type="bearer",
            message="Registration successful! Welcome to AI Debugger Factory!"
        )
        
    except Exception as e:
        logger.log_structured("error", "User registration failed", {
            "email": request.email,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login with OAuth2 password flow
    Secure authentication with token generation
    """
    
    try:
        # Authenticate user
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.log_structured("warning", "Failed login attempt", {
                "email": form_data.username
            })
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        # Update last login
        user.updated_at = datetime.now()
        db.commit()
        
        logger.log_structured("info", "User logged in", {
            "user_id": user.id,
            "email": user.email
        })
        
        return UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_structured("error", "Login error", {
            "email": form_data.username,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile and statistics"""
    
    # This would typically fetch additional user statistics
    return UserProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_verified=current_user.is_verified,
        member_since=current_user.created_at.isoformat(),
        total_projects=0,  # Would be calculated from database
        total_revenue=0.0,  # Would be calculated from revenue sharing
        account_status="active"
    )