#!/usr/bin/env python3
"""
Signup System Test Script
Tests multiple user registrations and database storage
"""

import requests
import json
from datetime import datetime
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10

# Test users
TEST_USERS = [
    {
        "name": "Test User 1",
        "full_name": "John Developer",
        "email": "john.dev@example.com",
        "phone": "+1-555-123-4567",
        "password": "SecurePass123",
        "role": "job_seeker"
    },
    {
        "name": "Test User 2",
        "full_name": "Jane Recruiter",
        "email": "jane.recruiter@example.com",
        "phone": "+1-555-987-6543",
        "password": "RecruiterPass456",
        "role": "recruiter"
    },
    {
        "name": "Test User 3 (No Phone)",
        "full_name": "Simple User",
        "email": "simple.user@example.com",
        "phone": None,
        "password": "MinimalPass789",
        "role": "job_seeker"
    }
]

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

def print_data(text):
    """Print formatted data"""
    print(f"{Colors.BLUE}{text}{Colors.RESET}")

def test_signup(user_data):
    """Test user signup"""
    print_info(f"Testing signup for: {user_data['name']}")
    print_data(f"  Email: {user_data['email']}")
    print_data(f"  Role: {user_data['role']}")
    
    # Prepare signup data
    signup_data = {
        "full_name": user_data['full_name'],
        "email": user_data['email'],
        "password": user_data['password'],
        "role": user_data['role']
    }
    
    if user_data['phone']:
        signup_data['phone'] = user_data['phone']
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=signup_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"User created successfully!")
            print_data(f"  ID: {data.get('id')}")
            print_data(f"  Email: {data.get('email')}")
            print_data(f"  Full Name: {data.get('full_name')}")
            print_data(f"  Phone: {data.get('phone', 'Not provided')}")
            print_data(f"  Role: {data.get('role')}")
            print_data(f"  Verified: {data.get('is_verified')}")
            print_data(f"  Created: {data.get('created_at')}")
            return {"success": True, "data": data}
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            print_error(f"Signup failed: {error_msg}")
            return {"success": False, "error": error_msg, "status": response.status_code}
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {API_BASE_URL}")
        print_info("Make sure the backend is running on port 8000")
        return {"success": False, "error": "Connection error"}
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_duplicate_email():
    """Test duplicate email prevention"""
    print_header("Testing Duplicate Email Prevention")
    
    email = "duplicate.test@example.com"
    password = "TestPass123"
    
    # First signup
    print_info("Creating first user with email...")
    signup_data = {
        "full_name": "First User",
        "email": email,
        "password": password,
        "role": "job_seeker"
    }
    
    try:
        response1 = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=signup_data,
            timeout=TIMEOUT
        )
        
        if response1.status_code == 201:
            print_success("First user created successfully")
        else:
            print_error(f"Failed to create first user: {response1.json().get('detail')}")
            return
        
        # Second signup with same email
        print_info("Attempting to create second user with same email...")
        signup_data['full_name'] = "Second User"
        
        response2 = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=signup_data,
            timeout=TIMEOUT
        )
        
        if response2.status_code == 400:
            error_msg = response2.json().get('detail', '')
            if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
                print_success("Correctly rejected duplicate email")
                print_data(f"  Message: {error_msg}")
            else:
                print_error(f"Got 400 error but message unclear: {error_msg}")
        else:
            print_error(f"Should have rejected duplicate email but got status {response2.status_code}")
    
    except Exception as e:
        print_error(f"Error in duplicate test: {str(e)}")

def test_invalid_inputs():
    """Test input validation"""
    print_header("Testing Input Validation")
    
    test_cases = [
        {
            "name": "Password too short",
            "data": {
                "full_name": "Test User",
                "email": "short.pass@example.com",
                "password": "Short1",
                "role": "job_seeker"
            },
            "expected_error": "at least 8"
        },
        {
            "name": "Password without numbers",
            "data": {
                "full_name": "Test User",
                "email": "no.numbers@example.com",
                "password": "NoNumbersHere",
                "role": "job_seeker"
            },
            "expected_error": "digit"
        },
        {
            "name": "Invalid email format",
            "data": {
                "full_name": "Test User",
                "email": "invalid-email",
                "password": "ValidPass123",
                "role": "job_seeker"
            },
            "expected_error": "email"
        },
        {
            "name": "Name too short",
            "data": {
                "full_name": "A",
                "email": "test@example.com",
                "password": "ValidPass123",
                "role": "job_seeker"
            },
            "expected_error": "2 characters"
        }
    ]
    
    for test_case in test_cases:
        print_info(f"Testing: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/signup",
                json=test_case['data'],
                timeout=TIMEOUT
            )
            
            if response.status_code != 201:
                error_msg = response.json().get('detail', '')
                if test_case['expected_error'].lower() in error_msg.lower():
                    print_success(f"Correctly rejected: {error_msg}")
                else:
                    print_info(f"Rejected with: {error_msg}")
            else:
                print_error("Should have been rejected but signup succeeded")
        except Exception as e:
            print_error(f"Error: {str(e)}")

def test_login_after_signup(user_data):
    """Test login with newly created account"""
    print_info(f"Testing login for: {user_data['email']}")
    
    login_data = {
        "email": user_data['email'],
        "password": user_data['password']
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=login_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print_success(f"Login successful!")
                print_data(f"  Token type: {data.get('token_type', 'N/A')}")
                print_data(f"  Access token: {data.get('access_token', '')[:30]}...")
                return True
            else:
                print_error("Login response missing token")
                return False
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            print_error(f"Login failed: {error_msg}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print_header("Signup System Test Suite")
    print_info("Testing multiple user signup and database storage")
    print_info(f"Target API: {API_BASE_URL}\n")
    
    results = {
        "signup_tests": [],
        "login_tests": [],
        "validation_tests": [],
        "duplicate_test": None
    }
    
    # Test 1: Multiple User Signups
    print_header("Test 1: Multiple User Signups")
    for user in TEST_USERS:
        result = test_signup(user)
        results["signup_tests"].append(result)
        
        # Try to login after signup
        if result['success']:
            print("\n")
            login_success = test_login_after_signup(user)
            results["login_tests"].append(login_success)
        print("\n")
    
    # Test 2: Input Validation
    print_header("Test 2: Input Validation")
    test_invalid_inputs()
    
    # Test 3: Duplicate Email Prevention
    print_header("Test 3: Duplicate Email Prevention")
    test_duplicate_email()
    
    # Summary
    print_header("Test Summary")
    
    signup_count = sum(1 for r in results["signup_tests"] if r['success'])
    print_success(f"{signup_count}/{len(results['signup_tests'])} users signed up successfully")
    
    login_count = sum(1 for r in results["login_tests"] if r)
    print_success(f"{login_count}/{len(results['login_tests'])} users logged in successfully")
    
    print_info("All tests completed!")
    print_info("Check the database to verify user storage:")
    print_data("  Database: backend/resume_matching.db")
    print_data("  Table: users")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nTests interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
