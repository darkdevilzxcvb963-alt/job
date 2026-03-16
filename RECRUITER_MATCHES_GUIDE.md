# Recruiter Match Display - Setup & Testing Guide

## Overview
The recruiter match display has been enhanced to show job-based matching with candidate resumes. Recruiters can now:
- View all their posted jobs in a dropdown
- Select a job to see matching candidates
- View detailed match scores (semantic, skills, experience)
- Expand cards to see match explanations and take action

## New Features Implemented

### 1. **Recruiter-Specific Job Selection**
- Dropdown showing recruiter's own jobs instead of manual ID input
- Displays job title and company for easy selection
- Automatically filters jobs posted by logged-in recruiter

### 2. **Enhanced Match Card UI**
- Candidate avatar with initials
- Candidate name and email displayed
- Color-coded match score (Green: 80%+, Amber: 60-80%, Red: <60%)
- Expandable cards with click-to-expand functionality

### 3. **Detailed Match Breakdown**
When expanded, cards show:
- **Semantic Match**: How well resume content matches job requirements
- **Skills Match**: Overlap between required and candidate skills
- **Experience Level**: Alignment of experience with job requirements
- **Match Explanation**: AI-generated insight on why this is a good match

### 4. **Action Buttons**
- 📧 Contact Candidate
- 👁️ View Full Resume
- ⭐ Save for Later

### 5. **Job Info Panel**
- Shows selected job details: title, company, location, job type
- Appears above match results for context

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn
- Windows PowerShell 5.1+ (for running scripts)

### Step 1: Database Initialization
First, ensure the database is initialized with users:

```bash
# From backend directory
cd backend
python init_db_improved.py
```

Output should show:
```
✓ Database tables created successfully!
✓ Test admin created: admin@example.com
✓ Test candidate created: candidate@example.com
✓ Test recruiter created: recruiter@example.com
```

### Step 2: Create Test Data (Jobs & Matches)
Create jobs and candidates for testing the matching system:

```bash
# From backend directory
python create_test_data.py
```

This creates:
- **3 Test Candidates**: Alice (Full Stack), Bob (Backend), Sarah (Designer)
- **3 Test Jobs**: Senior Full Stack Dev, Backend Engineer, Frontend Developer
- **5 Pre-calculated Matches** with realistic scores

### Step 3: Start Backend Service
```bash
# From backend directory
python run_server.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Start Frontend Service
```bash
# From frontend directory
npm install  # if not already done
npm run dev
```

Expected output:
```
  VITE v4.x.x  ready in 234 ms

  ➜  Local:   http://localhost:3000/
```

## Testing the Recruiter Match Display

### Test Case 1: Login as Recruiter
1. Open http://localhost:3000 in browser
2. Click "Already have an account? Login"
3. Enter credentials:
   - Email: `recruiter@example.com`
   - Password: `Recruiter@1234`
4. Should redirect to `/jobs` page
5. Look for "Matches" or navigation menu

### Test Case 2: View Job-Based Matches
1. On the Matches page, you should be on "Job Matches" tab
2. **Job Selection Dropdown** should show:
   - Senior Full Stack Developer
   - Backend Engineer
   - Frontend Developer
3. Select "Senior Full Stack Developer" from dropdown
4. Should display **Job Info Panel**:
   - Job Title: "Senior Full Stack Developer"
   - Company: "Tech Innovations Inc."
   - Location: "San Francisco, CA"
   - Job Type: "Full-time"

### Test Case 3: View Match Results
After selecting a job, you should see matching candidates:

**Example: Senior Full Stack Developer**
```
2 Matching Candidates Found

[Avatar: A] Alice Johnson
           jobseeker@example.com
           [88%] Match Score
           
[Avatar: B] Bob Martinez
           bob.engineer@example.com
           [84%] Match Score
```

### Test Case 4: Expand Match Card
1. Click on any match card to expand it
2. Should show:
   - **Semantic Match Score** (92% for Alice's job 1)
   - **Skills Match Score** (88% for Alice's job 1)
   - **Experience Alignment** (85% for Alice's job 1)
   - **Color-coded score bars** (Green for 80%+)
   - **Match Explanation**: "Strong match! Alice has extensive..."
   - **Action Buttons**: Contact, View Resume, Save

### Test Case 5: Color-Coded Scoring
Verify score colors by checking different matches:
- **Green** (80%+): Bob with Backend Engineer (92%)
- **Amber** (60-80%): Should appear if you have lower matches
- **Red** (<60%): Add test data with low scores if needed

### Test Case 6: Switch Between Match Types
1. Click "📄 Candidate Matches" tab
2. Enter a candidate ID (e.g., 1)
3. Should switch to candidate-centric view
4. Click "💼 Job Matches" to return to recruiter view

## API Integration Verification

### Check Required API Endpoints

#### 1. Get Recruiter's Jobs
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/v1/jobs
```

Expected response structure:
```json
{
  "data": [
    {
      "id": 1,
      "title": "Senior Full Stack Developer",
      "company": "Tech Innovations Inc.",
      "location": "San Francisco, CA",
      "job_type": "Full-time"
    }
  ]
}
```

#### 2. Get Matches for a Job
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/v1/matches/job/1
```

Expected response structure:
```json
[
  {
    "id": 1,
    "candidate_id": 1,
    "candidate_name": "Alice Johnson",
    "candidate_email": "jobseeker@example.com",
    "semantic_similarity": 0.92,
    "skill_overlap_score": 0.88,
    "experience_alignment": 0.85,
    "overall_score": 0.88,
    "match_explanation": "Strong match! Alice has..."
  }
]
```

## Test Data Reference

### Candidates
| Email | Password | Role | Skills |
|-------|----------|------|--------|
| jobseeker@example.com | Jobseeker@1234 | Job Seeker | Python, JS, React, FastAPI, PostgreSQL, Docker, AWS |
| bob.engineer@example.com | Bob@1234 | Job Seeker | Python, Java, FastAPI, Django, PostgreSQL, MongoDB, K8s |
| sarah.designer@example.com | Sarah@1234 | Job Seeker | Figma, Adobe XD, CSS, HTML, React, Design Systems |

### Recruiter
| Email | Password | Role | Company |
|-------|----------|------|---------|
| recruiter@example.com | Recruiter@1234 | Recruiter | Tech Innovations Inc. |

### Jobs (All posted by recruiter@example.com)
| Title | Experience Level | Location | Salary Range |
|-------|------------------|----------|---------------|
| Senior Full Stack Developer | Senior | San Francisco | $140K-$200K |
| Backend Engineer | Mid-Level | Remote | $120K-$160K |
| Frontend Developer | Mid-Level | San Francisco | $110K-$150K |

## Styling Updates

### CSS Classes Added/Updated
- `.job-info-panel` - Shows selected job context
- `.match-score-display` - Score circle display
- `.score-circle` - Colored circular score
- `.candidate-avatar` - Candidate initials avatar
- `.match-expanded` - Expanded card content section
- `.match-actions` - Action buttons container
- `.btn-contact`, `.btn-view`, `.btn-save` - Individual buttons

### Color Scheme
- **Primary Gradient**: #667eea → #764ba2 (Purple)
- **Success Green**: #10b981 (80%+ matches)
- **Warning Amber**: #f59e0b (60-80% matches)
- **Danger Red**: #ef4444 (<60% matches)

## Troubleshooting

### Issue: No jobs appear in dropdown
**Solution**: 
- Ensure you're logged in as recruiter
- Check that jobs were created: `python create_test_data.py`
- Verify /jobs API returns data

### Issue: No matches appear after selecting job
**Solution**:
- Ensure test data was created: `python create_test_data.py`
- Check browser console for API errors
- Verify job ID is valid

### Issue: Matches API returns empty
**Solution**:
```bash
# Check if matches exist in database
python -c "from app.models.match import Match; from app.core.database import SessionLocal; db = SessionLocal(); print(f'Matches: {db.query(Match).count()}')"
```

### Issue: Avatar not showing
**Solution**:
- Candidate name is required for avatar display
- Check that `candidate_name` field is populated in match response

## Frontend Components

### Files Modified
- `frontend/src/pages/Matches.jsx` - Main component (refactored)
- `frontend/src/styles/Matches.css` - Enhanced styling

### Key Imports
```javascript
import { getCandidateMatches, getJobMatches, getJobs } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
```

### Component State
- `matchType`: 'candidate' or 'job' (defaults to 'job' for recruiters)
- `jobId`: Selected job ID
- `candidateId`: Selected candidate ID
- `expandedMatch`: Currently expanded match card ID

## Performance Optimization

### Query Caching
- Recruiter jobs are cached via React Query
- Match data is cached per job/candidate
- Invalidate cache when new data is posted

### Lazy Loading
- Job dropdown loaded only when recruiter is detected
- Matches loaded only after job selection
- Avatar generated on-the-fly from candidate name

## Next Steps / Future Improvements

1. **Resume Preview Modal**: Add modal to preview full resume
2. **Contact Form**: Implement contact candidate functionality
3. **Save for Later**: Implement favorites/saved matches feature
4. **Filter & Sort**: Add filters by location, salary, experience
5. **Bulk Actions**: Select and email multiple candidates
6. **Analytics**: Track which matches were contacted/hired
7. **Notifications**: Alert when new matching candidates upload resume

## Support & Questions

If you encounter issues:
1. Check browser console (F12) for JavaScript errors
2. Check backend logs for API errors
3. Verify database has test data: `python create_test_data.py`
4. Clear browser cache: Ctrl+Shift+Delete
5. Restart both frontend and backend services

---

**Last Updated**: 2024
**Status**: Ready for Testing
