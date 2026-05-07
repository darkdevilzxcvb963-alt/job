"""
Email service for sending verification and password reset emails
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from loguru import logger
from app.services.notification_service import NotificationService

# Initialize Unified Notification Service
notification_service = NotificationService()

# Direct SMTP configuration (via fastapi-mail)
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
        logger.info("Direct SMTP service initialized")
except Exception as e:
    logger.warning(f"Direct SMTP initialization skipped: {str(e)}")


async def _send_email_common(email: str, subject: str, html_body: str, plain_body: str = None) -> bool:
    """Unified internal helper: Mailjet → Gmail SMTP (2-tier, no mocking)"""
    
    # 1. Try via NotificationService (Mailjet → Gmail SMTP)
    try:
        result = await notification_service.send_email(email, subject, html_body)
        if result:
            logger.info(f"✅ Email delivered to {email} via NotificationService")
            return True
        logger.warning(f"NotificationService returned False for {email}")
    except Exception as e:
        logger.error(f"NotificationService exception for {email}: {str(e)}")

    # 2. Last resort: Try fastapi-mail direct SMTP
    if fm:
        try:
            from_email = settings.MAIL_USERNAME if "gmail.com" in settings.MAIL_SERVER.lower() else settings.MAIL_FROM
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=html_body if html_body else plain_body,
                subtype=MessageType.html if html_body else MessageType.plain,
                from_address=from_email
            )
            await fm.send_message(message)
            logger.info(f"✅ Email delivered to {email} via fastapi-mail")
            return True
        except Exception as e:
            logger.error(f"❌ fastapi-mail SMTP also failed for {email}: {str(e)}")
    
    # NO MOCK — if we get here, email genuinely failed
    logger.error(f"❌ CRITICAL: All email delivery methods failed for {email} (subject: {subject})")
    return False

async def send_verification_email(email: str, token: str, name: str) -> bool:
    """Send email verification email"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = "Verify Your Email - Resume Matching Platform"
    html_body = f"<h1>Hello {name}</h1><p>Please verify your email: <a href='{verification_url}'>{verification_url}</a></p>"
    plain_body = f"Hello {name},\n\nPlease verify your email address: {verification_url}"
    return await _send_email_common(email, subject, html_body, plain_body)

async def send_password_reset_email(email: str, token: str, name: str) -> bool:
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Password Reset Request - Resume Matching Platform"
    html_body = f"<h1>Password Reset</h1><p>Hello {name}, click here: <a href='{reset_url}'>Reset Password</a></p>"
    plain_body = f"Hello {name},\n\nReset your password here: {reset_url}"
    return await _send_email_common(email, subject, html_body, plain_body)

async def send_mfa_email(email: str, code: str, name: str) -> bool:
    """Send Multi-Factor Authentication code"""
    subject = f"{code} is your verification code"
    html_body = f"<h1>Verification Code</h1><p>Hello {name}, your code is: <strong>{code}</strong></p>"
    plain_body = f"Hello {name},\n\nYour verification code is: {code}"
    return await _send_email_common(email, subject, html_body, plain_body)
