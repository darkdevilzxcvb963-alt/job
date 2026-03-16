# How to Run the Project - Quick Start Guide

## 🚀 Quick Start (Recommended)

### Option 1: Continuous Mode (Auto-Restart on Crash)

This is the **recommended way** to run the project. Services will automatically restart if they crash.

```powershell
.\start-all-continuous.ps1
```

This will:
- Open 2 new PowerShell windows
- Start the backend (port 8000) with auto-restart
- Start the frontend (port 3000) with auto-restart
- Keep both running continuously

### Option 2: Manual Start (Both in Separate Windows)

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## 🔐 Login Credentials

Default test accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@example.com` | `Admin@1234` |
| Candidate | `candidate@example.com` | `Test@1234` |
| Recruiter | `recruiter@example.com` | `Test@1234` |

Or **sign up** at http://localhost:3000/signup to create a new account.

---

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |

---

## ✅ Verify Everything Works

1. Open http://localhost:3000 in your browser
2. Click "Login"
3. Use credentials above to login
4. You should see your dashboard

---

## 🛠️ Manual Setup (if needed)

### Backend Setup

```powershell
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download SpaCy model
python -m spacy download en_core_web_sm

# Run migrations (optional)
# alembic upgrade head

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```powershell
cd frontend

# Install dependencies (if not done)
npm install

# Start dev server
npm run dev
```

---

## 🐛 Troubleshooting

### Backend keeps stopping?
- The project now has auto-restart capability
- Use `start-all-continuous.ps1` which handles crashes gracefully
- Check logs in the terminal for error messages

### Port 8000 already in use?
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Port 3000 already in use?
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Database issues?
The SQLite database will auto-initialize on first run. If issues occur:
```powershell
# Delete and recreate database
Remove-Item backend\resume_matching.db
# Restart backend - it will recreate the database
```

---

## 📝 Project Structure

```
new-project/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── main.py       # Entry point
│   ├── venv/             # Virtual environment
│   └── requirements.txt   # Dependencies
├── frontend/              # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## ✨ Features

- **User Authentication** - Sign up, login, password reset
- **Admin Panel** - Manage users and verify recruiters
- **Resume Matching** - Upload resume and find matching jobs
- **Job Posting** - Post jobs and find matching candidates
- **Real-time API** - Interactive API documentation at /docs
- **Auto-restart** - Services stay running even if they crash

---

## 📞 Support

For issues:
1. Check the terminal logs for error messages
2. Ensure both ports (3000, 8000) are available
3. Try deleting the SQLite database and restarting
4. Check that node_modules and venv are properly installed

---

**Happy coding! 🎉**
