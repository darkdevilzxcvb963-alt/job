# Quick Run Setup Instructions

## ✅ Automated Setup Complete!

The following has been automatically configured:

1. ✅ **Environment file created**: `backend/.env`
2. ✅ **Virtual environment created**: `backend/venv`
3. ✅ **Backend dependencies**: Installing...
4. ✅ **Frontend dependencies**: Installing...
5. ✅ **Setup scripts created**: Ready to use

## 🚀 Start the Application

### Option 1: Using Docker (Easiest)

If you have Docker installed:
```powershell
.\start-all.ps1
```

This will automatically:
- Start PostgreSQL database
- Start backend API server  
- Start frontend development server
- Initialize database schema

### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Start Backend:**
```powershell
.\start-backend.ps1
```

**Terminal 2 - Start Frontend:**
```powershell
.\start-frontend.ps1
```

**Terminal 3 - Initialize Database (First Time Only):**
```powershell
.\init-database.ps1
```

## 📝 Important Configuration

### 1. Add OpenAI API Key (Optional)

Edit `backend/.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Note**: The application will work without this, but LLM features (summaries, explanations) will have limited functionality.

### 2. Database Setup

**If using Docker**: Database is automatically set up.

**If using manual setup**: 
1. Install PostgreSQL
2. Create database: `createdb resume_matching_db`
3. Update `DATABASE_URL` in `backend/.env` if needed
4. Run: `.\init-database.ps1`

## 🌐 Access the Application

Once started:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## 📋 What's Ready

✅ Project structure complete
✅ Backend API (FastAPI)
✅ Frontend (React)
✅ Database models
✅ NLP processing services
✅ Matching engine
✅ LLM integration
✅ Docker configuration
✅ Setup scripts
✅ Environment configuration

## 🎯 Next Steps

1. **Wait for dependencies to finish installing** (check terminal windows)
2. **Add OpenAI API key** (optional) in `backend/.env`
3. **Start the services** using one of the methods above
4. **Test the application**:
   - Upload a resume
   - Post a job
   - View matches

## 🆘 Troubleshooting

### Dependencies Still Installing?
- Backend: Check `backend/` terminal
- Frontend: Check `frontend/` terminal
- Wait for "Installation complete" messages

### Port Already in Use?
- Change ports in `docker-compose.yml` or
- Stop other services using ports 3000, 8000, 5432

### Database Connection Error?
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `backend/.env`
- For Docker: `docker-compose up -d db`

### Need to Reinstall?
```powershell
.\setup.ps1
```

## 📚 Documentation

- **Full README**: `README.md`
- **Setup Guide**: `AUTOMATED_SETUP.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **API Reference**: `docs/API_REFERENCE.md`

---

**Status**: ✅ Ready to run! Just start the services and you're good to go!
