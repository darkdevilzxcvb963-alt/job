import asyncio
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

async def test_email():
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_FROM=os.getenv('MAIL_FROM'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
        MAIL_STARTTLS=os.getenv('MAIL_TLS', 'True').lower() == 'true',
        MAIL_SSL_TLS=os.getenv('MAIL_SSL', 'False').lower() == 'true',
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

    print(f"Testing email with config:")
    print(f"Server: {conf.MAIL_SERVER}:{conf.MAIL_PORT}")
    print(f"Username: {conf.MAIL_USERNAME}")
    print(f"From: {conf.MAIL_FROM}")
    print(f"TLS: {conf.MAIL_STARTTLS}")
    print(f"SSL: {conf.MAIL_SSL_TLS}")

    fm = FastMail(conf)
    
    message = MessageSchema(
        subject="Email Test - Resume Matching Platform",
        recipients=[conf.MAIL_FROM], # Send to self
        body="This is a test email to verify the configuration.",
        subtype=MessageType.plain
    )

    try:
        await fm.send_message(message)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_email())
