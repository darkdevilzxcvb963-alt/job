"""
Notification Service — sends email (SMTP) and SMS (Twilio) notifications.
Gracefully degrades if credentials are not configured.
"""
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from app.core.config import settings


class NotificationService:
    """Handles email, SMS and Push notifications for application events."""

    # ─── OneSignal ────────────────────────────────────────────────────────────

    async def _send_onesignal_request(self, payload: dict) -> bool:
        """Internal helper to send a request to OneSignal REST API."""
        if not settings.ONESIGNAL_APP_ID or not settings.ONESIGNAL_REST_API_KEY:
            logger.warning("OneSignal not configured. Skipping OneSignal request.")
            return False

        url = "https://onesignal.com/api/v1/notifications"
        headers = {
            "Authorization": f"Basic {settings.ONESIGNAL_REST_API_KEY}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload["app_id"] = settings.ONESIGNAL_APP_ID

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                if response.status_code >= 400:
                    logger.error(f"OneSignal Error {response.status_code}: {response.text}")
                    return False
                logger.info(f"OneSignal notification sent: {response.json()}")
                return True
        except Exception as e:
            logger.error(f"OneSignal API request failed: {e}")
            return False

    async def send_push_notification(self, user_id: str, title: str, message: str) -> bool:
        """Send a browser/mobile push notification to a specific user base on external_id."""
        payload = {
            "include_external_user_ids": [user_id],
            "headings": {"en": title},
            "contents": {"en": message}
        }
        return await self._send_onesignal_request(payload)

    # ─── Email ────────────────────────────────────────────────────────────────

    async def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an HTML email via OneSignal (preferred) or SMTP fallback."""
        # Try OneSignal first
        if settings.ONESIGNAL_APP_ID and settings.ONESIGNAL_REST_API_KEY:
            payload = {
                "target_channel": "email",
                "include_email_tokens": [to_email.lower().strip()],
                "email_subject": subject,
                "email_body": html_body
            }
            if await self._send_onesignal_request(payload):
                return True

        # Fallback to SMTP
        if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
            logger.warning("Email fallback not configured. Skipping email.")
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            msg["To"] = to_email
            msg.attach(MIMEText(html_body, "html"))

            import asyncio
            import functools

            def sync_send():
                with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10) as server:
                    server.ehlo()
                    if settings.MAIL_TLS:
                        server.starttls()
                    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                    server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sync_send)
            
            logger.info(f"Email sent via SMTP fallback to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send an SMS via OneSignal (preferred) or Twilio fallback."""
        # Try OneSignal first
        if settings.ONESIGNAL_APP_ID and settings.ONESIGNAL_REST_API_KEY:
            payload = {
                "sms_from": settings.TWILIO_PHONE_NUMBER, 
                "include_phone_numbers": [to_phone.strip()],
                "contents": {"en": message}
            }
            if await self._send_onesignal_request(payload):
                return True

        # Fallback to Twilio
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio not configured. Skipping SMS.")
            return False
        if not to_phone or not to_phone.strip():
            logger.warning("No recipient phone number provided. Skipping SMS.")
            return False
        try:
            from twilio.rest import Client
            import asyncio
            
            def sync_sms():
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                # Ensure we have a valid from number
                from_num = settings.TWILIO_PHONE_NUMBER or "+1234567890" # Example fallback
                client.messages.create(
                    body=message,
                    from_=from_num,
                    to=to_phone.strip()
                )

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sync_sms)
            
            logger.info(f"SMS sent via Twilio fallback to {to_phone}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return False

    # ─── Combined recruiter notification ──────────────────────────────────────

    async def notify_recruiter_of_application(
        self,
        recruiter_email: str,
        recruiter_phone: str,
        recruiter_name: str,
        candidate_name: str,
        job_title: str,
        company: str,
        cover_letter: str = ""
    ):
        """Fire off both an email and an SMS to the recruiter when a candidate applies."""

        # --- Email ---
        cover_section = (
            f"<blockquote style='border-left:4px solid #4f46e5;padding:12px 16px;"
            f"background:#f1f0fe;border-radius:4px;margin:16px 0;color:#333;'>"
            f"<strong>Cover Letter:</strong><br>{cover_letter.replace(chr(10),'<br>')}</blockquote>"
            if cover_letter else ""
        )
        email_html = f"""
        <div style="font-family:Inter,Arial,sans-serif;max-width:600px;margin:0 auto;background:#f9f9ff;padding:32px;border-radius:12px;">
          <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:24px;border-radius:10px;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:22px;">🎉 New Application Received!</h1>
          </div>
          <div style="background:#fff;padding:24px;border-radius:10px;margin-top:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <p style="color:#555;font-size:16px;">Hi <strong>{recruiter_name}</strong>,</p>
            <p style="color:#333;font-size:16px;">
              <strong style="color:#4f46e5;">{candidate_name}</strong> has just applied to your
              <strong>{job_title}</strong> position at <strong>{company}</strong>.
            </p>
            {cover_section}
            <p style="color:#555;">Log in to your recruiter dashboard to review the candidate's profile and resume.</p>
            <div style="text-align:center;margin-top:24px;">
              <a href="http://localhost:5173/matches"
                 style="background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:12px 28px;
                        border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;">
                View Application →
              </a>
            </div>
          </div>
          <p style="color:#aaa;font-size:12px;text-align:center;margin-top:20px;">
            Resume Matching Platform · Powered by AI
          </p>
        </div>
        """
        await self.send_email(
            to_email=recruiter_email,
            subject=f"🎯 {candidate_name} applied to {job_title} at {company}",
            html_body=email_html
        )

        # --- SMS ---
        sms_msg = (
            f"[Resume Match] New Application!\n"
            f"{candidate_name} applied to your '{job_title}' role at {company}.\n"
            f"Log in to review: http://localhost:5173/matches"
        )
        await self.send_sms(to_phone=recruiter_phone, message=sms_msg)

    # ─── Candidate notification ───────────────────────────────────────────────
    
    async def notify_candidate_of_application(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        company: str
    ):
        """Send a confirmation email to the candidate when they apply."""
        email_html = f"""
        <div style="font-family:Inter,Arial,sans-serif;max-width:600px;margin:0 auto;background:#f9f9ff;padding:32px;border-radius:12px;">
          <div style="background:linear-gradient(135deg,#6366f1,#a855f7);padding:24px;border-radius:10px;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:22px;">🚀 Application Sent!</h1>
          </div>
          <div style="background:#fff;padding:24px;border-radius:10px;margin-top:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <p style="color:#555;font-size:16px;">Hi <strong>{candidate_name}</strong>,</p>
            <p style="color:#333;font-size:16px;">
              Your application for <strong>{job_title}</strong> at <strong>{company}</strong> has been successfully delivered.
            </p>
            <p style="color:#555;">The recruiter has been notified and will review your profile shortly. You can track your application status in your dashboard.</p>
            <div style="text-align:center;margin-top:24px;">
              <a href="http://localhost:5173/candidate"
                 style="background:linear-gradient(135deg,#6366f1,#a855f7);color:#fff;padding:12px 28px;
                        border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;">
                View My Dashboard →
              </a>
            </div>
          </div>
          <p style="color:#aaa;font-size:12px;text-align:center;margin-top:20px;">
            Resume Matching Platform · Your Career Partner
          </p>
        </div>
        """
        await self.send_email(
            to_email=candidate_email,
            subject=f"✅ Application Confirmed: {job_title} at {company}",
            html_body=email_html
        )
