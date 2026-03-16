# 🚀 Admin Panel Quick Start

## 30-Second Setup

### Step 1: Initialize Database (First Time Only)
```bash
cd backend
python init_db_improved.py
```

### Step 2: Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
✅ Backend running at: http://localhost:8000

### Step 3: Start Frontend  
```bash
cd frontend
npm run dev
```
✅ Frontend running at: http://localhost:3000

### Step 4: Open Admin Dashboard
```
http://localhost:3000/admin
Email: admin@example.com
Password: Admin@1234
```

## 📊 What You Can Do

### Manage Users
- ✓ List all users in the system
- ✓ Search users by email or name
- ✓ Filter by role (Job Seeker, Recruiter)
- ✓ Verify unverified user accounts
- ✓ Reject suspicious accounts
- ✓ View user status and join dates

### Verify Recruiters
- ✓ Review pending recruiter companies
- ✓ View company information
- ✓ Approve/reject company verification
- ✓ Track verification status

### Monitor Platform
- ✓ View real-time statistics
- ✓ Track user growth
- ✓ Monitor verification rates
- ✓ View user distribution by role
- ✓ Check recent activity log

## 🎯 Quick Actions

### Verify a User
1. Go to Users tab
2. Search for user email
3. Click "✓ Verify" button
4. Done! User is now verified

### Approve a Recruiter
1. Go to Recruiters tab
2. Find the company
3. Click "✓ Verify Company"
4. Done! Recruiter can now post jobs

### Monitor Statistics
1. Go to Overview tab
2. See all platform metrics
3. Monitor user growth
4. Track verification progress

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Make sure you're in backend directory
cd backend

# Check if port 8000 is available
# If not, change port: python -m uvicorn app.main:app --reload --port 8001

# Make sure dependencies are installed
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Make sure you're in frontend directory
cd frontend

# Install dependencies if needed
npm install

# Clear cache if having issues
rm -rf node_modules package-lock.json
npm install
```

### Can't login to admin panel?
- Email: `admin@example.com` (case-sensitive)
- Password: `Admin@1234` (capital A, capital T)
- Make sure database was initialized: `python backend/init_db_improved.py`

## 📱 Test Accounts

Use these accounts to test different user roles:

```
Admin Account (Full Access)
├─ Email: admin@example.com
├─ Password: Admin@1234
└─ Access: Admin Panel at /admin

Job Seeker Account (Candidate)
├─ Email: candidate@example.com
├─ Password: Test@1234
└─ Access: Candidate Dashboard at /candidate

Recruiter Account (Employer)
├─ Email: recruiter@example.com
├─ Password: Test@1234
└─ Access: Job Posting at /jobs
```

## 📡 API Testing

### Test All Admin Endpoints
```bash
python test_admin_api.py
```

### Manual API Test
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin@1234"}'

# Get statistics (use token from above)
curl -X GET http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎨 Dashboard Features

### Overview Tab
- 📊 Total users count
- ✓ Verified users count
- ✗ Unverified users (needs action)
- 👥 Active users count
- 👤 Job seekers count
- 🏢 Recruiters count
- ✓ Verified companies
- ⏳ Pending companies

### Users Tab
- 🔍 Search by email/name
- 🏷️ Filter by role
- 📋 Complete user list
- ✓ Verify unverified users
- ✕ Reject suspicious accounts
- 📅 View registration dates
- 🔀 See verification status

### Recruiters Tab
- 🏢 Company cards
- ✓ Company verification status
- 📝 Company details
- 👤 Contact information
- ✓ Approve companies
- ⏳ Track pending approvals

## 💡 Common Tasks

### Task: Verify 10 New Users
1. Go to Users tab
2. Click search, leave empty to see all
3. For each unverified user, click "✓ Verify"
4. ✅ Done - all users now verified

### Task: Check New Recruiter Signups
1. Go to Recruiters tab
2. Review pending companies
3. Click "✓ Verify Company" for each approved one
4. ✅ Recruiters can now post jobs

### Task: Monitor Platform Health
1. Go to Overview tab
2. Check total user count - is it growing?
3. Check verification rate - % verified?
4. Check recruiter vs job seeker ratio
5. ✅ Platform health tracked

## 🔐 Security Notes

- Admin access requires admin role in database
- All endpoints protected by JWT tokens
- Passwords are securely hashed (bcrypt)
- Activity logged for audit trail
- Email verification required for accounts
- Session tokens expire for security

## 📞 Support

**API Documentation:** http://localhost:8000/docs
**Alternative Docs:** http://localhost:8000/redoc

**Full Guide:** See [ADMIN_PANEL_GUIDE.md](ADMIN_PANEL_GUIDE.md)
**Status Report:** See [ADMIN_PANEL_STATUS.md](ADMIN_PANEL_STATUS.md)

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Database initialized without errors
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can login to admin panel
- [ ] Can see statistics on Overview tab
- [ ] Can see users in Users tab
- [ ] Can see recruiters in Recruiters tab
- [ ] Can use search/filter functions
- [ ] Verify button works
- [ ] API docs accessible at /docs

## 🎉 Ready to Go!

Everything is set up and ready to use. Start managing your platform! 

**Questions?** Check the full documentation in ADMIN_PANEL_GUIDE.md
