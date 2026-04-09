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


async def send_verification_email(email: str, token: str, name: str) -> bool:
    """Send email verification email"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    try:
        if onesignal and settings.ONESIGNAL_APP_ID:
            body = f"Hello {name},\n\nPlease verify your email: {verification_url}"
            await onesignal.send_email(email, "Verify Your Email", f"<h1>Hello {name}</h1><p>Please verify your email: <a href='{verification_url}'>{verification_url}</a></p>")
            return True

        if not fm:
            logger.info(f"Email service disabled - verification email for {email} (token: {token[:10]}...)")
            return True
            
        message = MessageSchema(
            subject="Verify Your Email - Resume Matching Platform",
            recipients=[email],
            body=f"""
            Hello {name},
            
            Thank you for registering with the Resume Matching Platform!
            
            Please verify your email address by clicking the link below:
            {verification_url}
            
            This link will expire in 48 hours.
            
            If you did not create an account, please ignore this email.
            
            Best regards,
            Resume Matching Platform Team
            """,
            subtype=MessageType.plain
        )
        await fm.send_message(message)
        logger.info(f"Verification email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False

async def send_password_reset_email(email: str, token: str, name: str) -> bool:
    """Send password reset email with enhanced HTML template"""
    try:
        if not fm:
            logger.info(f"Email service disabled - password reset email for {email} (token: {token[:10]}...)")
            return True
            
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        # Enhanced HTML email template
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
                .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; border-radius: 4px; font-size: 14px; }}
                .footer {{ background-color: #f0f0f0; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
                .token-info {{ background-color: #e8f4f8; padding: 15px; border-radius: 6px; margin: 20px 0; font-size: 13px; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{name}</strong>,</p>
                    
                    <p>We received a request to reset your password for your Resume Matching Platform account.</p>
                    
                    <p><strong>Click the button below to reset your password:</strong></p>
                    
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <p>Or copy this link if the button doesn't work:</p>
                    <div class="token-info">
                        {reset_url}
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Important:</strong> This link will expire in 24 hours for security reasons.
                    </div>
                    
                    <p><strong>What if you didn't request this?</strong></p>
                    <p>If you did not request a password reset, please ignore this email and your password will remain unchanged. Your account is secure.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                    
                    <p><strong>Security Tips:</strong></p>
                    <ul>
                        <li>Never share your password reset link with anyone</li>
                        <li>Make sure your password is strong (8+ characters with letters and numbers)</li>
                        <li>We will never ask for your password via email</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>© Resume Matching Platform. All rights reserved.</p>
                    <p>If you have any questions, contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        plain_body = f"""
        Hello {name},
        
        We received a request to reset your password for your Resume Matching Platform account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours for security reasons.
        
        If you did not request this, please ignore this email and your password will remain unchanged.
        
        Best regards,
        Resume Matching Platform Team
        """
        
        if onesignal and settings.ONESIGNAL_APP_ID:
            await onesignal.send_email(email, "Password Reset Request", html_body)
            return True

        if not fm:
            logger.info(f"Email service disabled - password reset email for {email} (token: {token[:10]}...)")
            return True
            
        # ... (rest of the fastmail logic remains as fallback)
        message = MessageSchema(
            subject="Password Reset Request - Resume Matching Platform",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html
        )
        await fm.send_message(message)
        logger.info(f"Password reset email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False

async def send_mfa_email(email: str, code: str, name: str) -> bool:
    """Send Multi-Factor Authentication code via email"""
    try:
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1f2937; margin: 0; padding: 0; }}
                .container {{ max-width: 500px; margin: 40px auto; background-color: #ffffff; padding: 0; border-radius: 16px; border: 1px solid #e5e7eb; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
                .header {{ background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 32px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.025em; }}
                .content {{ padding: 32px; text-align: center; }}
                .code-box {{ background-color: #f3f4f6; border: 2px dashed #6366f1; border-radius: 12px; padding: 20px; margin: 24px 0; font-family: 'Courier New', monospace; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #4f46e5; }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }}
                .warning {{ font-size: 13px; color: #ef4444; margin-top: 16px; font-weight: 500; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Identity Verification</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{name}</strong>,</p>
                    <p>To access your account, please enter the following 6-digit verification code:</p>
                    <div class="code-box">{code}</div>
                    <p class="warning">This code will expire in 10 minutes.</p>
                    <p>If you didn't try to log in, please secure your account immediately.</p>
                </div>
                <div class="footer">
                    <p>© ResumeMatch. All rights reserved.</p>
                    <p>AI-Powered Talent Matching Ecosystem</p>
                </div>
            </div>
        </body>
        </html>
        """

        if onesignal and settings.ONESIGNAL_APP_ID:
            await onesignal.send_email(email, f"{code} is your verification code", html_body)
            return True

        if not fm:
            logger.info(f"Email service disabled - MFA code for {email}: {code}")
            return True
            
        message = MessageSchema(
            subject=f"{code} is your verification code",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html
        )
        await fm.send_message(message)
        logger.info(f"MFA email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send MFA email to {email}: {str(e)}")
        return False
