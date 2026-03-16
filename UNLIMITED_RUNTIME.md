# 🚀 How to Run the Application Indefinitely

This guide explains how to start the Resume Matching Platform with unlimited runtime (not just 60 seconds).

## Quick Start (Recommended)

### Option 1: PowerShell Script (Best)
```powershell
# Navigate to project root and run:
.\start-services.ps1
```

**This will:**
- ✅ Start backend on `http://127.0.0.1:8000`
- ✅ Start frontend on `http://localhost:3000`
- ✅ Open browser automatically
- ✅ Run indefinitely in separate windows

### Option 2: Batch Script (Windows Only)
```cmd
start-services.bat
```

Same features as PowerShell script.

### Option 3: Manual Startup (Two Terminal Windows)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\ADMIN\new-project\backend
.\venv\Scripts\activate
python run_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\ADMIN\new-project\frontend
npm run dev
```

---

## ⚡ Key Improvements Made

### Backend Optimization
- **Lazy Loading**: NLP models now load only when needed, not at startup
- **Fast Startup**: Backend starts in seconds, not minutes
- **Unlimited Runtime**: `run_server.py` script handles Windows asyncio properly

### Frontend
- Runs indefinitely with `npm run dev`
- Hot-reload enabled for development
- Properly configured to communicate with backend at `http://127.0.0.1:8000`

---

## 🧪 Testing the Full Flow

Once both servers are running:

1. **Access the Application:**
   - Frontend: http://localhost:3000
   - API Docs: http://127.0.0.1:8000/docs

2. **Create an Account:**
   - Go to signup page
   - Enter: Email, Password, Full Name
   - Account is auto-verified (no email needed)

3. **Login:**
   - Use your email and password
   - Should redirect to dashboard based on role:
     - Job Seeker → `/candidate` dashboard
     - Recruiter → `/jobs` dashboard

4. **Test API Directly:**
   ```bash
   # Signup
   curl -X POST "http://127.0.0.1:8000/api/v1/auth-simple/signup" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test@1234","full_name":"John Smith","confirm_password":"Test@1234"}'
   
   # Login
   curl -X POST "http://127.0.0.1:8000/api/v1/auth-simple/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test@1234"}'
   ```

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + Vite)                │
│  http://localhost:3000                   │
│  - Signup/Login pages                    │
│  - Candidate/Recruiter dashboards        │
└─────────────┬───────────────────────────┘
              │ (Axios HTTP requests)
              │ http://127.0.0.1:8000/api/v1
              ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI)                      │
│  http://127.0.0.1:8000                   │
│  - User authentication                   │
│  - Job management                        │
│  - Resume parsing                        │
│  - AI matching engine                    │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Database (SQLite)                      │
│  resume_matching.db                      │
│  - Users, Jobs, Candidates               │
│  - Matches, Sessions                     │
└─────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Backend won't start
- **Solution**: Delete `resume_matching.db` and restart
  ```powershell
  cd backend
  Remove-Item resume_matching.db -Force -ErrorAction SilentlyContinue
  python run_server.py
  ```

### Frontend won't connect to backend
- **Verify**: Backend is running on http://127.0.0.1:8000 (NOT localhost)
- **Check**: Frontend API URL in `frontend/src/services/api.js` is set to `http://127.0.0.1:8000/api/v1`

### Port already in use
- **Backend (8000)**:
  ```powershell
  # Find and kill process on port 8000
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```
- **Frontend (3000)**:
  ```powershell
  # Find and kill process on port 3000
  netstat -ano | findstr :3000
  taskkill /PID <PID> /F
  ```

### NLP Models Taking Too Long
- Models now load on-demand (first API request)
- Backend starts instantly
- First skill extraction request will take ~30 seconds as models load
- Subsequent requests are instant

---

## 📝 Default Test Credentials

Use these after signup:
- **Email**: any valid email (e.g., `user@example.com`)
- **Password**: Must be strong (uppercase, lowercase, number, special char)
- **Example**: `MyPassword@123`

Auto-verified - no email confirmation needed!

---

## 🎯 Endpoints Reference

### Authentication
- `POST /api/v1/auth-simple/signup` - Create account
- `POST /api/v1/auth-simple/login` - Login (returns user data with role)
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Candidates
- `POST /api/v1/candidates` - Create candidate profile
- `GET /api/v1/candidates` - List candidates
- `PUT /api/v1/candidates/{id}` - Update profile

### Jobs
- `POST /api/v1/jobs` - Create job posting
- `GET /api/v1/jobs` - List jobs
- `PUT /api/v1/jobs/{id}` - Update job

### Matching
- `POST /api/v1/matches` - Create match
- `GET /api/v1/matches/candidate/{candidate_id}` - Get candidate matches
- `GET /api/v1/matches/job/{job_id}` - Get job matches

---

## ✅ Status Check

Run this to verify everything is working:

```powershell
# Check backend
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -UseBasicParsing).StatusCode

# Check frontend  
(Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing).StatusCode

# Both should return 200
```

---

## 🛑 Stopping Services

- **Backend**: Close the backend terminal window or press `Ctrl+C`
- **Frontend**: Close the frontend terminal window or press `Ctrl+C`

Both services will stop cleanly without leaving processes running.
