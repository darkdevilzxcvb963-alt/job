# 🚀 Quick Start - Recruiter Matches Feature

## ⚡ 5-Minute Setup

### Step 1: Prepare Backend (1 min)
```powershell
# Open PowerShell and navigate to backend
cd backend

# Initialize database with users
python init_db_improved.py

# Create test jobs and candidates
python create_test_data.py
```

Expected output:
```
✓ Database tables created successfully!
✓ Test admin created: admin@example.com
✓ Test candidate created: candidate@example.com
✓ Test recruiter created: recruiter@example.com
✓ Candidates created successfully!
✓ Jobs created successfully!
✓ Matches created successfully!
```

### Step 2: Start Backend (1 min)
```powershell
# Still in backend directory
python run_server.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Start Frontend (1 min)
```powershell
# Open new PowerShell window
cd frontend

# Install dependencies (skip if already done)
npm install

# Start dev server
npm run dev
```

Expected output:
```
  VITE v4.x.x  ready in 234 ms
  ➜  Local:   http://localhost:3000/
```

### Step 4: Login & Test (2 min)
1. Open http://localhost:3000 in browser
2. Click **"Already have an account? Login"**
3. Enter credentials:
   - Email: `recruiter@example.com`
   - Password: `Recruiter@1234`
4. You should redirect to `/jobs` page
5. Look for **"Matches"** in navigation
6. Click **Matches** → Select job from dropdown → View matches!

---

## ✨ Features to Try

### Job Selection Dropdown
- Shows all your posted jobs
- Click dropdown to see list:
  - Senior Full Stack Developer
  - Backend Engineer
  - Frontend Developer

### Match Results
- **Count**: "X Matching Candidates Found"
- **Scores**: Color-coded circles
  - 🟢 Green: 80%+ (Excellent match)
  - 🟡 Amber: 60-80% (Good match)
  - 🔴 Red: <60% (Fair match)

### Expand Cards
- Click any candidate card to expand
- Shows:
  - Semantic Match Score
  - Skills Match Score
  - Experience Alignment
  - AI-generated explanation
  - Action buttons

### Color-Coded Feedback
```
Match Score Color Guide:
  80-100%  →  Green (#10b981)    "Excellent match!"
  60-79%   →  Amber (#f59e0b)    "Good match"
  0-59%    →  Red (#ef4444)      "Potential fit"
```

---

## 📊 Sample Data Included

### 3 Test Candidates
| Name | Email | Skills | Experience |
|------|-------|--------|------------|
| Alice Johnson | jobseeker@example.com | Full Stack, React, Python, FastAPI | 6 years |
| Bob Martinez | bob.engineer@example.com | Backend, Python, Java, Kubernetes | 8 years |
| Sarah Chen | sarah.designer@example.com | UI/UX, Figma, React, CSS | 4 years |

### 3 Test Jobs
| Title | Location | Experience | Salary |
|-------|----------|------------|--------|
| Senior Full Stack Developer | San Francisco | Senior | $140K-$200K |
| Backend Engineer | Remote | Mid-Level | $120K-$160K |
| Frontend Developer | San Francisco | Mid-Level | $110K-$150K |

### Pre-calculated Matches
- Alice → Senior Full Stack: **88%** ✅
- Bob → Backend Engineer: **92%** ✅✅
- Alice → Backend: **84%** ✅
- Alice → Frontend: **89%** ✅
- Sarah → Frontend: **84%** ✅

---

## 🧪 Test Scenarios

### Scenario 1: Excellent Match
1. Select "Senior Full Stack Developer"
2. Click "Alice Johnson" card
3. See 88% overall score
4. Green color-coded display
5. Explanation: "Strong match! Alice has extensive..."

### Scenario 2: High Match
1. Select "Backend Engineer"
2. Click "Bob Martinez" card
3. See 92% overall score
4. Green color-coded display
5. Excellent skill overlap

### Scenario 3: Good Match
1. Select "Frontend Developer"
2. Click "Sarah Chen" card
3. See 84% overall score
4. Green color-coded display
5. Design + React background

### Scenario 4: Cross-functional Match
1. Select "Backend Engineer"
2. Click "Alice Johnson" card
3. See 84% overall score
4. Full stack background helps

---

## 🔍 Verification Checklist

After setup, verify these work:

- [ ] Backend running on http://127.0.0.1:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Can login with recruiter email
- [ ] Redirects to /jobs after login
- [ ] Matches page loads
- [ ] Job dropdown shows 3 jobs
- [ ] Selecting job loads matches
- [ ] Cards display with:
  - [ ] Candidate avatar (initials)
  - [ ] Name and email
  - [ ] Overall score circle
  - [ ] Color-coded based on score
- [ ] Click card to expand
- [ ] Expanded view shows:
  - [ ] Semantic similarity score/bar
  - [ ] Skills match score/bar
  - [ ] Experience alignment score/bar
  - [ ] AI explanation text
  - [ ] Action buttons (Contact, View Resume, Save)
- [ ] Empty state shows "Get Started" message

---

## 🐛 Quick Troubleshooting

### "No jobs in dropdown"
```powershell
# Recreate test data
cd backend
python create_test_data.py
```

### "Backend won't start"
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000
# Kill process and restart: python run_server.py
```

### "Frontend won't start"
```powershell
# Check if port 3000 is in use
netstat -ano | findstr :3000
# Try different port: npm run dev -- --port 3001
```

### "No matches showing"
- Ensure test data created: `python create_test_data.py`
- Check browser console (F12) for errors
- Verify backend token is valid
- Clear browser cache: Ctrl+Shift+Delete

### "Styles not showing"
- Hard refresh: Ctrl+Shift+R
- Clear node_modules: `rm -r node_modules`
- Reinstall: `npm install`

---

## 📱 Alternative Logins

You can also test other roles:

**Job Seeker View**:
- Email: `jobseeker@example.com`
- Password: `Jobseeker@1234`
- Redirects to: `/candidate`
- Shows: Candidate matches (reverse logic)

**Admin View**:
- Email: `admin@example.com`
- Password: `Admin@1234`
- Redirects to: `/admin`
- Shows: Admin dashboard

---

## 📖 More Information

For detailed information, see:
- **RECRUITER_MATCHES_GUIDE.md** - Complete guide with API details
- **RECRUITER_MATCH_DISPLAY_IMPROVEMENTS.md** - Technical implementation
- **verify_recruiter_matches.py** - Run verification tests

---

## 🎯 Expected Behavior

### When You Select a Job:
```
Step 1: Click dropdown
  → Shows list of your jobs

Step 2: Select a job
  → Shows job info panel (title, company, location)
  → Loads matching candidates

Step 3: View results
  → Shows candidate count
  → Each card shows avatar, name, email, score
  → Colors indicate match quality

Step 4: Click card to expand
  → Shows detailed scores
  → Shows score breakdown with bars
  → Shows match explanation
  → Shows action buttons

Step 5: Take action
  → Contact, View Resume, or Save buttons
  → (Currently placeholder - buttons are clickable but non-functional)
```

---

## ✅ You're Ready!

Once you see the recruiter matches interface working with:
- Job dropdown populated
- Matches loading correctly
- Color-coded scores displaying
- Cards expanding/collapsing

**You've successfully tested the recruiter match display feature! 🎉**

---

## Next Steps

### To Continue Development:
1. Implement "Contact Candidate" functionality
2. Add "View Resume" modal with PDF preview
3. Implement "Save for Later" feature
4. Add filtering and sorting
5. Create interview scheduling

### For Production:
1. Replace test data with real database
2. Configure proper authentication
3. Set up email notifications
4. Add analytics tracking
5. Configure cloud storage for resumes

---

**Ready? Start with Step 1: Backend Setup! 🚀**

