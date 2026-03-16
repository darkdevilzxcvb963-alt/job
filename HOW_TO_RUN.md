# How to Run the Project

## 🚀 Quick Start (Easiest Method)

### Using Docker (Recommended)

1. **Open PowerShell in the project directory**
   ```powershell
   cd C:\Users\ADMIN\new-project
   ```

2. **Run the start script**
   ```powershell
   .\start-all.ps1
   ```

   This script will:
   - Check if Docker is installed
   - Create `.env` file if needed
   - Start all services (database, backend, frontend)
   - Run database migrations

3. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

---

## 📋 Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL 15+ installed and running
- Git (optional)

### Step 1: Backend Setup

1. **Navigate to backend directory**
   ```powershell
   cd backend
   ```

2. **Create virtual environment** (if not exists)
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Download SpaCy model**
   ```powershell
   python -m spacy download en_core_web_sm
   ```

6. **Create `.env` file** in `backend/` directory:
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/resume_matching_db
   
   # Security
   SECRET_KEY=your-secret-key-here-change-in-production
   
   # OpenAI (optional, for LLM features)
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Email Configuration (optional, for email verification)
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_FROM=noreply@resumematching.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com
   
   # Frontend URL
   FRONTEND_URL=http://localhost:3000
   ```

7. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE resume_matching_db;
   ```

8. **Run database migrations**
   ```powershell
   alembic upgrade head
   ```

9. **Start the backend server**
   ```powershell
   uvicorn app.main:app --reload
   ```

   Backend will run on: http://localhost:8000

### Step 2: Frontend Setup

1. **Open a NEW terminal/PowerShell window**

2. **Navigate to frontend directory**
   ```powershell
   cd frontend
   ```

3. **Install dependencies** (if not already installed)
   ```powershell
   npm install
   ```

4. **Start the development server**
   ```powershell
   npm run dev
   ```

   Frontend will run on: http://localhost:3000 (or the port shown in terminal)

---

## 🎯 Using the Application

### First Time Setup

1. **Sign Up**
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Choose your role (Job Seeker or Recruiter)
   - Fill in your details
   - Check your email for verification link

2. **Verify Email**
   - Click the verification link in your email
   - Or go to http://localhost:3000/verify-email?token=YOUR_TOKEN

3. **Login**
   - Use your email and password to login
   - You'll be redirected to your dashboard based on your role

### For Job Seekers

1. Go to **Dashboard** (http://localhost:3000/candidate)
2. Fill in your personal information
3. Upload your resume (PDF or DOCX)
4. Click "Create Profile"
5. View your matches at **Matches** page

### For Recruiters

1. Go to **Post Jobs** (http://localhost:3000/jobs)
2. Fill in job details
3. Add required skills
4. Click "Post Job"
5. View candidate matches at **Matches** page

---

## 🛠️ Troubleshooting

### Backend Issues

**Port 8000 already in use?**
```powershell
# Find and kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in backend/app/main.py
```

**Database connection error?**
- Make sure PostgreSQL is running
- Check DATABASE_URL in `.env` file
- Verify database exists: `psql -U user -d resume_matching_db`

**Module not found errors?**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

**Migration errors?**
```powershell
# Reset migrations (WARNING: This will delete data)
alembic downgrade base
alembic upgrade head
```

### Frontend Issues

**Port 3000 already in use?**
- Vite will automatically use the next available port (3001, 3002, etc.)
- Or change port in `vite.config.js`

**npm install fails?**
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

**API connection errors?**
- Make sure backend is running on http://localhost:8000
- Check `VITE_API_URL` in `.env` file (if exists)
- Check browser console for CORS errors

### Docker Issues

**Docker not starting?**
```powershell
# Check Docker Desktop is running
docker ps

# View logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

**Database migration in Docker?**
```powershell
docker-compose exec backend alembic upgrade head
```

---

## 📝 Environment Variables

### Required (Minimum)
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Secret key for JWT tokens

### Optional but Recommended
- `OPENAI_API_KEY` - For LLM features (resume summaries, match explanations)
- `MAIL_USERNAME` - For email verification
- `MAIL_PASSWORD` - For email verification
- `FRONTEND_URL` - For email links

---

## 🎨 Development Commands

### Backend
```powershell
# Run with auto-reload
uvicorn app.main:app --reload

# Run on specific port
uvicorn app.main:app --port 8001

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Frontend
```powershell
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 🔄 Restart Services

### With Docker
```powershell
docker-compose restart
# Or
docker-compose down
docker-compose up -d
```

### Manual
- **Backend**: Stop (Ctrl+C) and restart `uvicorn app.main:app --reload`
- **Frontend**: Stop (Ctrl+C) and restart `npm run dev`

---

## ✅ Verify Everything is Working

1. **Backend Health Check**
   - Visit: http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. **API Documentation**
   - Visit: http://localhost:8000/docs
   - Should show Swagger UI with all endpoints

3. **Frontend**
   - Visit: http://localhost:3000
   - Should show the home page

4. **Database**
   - Check PostgreSQL is running
   - Tables should be created after migration

---

## 🆘 Need Help?

- Check the logs:
  - Backend: Look at terminal output
  - Frontend: Check browser console (F12)
  - Docker: `docker-compose logs -f`

- Common issues:
  - Make sure all dependencies are installed
  - Check environment variables are set correctly
  - Verify database is accessible
  - Ensure ports are not blocked by firewall

---

## 🎉 Success!

If everything is running:
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:3000
- ✅ API Docs: http://localhost:8000/docs

You're ready to use the AI-Powered Resume & Job Matching Platform!
