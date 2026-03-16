"""
Authentication Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class UserSignup(BaseModel):
    """Schema for user registration with comprehensive validation"""
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="Valid email address (unique)")
    phone: Optional[str] = Field(None, min_length=10, max_length=50, description="Optional phone number")
    password: str = Field(..., min_length=8, max_length=100, description="Secure password with letters and numbers")
    role: UserRole = Field(default=UserRole.JOB_SEEKER, description="User role: job_seeker or recruiter")
    
    # Optional for recruiters
    company_name: Optional[str] = Field(None, max_length=255, description="Company name for recruiters")
    
    @validator('full_name', pre=True)
    def validate_full_name(cls, v):
        """Validate and clean full name"""
        if not v or not isinstance(v, str):
            raise ValueError('Full name is required and must be text')
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        if len(v) > 255:
            raise ValueError('Full name must not exceed 255 characters')
        # Check if name contains only letters, spaces, hyphens, and apostrophes
        if not all(c.isalpha() or c.isspace() or c in "-'" for c in v):
            raise ValueError('Full name can only contain letters, spaces, hyphens, and apostrophes')
        return v
    
    @validator('phone', pre=True, always=True)
    def validate_phone(cls, v):
        """Validate phone if provided"""
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if not isinstance(v, str):
            raise ValueError('Phone must be a string')
        v = v.strip()
        if not v:
            return None
        # Allow digits, spaces, hyphens, parentheses, plus sign
        if not all(c.isdigit() or c in ' ()-+' for c in v):
            raise ValueError('Phone number contains invalid characters')
        if len(v) < 10 or len(v) > 50:
            raise ValueError('Phone number must be between 10 and 50 characters')
        return v
    
    @validator('password', pre=True)
    def validate_password(cls, v):
        """Validate password strength"""
        if not v or not isinstance(v, str):
            raise ValueError('Password is required')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 100:
            raise ValueError('Password must not exceed 100 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit (0-9)')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter (a-z or A-Z)')
        if not any(c.isalnum() or c in '!@#$%^&*' for c in v):
            raise ValueError('Password contains invalid characters')
        return v
    
    @validator('email', pre=True)
    def validate_email(cls, v):
        """Validate email format"""
        if not v or not isinstance(v, str):
            raise ValueError('Email is required')
        v = v.lower().strip()
        if len(v) > 255:
            raise ValueError('Email is too long')
        return v
    
    class Config:
        description = "User signup request with all validation rules"

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class GoogleAuth(BaseModel):
    """Schema for Google Authentication"""
    id_token: str
    role: UserRole = UserRole.JOB_SEEKER

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    full_name: str
    email: str
    phone: Optional[str]
    role: UserRole
    is_verified: bool
    is_active: bool
    bio: Optional[str] = None
    location: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserResponse] = None

class CandidateProfileUpdate(BaseModel):
    """Schema for candidate profile update"""
    headline: Optional[str] = None
    years_of_experience: Optional[int] = None
    skills: Optional[List[str]] = None
    expertise_areas: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    salary_expectation_min: Optional[float] = None
    salary_expectation_max: Optional[float] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        from_attributes = True

class CandidateProfileResponse(BaseModel):
    """Schema for candidate profile response"""
    id: str
    user_id: str
    headline: Optional[str]
    years_of_experience: Optional[int]
    skills: Optional[List[str]]
    expertise_areas: Optional[List[str]]
    preferred_locations: Optional[List[str]]
    preferred_job_types: Optional[List[str]]
    salary_expectation_min: Optional[float]
    salary_expectation_max: Optional[float]
    profile_completion_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RecruiterProfileUpdate(BaseModel):
    """Schema for recruiter profile update"""
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_description: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        from_attributes = True

class RecruiterProfileResponse(BaseModel):
    """Schema for recruiter profile response"""
    id: str
    user_id: str
    company_name: str
    company_website: Optional[str]
    company_logo_url: Optional[str]
    company_description: Optional[str]
    company_size: Optional[str]
    company_industry: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    company_verified: bool
    total_jobs_posted: int
    active_job_postings: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str

class ChangePassword(BaseModel):
    """Schema for changing password when logged in"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

class AdminResetPassword(BaseModel):
    """Schema for admin to reset user password"""
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

class ResumeResponse(BaseModel):
    """Schema for resume/candidate match data"""
    id: str
    resume_file_path: Optional[str]
    resume_file_type: Optional[str]
    skills: Optional[List[str]] = []
    experience_years: Optional[float]
    education: Optional[List[dict]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    """Extended user response with profile details"""
    candidate_profile: Optional[CandidateProfileResponse] = None
    resume_data: Optional[ResumeResponse] = None
    
    class Config:
        from_attributes = True
