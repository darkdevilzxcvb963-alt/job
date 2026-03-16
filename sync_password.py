import sqlite3
import sqlalchemy
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email == 'uuid@test.com').first()
if user:
    user.hashed_password = get_password_hash("TestPassword123")
    db.commit()
    print("Updated uuid@test.com password to TestPassword123")
else:
    print("User uuid@test.com not found")
db.close()
