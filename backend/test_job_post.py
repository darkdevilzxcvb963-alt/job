import requests
import json

# Test job posting endpoint
url = "http://127.0.0.1:8000/api/v1/jobs/"

# Sample job data
job_data = {
    "title": "Test Engineer",
    "company": "Test Company",
    "description": "This is a test job posting",
    "location": "Remote",
    "job_type": "full-time",
    "required_skills": ["Python", "Testing"],
    "skills_by_category": {
        "technical": ["Python", "Testing"]
    }
}

try:
    response = requests.post(url, json=job_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
