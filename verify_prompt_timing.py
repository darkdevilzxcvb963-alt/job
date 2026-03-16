#!/usr/bin/env python3
"""
Verify Prompt Timing Configuration
Run from backend directory to verify unlimited token settings
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from app.core.config import settings  # type: ignore
except ImportError:
    print("Error: Could not import settings. Make sure you're in the project root.")
    sys.exit(1)

def verify_timing():
    """Verify prompt timing configuration"""
    
    print("\n" + "="*70)
    print("PROMPT TIMING CONFIGURATION VERIFICATION")
    print("="*70 + "\n")
    
    # Get token settings
    access_token_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # Convert to human-readable formats
    access_token_days = access_token_minutes / 60 / 24
    access_token_years = access_token_days / 365
    
    refresh_token_years = refresh_token_days / 365
    
    # Print configuration
    print("📋 CURRENT TOKEN CONFIGURATION")
    print("-" * 70)
    print()
    
    print(f"Access Token Duration:")
    print(f"  └─ {access_token_minutes:,} minutes")
    print(f"  └─ {access_token_days:.1f} days")
    print(f"  └─ {access_token_years:.1f} years")
    print()
    
    print(f"Refresh Token Duration:")
    print(f"  └─ {refresh_token_days:,} days")
    print(f"  └─ {refresh_token_years:.1f} years")
    print()
    
    # Verification
    print("✅ VERIFICATION")
    print("-" * 70)
    print()
    
    checks = [
        ("Access Token >= 365 days", access_token_days >= 365, f"{access_token_days:.1f} days"),
        ("Refresh Token >= 30000 days", refresh_token_days >= 30000, f"{refresh_token_days:,} days"),
        ("Configuration loaded", access_token_minutes > 0 and refresh_token_days > 0, "Yes"),
        ("Effectively Unlimited", 
         access_token_days >= 365 and refresh_token_days >= 30000, 
         "Yes - Sessions persist effectively forever"),
    ]
    
    all_pass = True
    for check_name, passed, value in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        print(f"   Value: {value}")
        print()
        if not passed:
            all_pass = False
    
    # Final status
    print("="*70)
    if all_pass:
        print("✅ STATUS: UNLIMITED PROMPT TIMING CONFIRMED")
        print()
        print("Users can stay logged in for:")
        print(f"  • Up to {access_token_years:.1f} years with access token")
        print(f"  • Up to {refresh_token_years:.1f} years total with refresh token")
        print()
        print("This configuration is PERSISTENT across project restarts.")
        print("No additional setup needed!")
    else:
        print("❌ STATUS: CONFIGURATION ISSUE DETECTED")
        print()
        print("Please check backend/app/core/config.py")
    
    print("="*70 + "\n")
    
    return all_pass

if __name__ == "__main__":
    success = verify_timing()
    sys.exit(0 if success else 1)
