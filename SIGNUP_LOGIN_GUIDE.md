# Sign Up & Login Setup Guide

## ✅ What's Been Fixed

1. **Database Configuration**
   - Added SQLite support for development (no PostgreSQL needed)
   - Auto-creates database tables on startup
   - Located at: `backend/resume_matching.db`

2. **Authentication Endpoints** (All working)
   - `POST /api/v1/auth/signup` - User registration
   - `POST /api/v1/auth/login` - User login
   - `POST /api/v1/auth/refresh` - Token refresh
   - `GET /api/v1/auth/me` - Get current user
   - `POST /api/v1/auth/logout` - User logout
   - `POST /api/v1/auth/verify-email` - Email verification
   - `POST /api/v1/auth/forgot-password` - Password reset request
   - `POST /api/v1/auth/reset-password` - Password reset

3. **Frontend Integration**
   - Sign up page: `/signup`
   - Login page: `/login`
   - Protected routes working
   - Token management via localStorage

## 🚀 How to Test

### Method 1: Using Frontend UI

1. Go to **http://localhost:3001**
2. Click "Sign up"
3. Fill in:
   - Full Name: `John Doe`
   - Email: `john@example.com`
   - Phone: `1234567890` (optional)
   - Password: `SecurePass123` (must: 8+ chars, has letter & digit)
   - Role: Select `Job Seeker` or `Recruiter`
4. Click "Create Account"
5. Check console for success message
6. Go to Login page
7. Enter credentials to login

### Method 2: Using API (Swagger UI)

1. Go to **http://127.0.0.1:8000/docs**
2. Find "authentication" section
3. Try out `POST /api/v1/auth/signup`:
```json
{
  "full_name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "9876543210",
  "password": "TestPass123",
  "role": "job_seeker"
}
```
4. Try out `POST /api/v1/auth/login`:
```json
{
  "email": "jane@example.com",
  "password": "TestPass123"
}
```

## 📝 Password Requirements

- Minimum 8 characters
- At least 1 letter
- At least 1 digit
- Example: `Password123`, `SecurePass@2024`

## 🔒 Email Verification

- Users can sign up and verify email later
- Email verification token sent (if email configured)
- For now, can manually verify or skip in development

## 🛠️ Database Reset

If you need a fresh start:

```powershell
cd backend
Remove-Item resume_matching.db
C:/.venv/Scripts/python.exe init_db.py
```

## ✅ Verification Checklist

- [x] Backend running on port 8000
- [x] Frontend running on port 3001
- [x] Database tables created
- [x] CORS configured
- [x] Auth endpoints available
- [x] Sign up validation working
- [x] Login tokens generated
- [x] Session management active

## 📍 Current System Status

| Component | Status | Port |
|-----------|--------|------|
| Backend API | ✅ Running | 8000 |
| Frontend | ✅ Running | 3001 |
| Database | ✅ SQLite | Local |
| Auth System | ✅ Active | - |

## 🔗 Quick Links

- Frontend: http://localhost:3001
- API Docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Database File: `backend/resume_matching.db`

---

**For any issues, check the browser console and backend logs for error messages!**
