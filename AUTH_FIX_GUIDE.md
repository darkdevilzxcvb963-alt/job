# Authentication Fix Guide

## Issues Fixed

### 1. Phone Validation
- Fixed phone field validation to handle empty/null values
- Phone is now truly optional

### 2. Email Verification
- Auto-verifies users if email is not configured (development mode)
- Users can login immediately after signup if email is not set up

### 3. API URL
- Changed from `127.0.0.1` to `localhost` for better compatibility

### 4. Error Handling
- Improved error messages in frontend
- Better error logging

### 5. Simplified Alternative
- Created `/auth-simple` endpoints that skip email verification
- Created `api-simple.js` for frontend to use simplified auth

---

## How to Use the Fixes

### Option 1: Use Fixed Main Auth (Recommended)

The main auth endpoints have been fixed. Just restart your backend:

```powershell
# Backend should auto-verify users if email is not configured
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Features:**
- Auto-verifies users if email is not configured
- Better phone validation
- Improved error handling

### Option 2: Use Simplified Auth (If Main Auth Still Has Issues)

1. **Update frontend to use simplified auth:**

Edit `frontend/src/contexts/AuthContext.jsx`:

Change this line:
```javascript
import { login, signup, logout, getCurrentUser, verifyEmail, forgotPassword, resetPassword } from '../services/api'
```

To:
```javascript
import { login, signup, logout, getCurrentUser } from '../services/api-simple'
import { verifyEmail, forgotPassword, resetPassword } from '../services/api'
```

2. **Restart frontend:**
```powershell
cd frontend
npm run dev
```

**Features:**
- No email verification required
- Immediate access after signup
- Simpler flow for development

---

## Testing the Fix

### Test Signup

1. Go to http://localhost:3000/signup
2. Fill in:
   - Full Name: Test User
   - Email: test@example.com
   - Password: Test1234 (must have letters and numbers)
   - Role: Job Seeker or Recruiter
3. Click "Sign Up"
4. Should see success message

### Test Login

1. Go to http://localhost:3000/login
2. Use the email and password you just created
3. Should login successfully and redirect to dashboard

---

## Common Issues and Solutions

### Issue: "User with this email already exists"
**Solution:** Use a different email or delete the existing user from database

### Issue: "Password must contain at least one digit"
**Solution:** Password must have both letters and numbers (e.g., "Test1234")

### Issue: "Incorrect email or password"
**Solution:** 
- Check email is correct
- Check password is correct
- Make sure user exists in database

### Issue: CORS errors
**Solution:** 
- Make sure backend is running on port 8000
- Check `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`

### Issue: Database errors
**Solution:**
- Make sure PostgreSQL is running
- Run migrations: `alembic upgrade head`
- Check `DATABASE_URL` in `.env`

---

## Manual Database Check

If signup/login still fails, check the database:

```sql
-- Connect to database
psql -U user -d resume_matching_db

-- Check users table
SELECT id, email, full_name, role, is_verified, is_active FROM users;

-- Delete test user if needed
DELETE FROM users WHERE email = 'test@example.com';
```

---

## Quick Test Script

Create a test user directly in database:

```sql
-- This will create a test user (password: Test1234)
-- You'll need to hash the password first using Python

-- Or use this Python script:
```

```python
# test_user.py
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.core.database import SessionLocal

db = SessionLocal()
hashed = get_password_hash("Test1234")

user = User(
    full_name="Test User",
    email="test@example.com",
    hashed_password=hashed,
    role=UserRole.JOB_SEEKER,
    is_verified=True,
    is_active=True
)

db.add(user)
db.commit()
print(f"User created: {user.email}")
```

---

## Still Having Issues?

1. **Check backend logs** for error messages
2. **Check browser console** (F12) for frontend errors
3. **Verify database** has auth tables (users, password_resets, user_sessions)
4. **Test API directly** at http://localhost:8000/docs

The simplified auth endpoints are available at:
- POST `/api/v1/auth-simple/signup`
- POST `/api/v1/auth-simple/login`

These skip all email verification and work immediately!
