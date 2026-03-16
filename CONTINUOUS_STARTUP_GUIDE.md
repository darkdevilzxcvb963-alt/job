# 🚀 How to Run the Project Continuously

Your project is now set up with **automatic continuous startup** scripts that keep services running without any time limits.

## Method 1: Simple Batch File (Recommended) ⭐

### Windows Users:

1. **Open File Explorer**
2. **Navigate to:** `C:\Users\ADMIN\new-project`
3. **Double-click:** `start-project.bat`
4. **You'll see:**
   - Backend server window opens (minimized)
   - Frontend server window opens (minimized)
   - Both run continuously

### To Stop:
- Close the windows or press `CTRL+C`

---

## Method 2: PowerShell Script

### Windows PowerShell Users:

1. **Open PowerShell** (as Administrator)
2. **Run:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
C:\Users\ADMIN\new-project\start-project.ps1
```

### Features:
- Auto-restarts crashed services
- Monitors both services continuously
- Shows real-time status

---

## Quick Terminal Commands

### If you prefer using terminal:

**Terminal 1 - Backend:**
```bash
cd C:\Users\ADMIN\new-project\backend
.\venv\Scripts\python.exe run_server.py
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\ADMIN\new-project\frontend
npm run dev
```

---

## What You'll See

### Services Starting:
```
[1/2] Starting Backend Server (Port 8000)...
✓ Backend process started

[2/2] Starting Frontend Server (Port 3000)...
✓ Frontend process started

================================
✓ Services Running Successfully!
================================

Backend:  http://localhost:8000
Frontend: http://localhost:3000
```

---

## Access the Application

### Login Credentials:

**Recruiter Account** (See Matches Dashboard):
```
Email:    recruiter@example.com
Password: Recruiter@1234
```

**Job Seeker Account**:
```
Email:    jobseeker@example.com
Password: Jobseeker@1234
```

### URL:
```
http://localhost:3000
(or http://localhost:3001 if 3000 is in use)
```

---

## What's Automated Now

✅ **Both services start together**
✅ **No time limits - runs until you stop it**
✅ **Auto-restarts if either service crashes**
✅ **Clears old processes before starting**
✅ **Keeps running in background**

---

## Features of Automated Matching

Once logged in as recruiter:

1. **Dashboard loads automatically** with all jobs
2. **All matches calculated in parallel** 
3. **Shows overview stats:**
   - Total jobs
   - Total matches
   - % Excellent matches
4. **Expandable job sections** to view candidates
5. **Color-coded scores** (Green/Amber/Red)
6. **AI explanations** for each match

---

## Troubleshooting

### Services not starting?
1. Delete `C:\Users\ADMIN\new-project\backend\resume_matching.db`
2. Run the startup script again

### Port already in use?
- The system auto-detects and uses alternate ports
- Check the output for actual URLs being used

### Frontend showing errors?
```bash
cd C:\Users\ADMIN\new-project\frontend
npm install
npm run dev
```

### Database issues?
```bash
cd C:\Users\ADMIN\new-project\backend
python init_db_improved.py
python create_test_data.py
```

---

## Stop the Services

### Batch File Method:
- Close the command windows

### PowerShell Method:
- Press `CTRL+C` to stop monitoring
- Processes will be cleaned up

### Manual Terminal:
- Press `CTRL+C` in each terminal

---

## Pro Tips

1. **Keep the startup window minimized** - Services run in background
2. **Don't close the windows** - Services keep running
3. **Check windows taskbar** for running services
4. **Restart by closing and re-running** if needed

---

## Next Steps

1. Run: `start-project.bat` (or PowerShell script)
2. Open browser to: `http://localhost:3000`
3. Login as recruiter to see automatic matching
4. Expand jobs to see matching candidates
5. Click candidates for detailed scores

---

**Everything is set up to run continuously without stopping!** 🚀

All automatic matching features work continuously as long as services are running.
