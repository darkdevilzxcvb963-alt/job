"""
Dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole
from typing import Callable, Optional

security = HTTPBearer()

async def get_user_from_token(token: str, db: Session) -> User:
    """Core logic to get user from token"""
    payload = verify_token(token, "access")
    user_id = payload.get("sub")
    
    if not user_id:
        from loguru import logger
        logger.warning("Token payload missing 'sub' field")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Ensure user_id is treated as string for UUID lookup
    user = db.query(User).filter(User.id == str(user_id)).first()
    if user is None:
        from loguru import logger
        logger.warning(f"User not found in database for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return await get_user_from_token(credentials.credentials, db)

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is present, otherwise None"""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_user_from_token(credentials.credentials, db)
    except HTTPException:
        return None

async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get current user and verify email is verified"""
    # Auto-verify if email is not configured (for development)
    from app.core.config import settings
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        if not current_user.is_verified:
            current_user.is_verified = True
            db.commit()
            db.refresh(current_user)
        return current_user
    
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access this resource."
        )
    return current_user

def require_role(allowed_roles: list[UserRole]):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_verified_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker
