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

    async def _send_brevo_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Internal helper to send email via Brevo (Sendinblue) HTTP API."""
        if not settings.BREVO_API_KEY:
            return False

        url = "https://api.brevo.com/v3/smtp/email"
        
        payload = {
            "sender": {
                "name": settings.MAIL_FROM_NAME,
                "email": settings.MAIL_FROM
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "htmlContent": html_body
        }

        try:
            headers = {
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                if response.status_code >= 400:
                    logger.error(f"Brevo Error {response.status_code}: {response.text}")
                    return False
                logger.info(f"Email sent via Brevo to {to_email}")
                return True
        except Exception as e:
            logger.error(f"Brevo API request failed: {e}")
            return False

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
        """Send an HTML email via Brevo API (1st) → Mailjet API (2nd) → Gmail SMTP (3rd)."""
        
        # 1. Try Brevo (Most reliable for new accounts)
        if settings.BREVO_API_KEY:
            try:
                if await self._send_brevo_email(to_email, subject, html_body):
                    return True
            except Exception as e:
                logger.error(f"❌ Brevo API failed for {to_email}: {str(e)}")

        # 2. Try Mailjet (2nd choice)
        if settings.MAILJET_API_KEY and settings.MAILJET_SECRET_KEY:
            try:
                if await self._send_mailjet_email(to_email, subject, html_body):
                    return True
            except Exception as e:
                logger.error(f"❌ Mailjet API failed for {to_email}: {str(e)}")

        # 3. Try Gmail SMTP (Fallback - likely to be blocked on Render)
        if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
            try:
                import aiosmtplib
                from email.message import EmailMessage
                
                from_addr = settings.MAIL_USERNAME if "gmail" in settings.MAIL_SERVER.lower() else settings.MAIL_FROM
                
                message = EmailMessage()
                message["From"] = f"{settings.MAIL_FROM_NAME} <{from_addr}>"
                message["To"] = to_email
                message["Subject"] = subject
                message.set_content("Please enable HTML to view this message.")
                message.add_alternative(html_body, subtype="html")

                smtp_options = {
                    "hostname": settings.MAIL_SERVER,
                    "port": settings.MAIL_PORT,
                    "use_tls": settings.MAIL_SSL,
                    "start_tls": settings.MAIL_TLS or (settings.MAIL_PORT == 587),
                    "timeout": 15
                }

                await aiosmtplib.send(
                    message,
                    username=settings.MAIL_USERNAME,
                    password=settings.MAIL_PASSWORD,
                    **smtp_options
                )
                
                logger.info(f"✅ Email delivered via aiosmtplib to {to_email}")
                return True
            except Exception as e:
                logger.error(f"❌ SMTP also failed for {to_email}: {str(e)}")

        logger.error(f"❌ ALL email providers failed for {to_email}")
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

    # ─── Push Notifications (Stub) ──────────────────────────────────────────────
    async def send_push_notification(self, user_id: str, title: str, message: str) -> bool:
        """Stub for push notifications (Firebase/OneSignal). Currently just logged."""
        logger.info(f"📣 PUSH NOTIFICATION [User: {user_id}]: {title} - {message}")
        return True

    # ─── Application Event Notifications ────────────────────────────────────────

    async def notify_recruiter_of_application(
        self,
        recruiter_email: str,
        recruiter_name: str,
        candidate_name: str,
        job_title: str,
        company: str,
        cover_letter: str = "",
        recruiter_phone: str = ""
    ) -> bool:
        """Notify recruiter when a candidate applies to their job."""
        subject = f"🚀 New Application: {candidate_name} for {job_title}"
        
        html_body = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 25px; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; line-height: 1.6;">
            <div style="text-align: center; margin-bottom: 25px;">
                <h2 style="color: #2563eb; margin-bottom: 5px;">New Application Received</h2>
                <p style="color: #64748b; font-size: 14px;">Resume Matching Platform</p>
            </div>
            
            <p>Hello <strong>{recruiter_name}</strong>,</p>
            <p>Good news! <strong>{candidate_name}</strong> has just applied for your position:</p>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb;">
                <p style="margin: 0; font-size: 18px; font-weight: bold; color: #1e293b;">{job_title}</p>
                <p style="margin: 5px 0 0 0; color: #64748b;">{company}</p>
            </div>
            
            {f'<div style="background: #fff; padding: 15px; border: 1px dashed #cbd5e1; border-radius: 8px; margin: 20px 0;"><strong>Cover Letter Snippet:</strong><br/><i style="color: #475569;">"{cover_letter[:300]}..."</i></div>' if cover_letter else ""}
            
            <p>You can view the candidate's full profile, AI-match score, and resume in your dashboard.</p>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{settings.FRONTEND_URL}/recruiter/dashboard" style="background: #2563eb; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Review Application</a>
            </div>
            
            <p style="font-size: 12px; color: #94a3b8; margin-top: 40px; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 20px;">
                &copy; 2026 Resume Matching Platform. All rights reserved.
            </p>
        </div>
        """
        
        # Send Email
        email_sent = await self.send_email(recruiter_email, subject, html_body)
        
        # Send SMS (Optional)
        if recruiter_phone and recruiter_phone.strip():
            sms_msg = f"New App: {candidate_name} applied for '{job_title}'. Log in to review."
            await self.send_sms(recruiter_phone, sms_msg)
            
        return email_sent

    async def notify_candidate_of_application(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        company: str
    ) -> bool:
        """Confirmation email to the candidate after applying."""
        subject = f"✅ Application Sent: {job_title} at {company}"
        
        html_body = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 25px; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; line-height: 1.6;">
            <div style="text-align: center; margin-bottom: 25px;">
                <h2 style="color: #10b981; margin-bottom: 5px;">Application Confirmed</h2>
                <p style="color: #64748b; font-size: 14px;">Resume Matching Platform</p>
            </div>
            
            <p>Hello <strong>{candidate_name}</strong>,</p>
            <p>Your application for <strong>{job_title}</strong> at <strong>{company}</strong> has been successfully submitted.</p>
            
            <p>What happens next?</p>
            <ul style="color: #475569;">
                <li>The recruiter will review your profile and AI-match score.</li>
                <li>If there's a good fit, they will contact you directly via the platform.</li>
                <li>You can track the status of your application in your dashboard.</li>
            </ul>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{settings.FRONTEND_URL}/dashboard" style="background: #10b981; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Track My Applications</a>
            </div>
            
            <p style="font-size: 12px; color: #94a3b8; margin-top: 40px; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 20px;">
                Good luck with your application!
            </p>
        </div>
        """
        
        return await self.send_email(candidate_email, subject, html_body)

    async def notify_interview_scheduled(
        self,
        email: str,
        name: str,
        job_title: str,
        company: str,
        date_time: str,
        location: str = "Virtual"
    ) -> bool:
        """Notify user when an interview is scheduled."""
        subject = f"🗓️ Interview Scheduled: {job_title}"
        
        html_body = f"""
        <div style="font-family: sans-serif; padding: 25px; border: 1px solid #e2e8f0; border-radius: 12px;">
            <h2 style="color: #2563eb;">Interview Details</h2>
            <p>Hello {name},</p>
            <p>An interview has been scheduled for the <strong>{job_title}</strong> role at <strong>{company}</strong>.</p>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Date & Time:</strong> {date_time}</p>
                <p><strong>Location/Link:</strong> {location}</p>
            </div>
            
            <p>Please make sure to be available 5 minutes before the scheduled time.</p>
            <a href="{settings.FRONTEND_URL}/interviews" style="background: #2563eb; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; display: inline-block;">View in Calendar</a>
        </div>
        """
        
        return await self.send_email(email, subject, html_body)
