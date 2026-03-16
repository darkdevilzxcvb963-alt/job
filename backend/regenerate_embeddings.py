"""
Script to trigger bulk embedding regeneration via admin endpoint
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@1234"  # Default admin password


def login_as_admin():
    """Login and get access token"""
    print("Logging in as admin...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    data = response.json()
    token = data.get("access_token")
    print(f"✓ Logged in successfully")
    return token

def regenerate_embeddings(token, min_score=0.01):
    """Call the bulk embedding regeneration endpoint"""
    print(f"\nTriggering bulk embedding regeneration (min score: {min_score})...")
    print("This may take a few minutes depending on the number of jobs and candidates...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/admin/regenerate-embeddings?min_match_score={min_score}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    result = response.json()
    return result

def main():
    print("="*60)
    print("BULK EMBEDDING REGENERATION")
    print("="*60)
    
    # Login
    token = login_as_admin()
    
    # Regenerate embeddings
    result = regenerate_embeddings(token, min_score=0.01)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    summary = result.get("summary", {})
    
    print(f"\n📋 JOBS:")
    print(f"   Processed: {summary.get('jobs', {}).get('processed', 0)}")
    print(f"   Failed: {summary.get('jobs', {}).get('failed', 0)}")
    
    print(f"\n👤 CANDIDATES:")
    print(f"   Processed: {summary.get('candidates', {}).get('processed', 0)}")
    print(f"   Failed: {summary.get('candidates', {}).get('failed', 0)}")
    
    print(f"\n🔗 MATCHES:")
    print(f"   Created: {summary.get('matches', {}).get('created', 0)}")
    
    errors = result.get("errors", [])
    total_errors = result.get("total_errors", 0)
    
    if total_errors > 0:
        print(f"\n⚠️  ERRORS: {total_errors} total")
        if errors:
            print("\nFirst few errors:")
            for error in errors[:5]:
                print(f"   - {error}")
    else:
        print("\n✅ No errors!")
    
    print("\n" + "="*60)
    print("✓ Bulk embedding regeneration completed!")
    print("="*60)

if __name__ == "__main__":
    main()
