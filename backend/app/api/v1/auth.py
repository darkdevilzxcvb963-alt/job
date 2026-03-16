"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_verification_token,
    generate_password_reset_token
)
from app.core.email import send_verification_email, send_password_reset_email
from app.core.config import settings
from app.core.dependencies import get_current_user, get_current_verified_user
from app.models.user import User, UserRole, CandidateProfile, RecruiterProfile
from app.models.password_reset import PasswordReset
from app.schemas.auth import (
    UserSignup,
    UserLogin,
    GoogleAuth,
    TokenResponse,
    UserResponse,
    UserUpdate,
    PasswordResetRequest,
    PasswordReset as PasswordResetSchema,
    EmailVerification,
    RefreshTokenRequest,
    ChangePassword
)
from google.oauth2 import id_token
from google.auth.transport import requests
from loguru import logger
import secrets

router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """Register a new user with comprehensive validation and database storage"""
    try:
        # Input validation: email
        existing_email = db.query(User).filter(
            User.email == user_data.email.lower().strip()
        ).first()
        
        if existing_email:
            logger.warning(f"Signup attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please use a different email or login."
            )
        
        # Input validation: phone (if provided)
        if user_data.phone and user_data.phone.strip():
            existing_phone = db.query(User).filter(
                User.phone == user_data.phone.strip()
            ).first()
            if existing_phone:
                logger.warning(f"Signup attempt with existing phone: {user_data.phone}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered. Please use a different phone number."
                )
        
        # Input validation: full name
        full_name = user_data.full_name.strip()
        if len(full_name) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name must be at least 2 characters long"
            )
        
        # Input validation: password strength (done by schema, but extra check)
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with letters and numbers"
            )
        
        # Hash password securely
        hashed_password = get_password_hash(user_data.password)
        
        # Generate email verification token
        verification_token = generate_verification_token()
        
        # Create new user with all validated data
        new_user = User(
            full_name=full_name,
            email=user_data.email.lower().strip(),
            phone=user_data.phone.strip() if user_data.phone and user_data.phone.strip() else None,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(
                hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
            ),
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add user to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created successfully: {new_user.email} (ID: {new_user.id}, Role: {new_user.role})")
        
        # Create associated profile based on role
        try:
            if new_user.role == UserRole.JOB_SEEKER:
                profile = CandidateProfile(user_id=new_user.id)
                db.add(profile)
                logger.info(f"Created CandidateProfile for user: {new_user.email}")
            elif new_user.role == UserRole.RECRUITER:
                # Use company_name from signup data if available
                company_name = getattr(user_data, 'company_name', 'My Company') or 'My Company'
                profile = RecruiterProfile(user_id=new_user.id, company_name=company_name)
                db.add(profile)
                logger.info(f"Created RecruiterProfile for user: {new_user.email}")
            
            db.commit()
        except Exception as profile_err:
            logger.error(f"Failed to create profile for user {new_user.email}: {str(profile_err)}")
            # Don't fail the whole signup if profile creation fails, but it's a serious issue
            db.rollback()
        
        # Auto-verify in development mode or if email is not configured
        if settings.DEBUG or not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
            new_user.is_verified = True
            new_user.verification_token = None
            new_user.verification_token_expires = None
            db.commit()
            db.refresh(new_user)
            logger.info(f"User auto-verified (development mode): {new_user.email}")
        else:
            # Send verification email
            try:
                await send_verification_email(new_user.email, verification_token, new_user.full_name)
                logger.info(f"Verification email sent to: {new_user.email}")
            except Exception as e:
                logger.error(f"Failed to send verification email to {new_user.email}: {str(e)}")
                # Auto-verify on email failure for development
                new_user.is_verified = True
                new_user.verification_token = None
                new_user.verification_token_expires = None
                db.commit()
                db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.email}")
        return new_user
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    try:
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
        
        logger.info(f"User logged in: {user.email}")
        
        # Convert user to UserResponse schema
        user_response = UserResponse.from_orm(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during login: {str(e)}")
        # DEBUG: Return actual error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )

@router.post("/google-auth", response_model=TokenResponse)
async def google_auth(
    auth_data: GoogleAuth,
    db: Session = Depends(get_db)
):
    """Authenticate user with Google ID Token with enhanced security and restrictions"""
    try:
        # 1. Check if Google Auth is globally enabled
        if not settings.GOOGLE_AUTH_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Google Authentication is currently disabled by administrator."
            )

        # 2. Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            auth_data.id_token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        # 3. Extract and validate user info
        email = idinfo['email'].lower().strip()
        domain = email.split('@')[-1]
        full_name = idinfo.get('name', '')
        google_id = idinfo.get('sub') # Unique Google ID
        
        # 4. Domain restriction check
        if settings.ALLOWED_GOOGLE_DOMAINS and domain not in settings.ALLOWED_GOOGLE_DOMAINS:
            logger.warning(f"Google Auth denied: Domain {domain} not in allowed list")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sign-up with Google is restricted to certain domains. Domain '{domain}' is not allowed."
            )

        # 5. Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user if they don't exist
            user = User(
                full_name=full_name,
                email=email,
                role=auth_data.role,
                is_active=True,
                is_verified=settings.GOOGLE_AUTO_VERIFY,
                auth_provider="google",
                auth_provider_id=google_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                hashed_password=get_password_hash(secrets.token_urlsafe(32)) # Dummy password for Google users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created via Google Auth: {email}")
        else:
            # Update existing user tracking if not already set
            if user.auth_provider != "google":
                user.auth_provider = "google"
                user.auth_provider_id = google_id
                # If they were already verified, keep it, otherwise update based on settings
                if settings.GOOGLE_AUTO_VERIFY:
                    user.is_verified = True
                db.commit()
                db.refresh(user)
                logger.info(f"Linked existing user to Google Auth: {email}")
        
        # 6. Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Create tokens
        role_value = user.role.value if hasattr(user.role, "value") else user.role
        access_token = create_access_token(data={"sub": user.id, "role": role_value})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        logger.info(f"User logged in via Google Auth: {email}")
        
        user_response = UserResponse.from_orm(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 403 denied)
        raise
    except ValueError as e:
        # Invalid token
        logger.warning(f"Invalid Google ID token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during Google Auth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during Google Auth: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = verify_token(token_data.refresh_token, "refresh")
    user_id: str = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    role_value = user.role.value if hasattr(user.role, "value") else user.role
    access_token = create_access_token(data={"sub": user.id, "role": role_value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/verify-email", response_model=dict)
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    user = db.query(User).filter(
        User.verification_token == verification_data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    if user.verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    
    logger.info(f"Email verified for user: {user.email}")
    return {"message": "Email verified successfully"}

@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset with enhanced security and validation"""
    # Validate email format
    email_lower = reset_request.email.lower().strip()
    
    # Check rate limiting - max 3 requests per hour
    from datetime import datetime, timedelta
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    user = db.query(User).filter(User.email == email_lower).first()
    
    reset_token = None
    if user:
        # Check if user has too many reset requests (optimized query)
        user_recent_requests = db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.created_at >= one_hour_ago
        ).count()
        
        if user_recent_requests >= 3:
            logger.warning(f"Rate limit exceeded for password reset: {email_lower}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many password reset requests. Please try again later."
            )
        
        # Invalidate existing unused reset tokens
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.is_used == False
        ).update({"is_used": True})
        
        reset_token = generate_password_reset_token()
        expires_at = datetime.utcnow() + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        
        db.add(password_reset)
        db.commit()
        
        try:
            email_sent = await send_password_reset_email(user.email, reset_token, user.full_name)
            if not email_sent and settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                logger.error(f"Email service error: Failed to send to {user.email}")
                # If email is configured but fails, we should return an error
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="The email service is currently unavailable. Please try again later."
                )
            logger.info(f"Password reset email sent to {user.email}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
    else:
        logger.info(f"Password reset requested for non-existent email: {email_lower}")
    
    # Build response
    response = {
        "message": "If an account exists with this email, a password reset link has been sent. Please check your email."
    }
    
    # In development mode (no email configured), include the reset link directly
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        if reset_token:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            response["dev_reset_link"] = reset_url
            response["message"] = f"Development Mode: {response['message']} Or use this link: {reset_url}"
            logger.info(f"Development mode: Reset link generated for {email_lower}: {reset_url}")
    
    return response

@router.post("/validate-reset-token", response_model=dict)
async def validate_reset_token(
    token_data: EmailVerification,  # Reusing schema that has a 'token' field
    db: Session = Depends(get_db)
):
    """Validate if a password reset token is valid and not expired"""
    token = token_data.token
    
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required"
        )
    
    password_reset = db.query(PasswordReset).filter(
        PasswordReset.token == token,
        PasswordReset.is_used == False
    ).first()
    
    if not password_reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    if password_reset.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    return {
        "valid": True,
        "expires_at": password_reset.expires_at.isoformat(),
        "expires_in_hours": max(0, (password_reset.expires_at - datetime.utcnow()).total_seconds() / 3600)
    }

@router.post("/reset-password", response_model=dict)
async def reset_password(
    reset_data: PasswordResetSchema,
    db: Session = Depends(get_db)
):
    """Reset password using token with enhanced security and logging"""
    # Validate token is present
    if not reset_data.token or not reset_data.token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format"
        )
    
    password_reset = db.query(PasswordReset).filter(
        PasswordReset.token == reset_data.token.strip(),
        PasswordReset.is_used == False
    ).first()
    
    if not password_reset:
        logger.warning(f"Password reset attempted with invalid token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please request a new password reset."
        )
    
    if password_reset.expires_at < datetime.utcnow():
        # Mark the token as used to prevent reuse
        password_reset.is_used = True
        password_reset.used_at = datetime.utcnow()
        db.commit()
        
        logger.warning(f"Expired password reset token attempted for user: {password_reset.user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new password reset."
        )
    
    # Additional validation - prevent same password
    user = password_reset.user
    if verify_password(reset_data.new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as your current password"
        )
    
    user.hashed_password = get_password_hash(reset_data.new_password)
    password_reset.is_used = True
    password_reset.used_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Password successfully reset for user: {user.email}")
    return {
        "message": "Password reset successfully. You can now log in with your new password."
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.location is not None:
        current_user.location = user_update.location
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for a logged-in user"""
    from app.core.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Prevent same password
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as your current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    return {"message": "Password changed successfully"}

@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user"""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}
