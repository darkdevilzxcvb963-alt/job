import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

jobs = [
    {
        "title": "Senior Solutions Architect",
        "company": "Global Tech",
        "location": "Remote",
        "description": "Expert in AWS, distributed systems, and Python. Lead cloud-native transformations and mentoring engineering teams. Strong knowledge of cybersecurity and risk assessment.",
        "job_type": "full-time",
        "salary_min": 140000,
        "salary_max": 180000,
        "experience_required": 8,
        "required_skills": ["Python", "AWS", "Cybersecurity", "Strategic Planning", "Technical Writing"]
    },
    {
        "title": "Frontend Developer",
        "company": "Visual Arts",
        "location": "Hybrid",
        "description": "Looking for a React expert with strong UI/UX design skills. Experience with Figma, Adobe Photoshop, and modern CSS frameworks. Collaborative team player with Agile experience.",
        "job_type": "full-time",
        "salary_min": 90000,
        "salary_max": 130000,
        "experience_required": 3,
        "required_skills": ["React", "JavaScript", "Figma", "UI/UX Design", "Agile Methodology"]
    },
    {
        "title": "Product Manager",
        "company": "SaaS Cloud",
        "location": "Austin, TX",
        "description": "Drive product roadmap and strategy for cloud platforms. Strong stakeholder management and business development skills. Experience with Jira and HubSpot.",
        "job_type": "full-time",
        "salary_min": 110000,
        "salary_max": 150000,
        "experience_required": 5,
        "required_skills": ["Product Management", "Jira", "Stakeholder Management", "Business Development", "Market Research"]
    }
]

print(f"Pinging server at {BASE_URL}...")
try:
    r = requests.get(f"{BASE_URL}/jobs/")
    print(f"Server is up! Current job count: {len(r.json())}")
except Exception as e:
    print(f"Error connecting to server: {e}")
    exit(1)

print("\nStarting job seeding...")
for job in jobs:
    print(f"Creating: {job['title']}...")
    try:
        r = requests.post(f"{BASE_URL}/jobs/", json=job)
        if r.status_code == 201:
            print(f"✓ Success: {job['title']} created.")
        else:
            print(f"✗ Failed ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

print("\nSeeding complete! Now checking job count again...")
r = requests.get(f"{BASE_URL}/jobs/")
print(f"Final job count: {len(r.json())}")
