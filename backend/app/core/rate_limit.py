from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from collections import defaultdict
import threading

class RateLimiter:
    """Simple in-memory rate limiter for production fallback"""
    def __init__(self, requests_limit: int, window_seconds: int):
        self.limit = requests_limit
        self.window = window_seconds
        self.history = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        now = datetime.utcnow()
        with self.lock:
            # Clean old entries
            self.history[key] = [t for t in self.history[key] if (now - t).total_seconds() < self.window]
            
            if len(self.history[key]) < self.limit:
                self.history[key].append(now)
                return True
            return False

# Global limiters for auth
login_limiter = RateLimiter(requests_limit=5, window_seconds=60) # 5 attempts per minute
otp_limiter = RateLimiter(requests_limit=3, window_seconds=300)   # 3 OTPs per 5 minutes

async def check_login_rate_limit(request: Request):
    client_ip = request.client.host
    if not login_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please wait a minute.")

async def check_otp_rate_limit(request: Request):
    client_ip = request.client.host
    if not otp_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait 5 minutes.")
