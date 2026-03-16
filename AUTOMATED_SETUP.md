# Automated Setup Guide

This project includes automated setup scripts to get you running quickly.

## Quick Setup (Recommended)

### Option 1: Automated PowerShell Script (Windows)

Simply run:
```powershell
.\setup.ps1
```

This script will:
- ✓ Check for Python and Node.js
- ✓ Create Python virtual environment
- ✓ Install all backend dependencies
- ✓ Download SpaCy NLP model
- ✓ Install all frontend dependencies
- ✓ Create configuration files
- ✓ Set up directory structure

### Option 2: Python Setup Script (Cross-platform)

Run:
```bash
python setup.py
```

### Option 3: Docker Compose (Easiest)

If you have Docker installed:
```powershell
.\start-all.ps1
```

Or manually:
```bash
docker-compose up -d
```

## Starting the Application

### Using Docker (Recommended)

```powershell
.\start-all.ps1
```

This will:
- Start PostgreSQL database
- Start backend API server
- Start frontend development server
- Initialize database schema

### Manual Start

**Terminal 1 - Backend:**
```powershell
.\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\start-frontend.ps1
```

**Terminal 3 - Initialize Database (first time only):**
```powershell
.\init-database.ps1
```

## Configuration

### Environment Variables

The `.env` file has been created automatically. You may want to edit `backend/.env`:

1. **OpenAI API Key** (optional, for LLM features):
   ```
   OPENAI_API_KEY=your-actual-api-key-here
   ```

2. **Database URL** (if using custom PostgreSQL):
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

3. **Secret Key** (change in production):
   ```
   SECRET_KEY=your-secure-random-secret-key
   ```

## Access the Application

After starting:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Port Already in Use
Change ports in:
- `docker-compose.yml` (for Docker)
- `frontend/vite.config.js` (for frontend)
- `backend/app/main.py` (for backend)

### Database Connection Error
1. Ensure PostgreSQL is running
2. Check `DATABASE_URL` in `backend/.env`
3. Create database: `createdb resume_matching_db`

### Missing Dependencies
Run setup again:
```powershell
.\setup.ps1
```

### Virtual Environment Issues
Delete and recreate:
```powershell
cd backend
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## What's Been Set Up

✅ Python virtual environment
✅ All Python dependencies installed
✅ SpaCy NLP model downloaded
✅ Node.js dependencies installed
✅ Environment configuration files created
✅ Database migration files ready
✅ Docker configuration ready
✅ Startup scripts created

## Next Steps

1. **Add OpenAI API Key** (optional) in `backend/.env`
2. **Start the services** using one of the methods above
3. **Initialize database** (if not using Docker):
   ```powershell
   .\init-database.ps1
   ```
4. **Test the application**:
   - Upload a resume at http://localhost:3000/candidate
   - Post a job at http://localhost:3000/jobs
   - View matches at http://localhost:3000/matches

## Scripts Available

- `setup.ps1` - Full automated setup
- `setup.py` - Cross-platform Python setup
- `start-all.ps1` - Start all services with Docker
- `start-backend.ps1` - Start backend server only
- `start-frontend.ps1` - Start frontend server only
- `init-database.ps1` - Initialize database schema

Enjoy your AI-Powered Resume & Job Matching Platform! 🚀
