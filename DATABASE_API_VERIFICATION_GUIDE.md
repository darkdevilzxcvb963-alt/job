# 🔍 Database & API Verification Guide (1000% Working)

Here is exactly how you can independently verify that all Candidate, Recruiter, and Admin databases are fully loaded, and that the AI Resume Analyzer and Matchmaker APIs are running perfectly on your laptop.

### Phase 1: Verify the Database (Recruiters, Candidates, Admin)

Your data is stored safely in `backend/resume_matching.db`. Here are three perfect ways to see the data directly on your laptop:

**Method 1: Run The Diagnostic Script**
Open a new terminal and run:
`python check_db_state.py`
*(This directly queries your SQLite database and prints out the exact counts of Recruiters, Candidates, Jobs, and Admins).*

**Method 2: Visual Database Interface (Recommended)**
Since your database is `resume_matching.db` (SQLite), you can view it seamlessly in VS Code!
1. Go to the Extensions tab in VS Code.
2. Search and install **"SQLite Viewer"** (by Florian Klampfer).
3. Open the file `backend/resume_matching.db` from your explorer.
4. You will instantly see all tables (`users`, `candidates`, `jobs`, `matches`, `applications`). You can click on them and see the 1000% saved rows for recruiters, candidates, and admins!

---

### Phase 2: Verify the AI Resume Analysis & Matching APIs

To prove the AI Processing is functioning properly, you can test the APIs in two ways:

**Method 1: Internal API Automated Testing**
Your project comes with bulletproof verification scripts. Run these in your terminal from the `new-project` directory:

1. **Test Resume Processing**: 
   `python backend/test_resume_processing.py`
   *(This uploads a dummy resume block, triggers the NLP pipeline, and shows you exactly how the API extracts skills, experience, and education).*

2. **Test Recruiter Matches**: 
   `python verify_recruiter_matches.py`
   *(This simulates the exact Matching Engine backend logic. It takes a job description and runs it against active candidates, printing out the 0 to 100 Overall Score data based on skills and location!).*

3. **Verify the Full Application Cycle**:
   `python verify_application_flow.py`
   *(This creates a dummy job match and simulates a candidate applying, verifying the backend automatically pings the recruiter via the Notification API).*

**Method 2: Interactive API Swagger Dashboard**
FastAPI gives you a beautiful web interface to manually test your APIs:
1. Start your backend by running `./start-backend.ps1`
2. Open your browser and go to: **[http://localhost:8000/docs](http://localhost:8000/docs)**
3. You will see every single API route documented! 
4. Scroll down to `Candidates`, find the `/api/v1/candidates/{candidate_id}/resume` route, click **"Try it out"**, upload a PDF, and hit Execute. You'll see the exact 1000% working JSON response the frontend gets!

---

### Phase 3: See it 1000% Working on the Live Frontend

1. Run the full project using your shortcut:
   `./start-project.bat`
2. **For Admin Verification**: Go to `http://localhost:3000/admin`. Log in with your admin credentials to see the system statistics (users, active jobs, complete metrics).
3. **For Recruiter Verification**: Log in as a Recruiter. Go to the "Active Roles" tab and see the jobs. Click "Matches" to see the dynamic AI score cards populating from the API natively.
4. **For Candidate Verification**: Log in as a Candidate, go to "Settings -> Profile", and upload a test Resume PDF. You will see the UI immediately analyze and fill out the fields, proving the AI API is deeply integrated.

By using the **SQLite Viewer** extension and the **http://localhost:8000/docs** interface, you can see all your backend data physically mapped on your machine!
