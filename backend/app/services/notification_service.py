"""
Notification Service — sends email (Mailjet/SMTP) and SMS (Twilio) notifications.
Gracefully degrades if credentials are not configured.
"""
import smtplib
import httpx
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from app.core.config import settings


class NotificationService:
    """Handles email and SMS notifications for application events."""

    # ─── Mailjet (Primary No-Domain Solution) ──────────────────────────────────

    async def _send_mailjet_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Internal helper to send email via Mailjet HTTP API."""
        if not settings.MAILJET_API_KEY or not settings.MAILJET_SECRET_KEY:
            return False

        url = "https://api.mailjet.com/v3.1/send"
        
        payload = {
            "Messages": [
                {
                    "From": {
                        "Email": settings.MAIL_FROM,
                        "Name": settings.MAIL_FROM_NAME
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": subject,
                    "HTMLPart": html_body
                }
            ]
        }

        try:
            auth_str = base64.b64encode(f"{settings.MAILJET_API_KEY}:{settings.MAILJET_SECRET_KEY}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_str}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                if response.status_code >= 400:
                    logger.error(f"Mailjet Error {response.status_code}: {response.text}")
                    return False
                logger.info(f"Email sent via Mailjet to {to_email}")
                return True
        except Exception as e:
            logger.error(f"Mailjet API request failed: {e}")
            return False

    # ─── Email Dispatcher ─────────────────────────────────────────────────────

    async def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an HTML email via Mailjet (Primary) or SMTP (Fallback)."""
        
        # 1. Try Mailjet (HTTP API - Best for Production)
        if settings.MAILJET_API_KEY and settings.MAILJET_SECRET_KEY:
            if await self._send_mailjet_email(to_email, subject, html_body):
                return True

        # 2. Try SMTP Fallback (Gmail/FastMail)
        if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
                msg["To"] = to_email
                msg.attach(MIMEText(html_body, "html"))

                def sync_send():
                    if settings.MAIL_PORT == 465 or settings.MAIL_SSL:
                        server_class = smtplib.SMTP_SSL
                    else:
                        server_class = smtplib.SMTP
                    
                    with server_class(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10) as server:
                        if settings.MAIL_PORT == 587 or settings.MAIL_TLS:
                            server.ehlo()
                            server.starttls()
                            server.ehlo()
                        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                        server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())

                import asyncio
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, sync_send)
                logger.info(f"Email sent via SMTP to {to_email}")
                return True
            except Exception as e:
                logger.error(f"SMTP Fallback failed: {e}")

        return False

    # ─── SMS (Twilio) ─────────────────────────────────────────────────────────

    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send an SMS via Twilio."""
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio not configured. Skipping SMS.")
            return False
        
        try:
            from twilio.rest import Client
            import asyncio
            
            def sync_sms():
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                from_num = settings.TWILIO_PHONE_NUMBER or "+1234567890"
                client.messages.create(
                    body=message,
                    from_=from_num,
                    to=to_phone.strip()
                )

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sync_sms)
            logger.info(f"SMS sent via Twilio to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return False
