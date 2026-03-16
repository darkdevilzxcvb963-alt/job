import sys
import os
import enum

class UserRole(str, enum.Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"

def verify_comparison():
    print("Verifying Enum vs String comparison...")
    
    # Simulating what comes from DB (String)
    db_role = "admin"
    
    # Simulating the check in verify_admin_access
    if db_role == UserRole.ADMIN:
        print("✅ String 'admin' EQUALS UserRole.ADMIN")
    else:
        print("❌ String 'admin' DOES NOT EQUAL UserRole.ADMIN")
        print(f"   String: {db_role} ({type(db_role)})")
        print(f"   Enum: {UserRole.ADMIN} ({type(UserRole.ADMIN)})")

    if db_role != UserRole.ADMIN:
        print("⚠️  The check 'if user.role != UserRole.ADMIN' WILL FAIL (block access)")
    else:
        print("✅ The check 'if user.role != UserRole.ADMIN' WILL PASS (allow access)")

if __name__ == "__main__":
    verify_comparison()
