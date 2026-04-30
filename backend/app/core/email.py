"""
Email service for sending verification and password reset emails
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from loguru import logger

# OneSignal fallback
try:
    from app.services.notification_service import NotificationService
    onesignal = NotificationService()
except ImportError:
    onesignal = None

# Email configuration - disabled for development
# Use optional email or mock sending
conf = None
fm = None

try:
    if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_TLS,
            MAIL_SSL_TLS=settings.MAIL_SSL,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        fm = FastMail(conf)
        logger.info("Email service initialized")
    else:
        logger.warning("Email not configured - using mock email sending")
except Exception as e:
    logger.warning(f"Email service initialization skipped: {str(e)}")
    fm = None


async def _send_email_common(email: str, subject: str, html_body: str, plain_body: str = None) -> bool:
    """Internal helper to send email with OneSignal -> FastMail fallback"""
    # 1. Try OneSignal if enabled and configured
    if onesignal and settings.ONESIGNAL_APP_ID and settings.ONESIGNAL_REST_API_KEY:
        try:
            logger.info(f"Attempting to send email via OneSignal to {email}")
            await onesignal.send_email(email, subject, html_body)
            return True
        except Exception as e:
            logger.warning(f"OneSignal email delivery failed for {email}: {str(e)}. Falling back to SMTP.")
    
    # 2. Try FastMail/SMTP if configured
    if fm:
        try:
            logger.info(f"Attempting to send email via SMTP to {email}")
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=html_body if html_body else plain_body,
                subtype=MessageType.html if html_body else MessageType.plain
            )
            await fm.send_message(message)
            return True
        except Exception as e:
            logger.error(f"SMTP email delivery failed for {email}: {str(e)}")
    else:
        logger.warning(f"No email providers available. Mocking email to {email}")
        if settings.DEBUG:
            logger.info(f"MOCK EMAIL CONTENT:\nSubject: {subject}\nTo: {email}\nBody: {plain_body or 'HTML Content'}")
        return True # Return true in dev/mock mode
        
    return False

async def send_verification_email(email: str, token: str, name: str) -> bool:
    """Send email verification email"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = "Verify Your Email - Resume Matching Platform"
    html_body = f"<h1>Hello {name}</h1><p>Please verify your email: <a href='{verification_url}'>{verification_url}</a></p>"
    plain_body = f"Hello {name},\n\nPlease verify your email address: {verification_url}"
    
    return await _send_email_common(email, subject, html_body, plain_body)

async def send_password_reset_email(email: str, token: str, name: str) -> bool:
    """Send password reset email with enhanced HTML template"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Password Reset Request - Resume Matching Platform"
    
    # Using the existing template logic but via common sender
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ background-color: white; padding: 30px; margin: 0; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
            .button:hover {{ transform: scale(1.02); }}
            .footer {{ background-color: #f0f0f0; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><h1>Password Reset</h1></div>
            <div class="content">
                <p>Hello <strong>{name}</strong>,</p>
                <p>Click the button below to reset your password:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p>This link will expire in 24 hours.</p>
            </div>
            <div class="footer"><p>© Resume Matching Platform</p></div>
        </div>
    </body>
    </html>
    """
    plain_body = f"Hello {name},\n\nReset your password here: {reset_url}"
    
    return await _send_email_common(email, subject, html_body, plain_body)

async def send_mfa_email(email: str, code: str, name: str) -> bool:
    """Send Multi-Factor Authentication code via email"""
    subject = f"{code} is your verification code"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1f2937; margin: 0; padding: 0; }}
            .container {{ max-width: 500px; margin: 40px auto; background-color: #ffffff; padding: 0; border-radius: 16px; border: 1px solid #e5e7eb; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 32px 20px; text-align: center; }}
            .code-box {{ background-color: #f3f4f6; border: 2px dashed #6366f1; border-radius: 12px; padding: 20px; margin: 24px 0; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #4f46e5; text-align: center; }}
            .content {{ padding: 32px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><h1>Verification Code</h1></div>
            <div class="content">
                <p>Hello <strong>{name}</strong>,</p>
                <p>Your verification code is:</p>
                <div class="code-box">{code}</div>
                <p>This code expires in 10 minutes.</p>
            </div>
        </div>
    </body>
    </html>
    """
    plain_body = f"Hello {name},\n\nYour verification code is: {code}"
    
    return await _send_email_common(email, subject, html_body, plain_body)
