from app.core.database import SessionLocal
from app.models.user import User

session = SessionLocal()
users = session.query(User).all()
if not users:
    print('No users found')
else:
    for u in users:
        print(f"id={u.id}, email={u.email}, role={u.role}, is_active={u.is_active}, is_verified={u.is_verified}, hashed_password={u.hashed_password[:20]}...")
session.close()
