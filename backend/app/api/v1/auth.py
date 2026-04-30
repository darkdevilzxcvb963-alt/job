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
    ChangePassword,
    VerifyMFARequest,
    MFASetupResponse,
    SendOTP,
    VerifyOTP,
    MagicLinkRequest
)
from app.services.auth_service import AuthService
from app.models.auth_tokens import RefreshToken, OTPToken, LoginAttempt, VerificationToken
from app.core.email import send_mfa_email
from google.oauth2 import id_token
from google.auth.transport import requests
from loguru import logger
import secrets
from fastapi import Request, Response, Cookie
from app.core.rate_limit import check_login_rate_limit, check_otp_rate_limit
from typing import Optional

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
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
            
        # Input validation: username
        existing_username = db.query(User).filter(
            User.username == user_data.username.lower().strip()
        ).first()
        
        if existing_username:
            logger.warning(f"Signup attempt with existing username: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken. Please choose another one."
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
        
        # Set verified status based on configuration
        is_verified = False
        if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
            is_verified = True
        
        # Create new user with all validated data
        new_user = User(
            full_name=full_name,
            email=user_data.email.lower().strip(),
            username=user_data.username.lower().strip(),
            phone=user_data.phone.strip() if user_data.phone and user_data.phone.strip() else None,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(
                hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
            ),
            is_verified=is_verified,
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
            if new_user.role == UserRole.JOB_SEEKER.value:
                profile = CandidateProfile(user_id=new_user.id)
                db.add(profile)
                logger.info(f"Created CandidateProfile for user: {new_user.email}")
            elif new_user.role == UserRole.RECRUITER.value:
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
        
        # 7. Generate MFA token and send OTP instead of direct success
        mfa_token = create_access_token(
            data={"sub": new_user.id, "type": "mfa_pending", "purpose": "signup_verification"},
            expires_delta=timedelta(minutes=10)
        )
        
        # Generate and send dual MFA (Email + SMS)
        otp_code = await AuthService.send_dual_mfa(db, new_user)
        
        logger.info(f"New user registered, MFA verification required: {new_user.email}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "mfa_required": True,
            "mfa_token": mfa_token,
            "session_id": otp_code if settings.DEBUG else None
        }
    
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
    request: Request,
    response: Response,
    _ = Depends(check_login_rate_limit),
    db: Session = Depends(get_db)
):
    """Authenticate user with production security (lockout, session tracking, HTTP-only cookies)"""
    # 1. Check for account lockout before anything else
    ip_address = request.client.host
    identifier = user_data.identifier.lower().strip()
    
    if await AuthService.is_locked_out(db, identifier):
        logger.warning(f"Login blocked due to lockout: {identifier}")
        raise HTTPException(
            status_code=423,
            detail="Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
        )

    # Search by email OR username
    user = db.query(User).filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        await AuthService.track_login_attempt(db, identifier, ip_address, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    # 2. Record successful login attempt
    await AuthService.track_login_attempt(db, identifier, ip_address, True)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # 4. Auto-verify if no email service configured
    if not user.is_verified and (not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD):
        user.is_verified = True
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # 3. MFA logic (Disabled for regular logins as per request)
    """
    if user.mfa_enabled:
        # Generate temporary MFA token
        mfa_token = create_access_token(
            data={"sub": user.id, "type": "mfa_pending"},
            expires_delta=timedelta(minutes=5)
        )
        # Send dual MFA (Email + SMS)
        otp_code = await AuthService.send_dual_mfa(db, user)
        
        return TokenResponse(
            mfa_required=True,
            mfa_token=mfa_token,
            user=UserResponse.from_orm(user),
            session_id=otp_code if settings.DEBUG else None 
        )
    """

    # 4. Create tokens and secure session (Direct login)
    access_token, refresh_token = AuthService.create_session_tokens(db, user)
    
    # 5. Set HTTP-only Cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )

@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(
    data: SendOTP,
    request: Request,
    _ = Depends(check_otp_rate_limit),
    db: Session = Depends(get_db)
):
    """Generate and send a 6-digit OTP for login or verification"""
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user:
        # Don't reveal if user exists for security, but we need to for real flow?
        # For now, return success to prevent enumeration
        return {"message": "OTP sent if account exists"}
        
    otp_code = await AuthService.generate_otp(db, user.id, data.type, data.purpose)
    
    if data.type == "email":
        await send_mfa_email(user.email, otp_code, user.full_name)
    else:
        # SMS Logic here (Twilio)
        logger.info(f"SMS OTP for {user.email}: {otp_code}")
        
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    data: VerifyOTP,
    response: Response,
    db: Session = Depends(get_db)
):
    """Verify OTP and return session tokens"""
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid request")
        
    is_valid = await AuthService.verify_otp(db, user.id, data.code, data.purpose)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid OTP code")
        
    # Success -> login
    access_token, refresh_token = AuthService.create_session_tokens(db, user)
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )

# Removed Magic Link endpoints as per new production security requirements

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
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_data.id_token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
        except Exception as verify_err:
            logger.error(f"Google Token Verification Failed: {str(verify_err)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google token verification failed: {str(verify_err)}"
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

        # 7. Handle Login vs Signup Flow for Google
        is_first_login = not user.last_login or (datetime.utcnow() - user.created_at).total_seconds() < 60
        
        # Simplified: Auto-verify and bypass MFA if email not configured
        if is_first_login and (not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD):
            user.is_verified = True
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
        elif is_first_login:
            # Traditional flow: Require MFA for first login if mail is available
            mfa_token = create_access_token(
                data={"sub": user.id, "type": "mfa_pending", "purpose": "signup_verification"},
                expires_delta=timedelta(minutes=10)
            )
            otp_code = await AuthService.send_dual_mfa(db, user)
            
            return TokenResponse(
                mfa_required=True,
                mfa_token=mfa_token,
                user=UserResponse.from_orm(user),
                session_id=otp_code if settings.DEBUG else None
            )

        # Update last login for existing users
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Create direct tokens for existing Google users
        role_value = user.role.value if hasattr(user.role, "value") else user.role
        access_token = create_access_token(data={"sub": user.id, "role": role_value})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        logger.info(f"User logged in via Google Auth: {email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 403 denied)
        raise
    except ValueError as e:
        # Check if this is a hashing error misreported as a ValueError (like bcrypt 72-byte limit)
        error_msg = str(e)
        if "72 bytes" in error_msg:
            logger.error(f"Internal Hashing failure during Google Auth: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account creation failed due to internal hashing constraints. Please try a different login method."
            )
            
        # Invalid Google token
        logger.warning(f"Invalid Google ID token: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {error_msg}"
        )
    except Exception as e:
        logger.error(f"Error during Google Auth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during Google Auth: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    token_data: RefreshTokenRequest = None,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Refresh access token using secure rotation and HTTP-only cookies"""
    token_to_use = refresh_token or (token_data.refresh_token if token_data else None)
    
    if not token_to_use:
         raise HTTPException(status_code=401, detail="Refresh token missing")
         
    access_token, new_refresh_token = await AuthService.rotate_refresh_token(db, token_to_use)
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
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
    if user_update.profile_picture_url is not None:
        current_user.profile_picture_url = user_update.profile_picture_url
    
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
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and clear secure session cookies"""
    await AuthService.logout_all_devices(db, current_user.id)
    response.delete_cookie("refresh_token")
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out and all sessions ended successfully"}

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable Multi-Factor Authentication for the current user"""
    if current_user.mfa_enabled:
        return MFASetupResponse(message="MFA is already enabled", mfa_enabled=True)
        
    current_user.mfa_enabled = True
    current_user.mfa_type = "email"
    db.commit()
    
    logger.info(f"MFA enabled for user: {current_user.email}")
    return MFASetupResponse(
        message="Multi-Factor Authentication has been enabled. You will be asked for a code on your next login.",
        mfa_enabled=True
    )

@router.post("/mfa/verify", response_model=TokenResponse)
async def verify_mfa(
    verify_data: VerifyMFARequest,
    db: Session = Depends(get_db)
):
    """Verify MFA code and return full tokens"""
    payload = verify_token(verify_data.mfa_token, "mfa_pending")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    # Allow verification if it's a signup MFA OR if MFA is explicitly enabled
    is_signup_verify = payload.get("purpose") == "signup_verification"
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    if not user.mfa_enabled and not is_signup_verify:
        raise HTTPException(status_code=401, detail="Invalid MFA status")
        
    is_valid = await AuthService.verify_otp(db, user.id, verify_data.code, purpose="mfa")
    if not is_valid:
        raise HTTPException(status_code=401, detail="Incorrect or expired verification code")
    
    # If this was signup verification, mark user as verified
    if is_signup_verify:
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        
    db.commit()
    
    # Create real tokens
    role_value = user.role.value if hasattr(user.role, "value") else user.role
    access_token = create_access_token(data={"sub": user.id, "role": role_value})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )

@router.post("/mfa/disable", response_model=dict)
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable Multi-Factor Authentication"""
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    db.commit()
    
    logger.info(f"MFA disabled for user: {current_user.email}")
    return {"message": "Multi-Factor Authentication disabled"}
