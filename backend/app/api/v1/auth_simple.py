"""
Simplified Authentication API Endpoints (Alternative - No Email Verification Required)
Use this if the main auth endpoints are not working
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import (
    UserSignup,
    UserLogin,
    TokenResponse,
    UserResponse
)
from loguru import logger

router = APIRouter(prefix="/auth-simple", tags=["authentication-simple"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup_simple(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """Register a new user (simplified - auto-verified)"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
        
        if existing_user:
            logger.warning(f"Signup attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user (auto-verified for simplicity)
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            full_name=user_data.full_name.strip(),
            email=user_data.email.lower().strip(),
            phone=user_data.phone if user_data.phone else None,
            hashed_password=hashed_password,
            role=user_data.role,
            is_verified=True,  # Auto-verify
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered (simple): {new_user.email}")
        return new_user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_simple(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens (simplified)"""
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)  # Refresh user object after commit
    
    # Create tokens
    role_value = user.role.value if hasattr(user.role, "value") else user.role
    access_token = create_access_token(data={"sub": user.id, "role": role_value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    logger.info(f"User logged in (simple): {user.email}")
    
    # Convert user to UserResponse schema
    user_response = UserResponse.from_orm(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )
