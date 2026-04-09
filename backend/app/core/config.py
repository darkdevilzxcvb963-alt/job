"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Get the base directory (backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

# Load environment variables from .env file explicitly
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600  # 1 year (unlimited)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 36500  # 100 years (effectively unlimited)
    
    # Database
    DATABASE_URL: str = f"sqlite:///{ (BASE_DIR.parent / 'resume_matching.db').resolve().as_posix() }"
    DB_BACKUP_DIR: str = "./backups"
    DB_PERSISTENT: bool = True
    
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_2: str = ""
    GEMINI_API_KEY_3: str = ""
    GEMINI_API_KEY_4: str = ""
    GEMINI_API_KEY_5: str = ""
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # LlamaParse Configuration
    LLAMA_CLOUD_API_KEY: str = ""
    
    # NLP Configuration
    SPACY_MODEL: str = "en_core_web_sm"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = str(BASE_DIR.parent / "uploads")
    
    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Frontend URL
    FRONTEND_URL: str = "http://127.0.0.1:3000"
    
    # Email Configuration
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@resumematching.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Resume Matching Platform"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""  # Your Twilio number e.g. +1xxxxxxxxxx

    # OneSignal Configuration
    ONESIGNAL_APP_ID: str = ""
    ONESIGNAL_REST_API_KEY: str = ""

    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = "YOUR_GOOGLE_CLIENT_ID"
    GOOGLE_AUTH_ENABLED: bool = True
    GOOGLE_AUTO_VERIFY: bool = True
    ALLOWED_GOOGLE_DOMAINS: List[str] = []  # Empty list means all domains allowed
    
    # Password Reset
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins"""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
    
    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        """Get allowed file extensions"""
        return ["pdf", "docx", "doc"]
    
    class Config:
        env_file = str(env_path) if env_path.exists() else ".env"
        case_sensitive = True

settings = Settings()
print(f"DEBUG: BASE_DIR is {BASE_DIR}")
print(f"DEBUG: DATABASE_URL is {settings.DATABASE_URL}")
