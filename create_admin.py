"""
Simple Admin Account Setup Tool
Creates a new admin account directly in the database
"""
import sqlite3
from pathlib import Path
from datetime import datetime

def hash_password(password):
    """Hash password using bcrypt"""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except ImportError:
        # Fallback to simple hash (not recommended for production)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def create_admin_account():
    """Create or reset admin account"""
    print("=" * 60)
    print("ADMIN ACCOUNT SETUP")
    print("=" * 60)
    
    # Get admin details
    print("\nEnter admin account details:")
    email = input("Email (press Enter for 'admin@example.com'): ").strip()
    if not email:
        email = "admin@example.com"
    
    full_name = input("Full Name (press Enter for 'Admin User'): ").strip()
    if not full_name:
        full_name = "Admin User"
    
    password = input("Password (min 8 characters): ").strip()
    
    if len(password) < 8:
        print("\n❌ Error: Password must be at least 8 characters!")
        return
    
    # Connect to database
    db_path = Path(__file__).parent / 'backend' / 'resume_matching.db'
    if not db_path.exists():
        # Try alternative path
        db_path = Path(__file__).parent / 'resume_matching.db'
        if not db_path.exists():
            print(f"\n❌ Error: Database not found!")
            print(f"Searched: {db_path}")
            return
    
    print(f"\n📁 Using database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id, role FROM users WHERE email = ?", (email,))
    existing = cursor.fetchone()
    
    # Hash password
    hashed_password = hash_password(password)
    now = datetime.utcnow()
    
    if existing:
        user_id, current_role = existing
        print(f"\n⚠️  User {email} already exists with role: {current_role}")
        
        # Update to admin and reset password
        cursor.execute("""
            UPDATE users 
            SET role = 'admin', 
                hashed_password = ?,
                full_name = ?,
                is_verified = 1,
                is_active = 1,
                verification_token = NULL,
                verification_token_expires = NULL,
                updated_at = ?
            WHERE email = ?
        """, (hashed_password, full_name, now, email))
        
        conn.commit()
        print(f"✅ Updated {email} to admin role and reset password!")
    else:
        # Create new admin user
        import uuid
        user_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO users (
                id, email, full_name, hashed_password, role, 
                is_verified, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'admin', 1, 1, ?, ?)
        """, (user_id, email, full_name, hashed_password, now, now))
        
        conn.commit()
        print(f"✅ Created new admin account: {email}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("ADMIN ACCOUNT READY!")
    print("=" * 60)
    print(f"📧 Email:    {email}")
    print(f"🔑 Password: {password}")
    print(f"👑 Role:     admin")
    print("\n🌐 Login URL: http://127.0.0.1:3000/login")
    print("🛡️  Admin Panel: http://127.0.0.1:3000/admin")
    print("=" * 60)
    print("\nℹ️  Note: The password is hashed in the database for security.")

if __name__ == "__main__":
    try:
        create_admin_account()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
