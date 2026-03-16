"""
Verification script to test the recruiter matches interface setup
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"
RECRUITER_EMAIL = "recruiter@example.com"
RECRUITER_PASSWORD = "Recruiter@1234"

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def test_backend_connection():
    """Test if backend is running"""
    print_header("1. Testing Backend Connection")
    try:
        response = requests.get(f"{BASE_URL}/health" if hasattr(requests, 'get') else BASE_URL, timeout=5)
        print("✓ Backend is running at http://127.0.0.1:8000")
        return True
    except Exception as e:
        print(f"✗ Backend not responding: {str(e)}")
        print("  Make sure to run: python run_server.py")
        return False

def test_recruiter_login():
    """Test recruiter login"""
    print_header("2. Testing Recruiter Login")
    try:
        response = requests.post(
            f"{BASE_URL}/auth-simple/login",
            json={"email": RECRUITER_EMAIL, "password": RECRUITER_PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user = data.get('user', {})
            print(f"✓ Login successful")
            print(f"  User: {user.get('full_name')} ({user.get('role')})")
            print(f"  Email: {user.get('email')}")
            return token
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {str(e)}")
        return None

def test_get_jobs(token):
    """Test getting recruiter's jobs"""
    print_header("3. Testing Get Jobs Endpoint")
    if not token:
        print("⊘ Skipped (no token)")
        return None
    
    try:
        response = requests.get(
            f"{BASE_URL}/jobs",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', []) if isinstance(data, dict) else data
            print(f"✓ Retrieved {len(jobs)} jobs")
            for job in jobs[:3]:  # Show first 3
                print(f"  - {job.get('title')} (ID: {job.get('id')})")
            return jobs if jobs else []
        else:
            print(f"✗ Failed to get jobs: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return []

def test_get_job_matches(token, job_id):
    """Test getting matches for a job"""
    print_header("4. Testing Get Job Matches Endpoint")
    if not token:
        print("⊘ Skipped (no token)")
        return None
    
    try:
        response = requests.get(
            f"{BASE_URL}/matches/job/{job_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            matches = response.json()
            if isinstance(matches, dict) and 'data' in matches:
                matches = matches['data']
            print(f"✓ Retrieved {len(matches)} matches for job {job_id}")
            for match in matches[:2]:  # Show first 2
                score = match.get('overall_score', 0)
                name = match.get('candidate_name', 'Unknown')
                print(f"  - {name}: {score*100:.0f}% match")
                print(f"    - Semantic: {match.get('semantic_similarity', 0)*100:.0f}%")
                print(f"    - Skills: {match.get('skill_overlap_score', 0)*100:.0f}%")
                print(f"    - Experience: {match.get('experience_alignment', 0)*100:.0f}%")
            return matches
        else:
            print(f"✗ Failed to get matches: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return []

def test_database_data():
    """Test if database has test data"""
    print_header("5. Testing Database Content")
    try:
        import sys
        sys.path.insert(0, '/root/backend')
        from app.core.database import SessionLocal
        from app.models.user import User, UserRole
        from app.models.job import Job
        from app.models.match import Match
        
        db = SessionLocal()
        
        # Count users
        users = db.query(User).count()
        recruiters = db.query(User).filter(User.role == UserRole.RECRUITER).count()
        job_seekers = db.query(User).filter(User.role == UserRole.JOB_SEEKER).count()
        
        # Count jobs
        jobs = db.query(Job).count()
        
        # Count matches
        matches = db.query(Match).count()
        
        db.close()
        
        print(f"✓ Database connected")
        print(f"  Total Users: {users}")
        print(f"    - Recruiters: {recruiters}")
        print(f"    - Job Seekers: {job_seekers}")
        print(f"  Total Jobs: {jobs}")
        print(f"  Total Matches: {matches}")
        
        if users < 3:
            print(f"\n  ⚠️  Need to create test users:")
            print(f"     python init_db_improved.py")
        
        if jobs < 3 or matches < 3:
            print(f"\n  ⚠️  Need to create test data:")
            print(f"     python create_test_data.py")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        return False

def test_frontend_files():
    """Test if frontend files exist"""
    print_header("6. Testing Frontend Files")
    import os
    
    files = [
        "frontend/src/pages/Matches.jsx",
        "frontend/src/styles/Matches.css",
        "frontend/src/contexts/AuthContext.jsx",
        "frontend/src/services/api.js"
    ]
    
    all_exist = True
    for file in files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print_header("RECRUITER MATCHES INTERFACE - VERIFICATION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    
    # Test backend connection
    if not test_backend_connection():
        print("\n✗ Cannot proceed without backend running")
        return False
    
    # Test frontend files
    test_frontend_files()
    
    # Test database
    test_database_data()
    
    # Test recruiter login
    token = test_recruiter_login()
    
    # Test get jobs
    jobs = test_get_jobs(token)
    
    # Test get matches (if we have jobs)
    if jobs and len(jobs) > 0:
        first_job = jobs[0]
        test_get_job_matches(token, first_job['id'])
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    print("\n✓ System verification complete!")
    print("\nNext Steps:")
    print("  1. Open http://localhost:3000 in your browser")
    print("  2. Login with: recruiter@example.com / Recruiter@1234")
    print("  3. Navigate to Matches page")
    print("  4. Select a job from the dropdown")
    print("  5. View matching candidates!")
    print("\nFor detailed guide, see: RECRUITER_MATCHES_GUIDE.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
