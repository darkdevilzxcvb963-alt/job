
from app.core.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User

def check_notifications(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found.")
            return
        
        notifs = db.query(Notification).filter(Notification.user_id == user.id).all()
        print(f"Total Notifications for {email}: {len(notifs)}")
        for n in notifs:
            print(f"  [{n.created_at}] Type={n.type}, Status={n.status}, Read={n.is_read}")
            print(f"    Content: {n.content[:100]}...")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_notifications("appleballcatdog54321@gmail.com")
