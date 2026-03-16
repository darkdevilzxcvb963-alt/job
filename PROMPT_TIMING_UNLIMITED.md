# Prompt Timing - Unlimited Configuration

## Current Configuration ✅

The project is configured with **unlimited prompt timing** (effectively unlimited session duration).

### Token Settings (in `backend/app/core/config.py`)

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600  # 1 year (unlimited)
REFRESH_TOKEN_EXPIRE_DAYS: int = 36500     # 100 years (effectively unlimited)
```

### Duration Breakdown

| Token Type | Duration | Minutes/Days |
|-----------|----------|--------------|
| **Access Token** | 1 year | 525,600 minutes |
| **Refresh Token** | 100 years | 36,500 days |

### What This Means

✅ **Users can stay logged in for up to 1 year** without needing to re-login
✅ **Refresh tokens last 100 years** - effectively forever
✅ **Sessions are persistent** - users won't be logged out
✅ **Perfect for development and testing** - no token expiration interruptions

---

## How Token Refresh Works

```
1. User logs in
   ↓
2. Gets access token (valid for 525,600 minutes / 1 year)
   ↓
3. Gets refresh token (valid for 36,500 days / 100 years)
   ↓
4. If access token expires after 1 year:
   → Can use refresh token to get new access token
   → Refresh token is also valid for 100 years
   ↓
5. User stays logged in effectively forever
```

---

## Verification

To verify the settings are loaded correctly:

```bash
# From backend directory
python -c "from app.core.config import settings; print(f'Access Token: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes = {settings.ACCESS_TOKEN_EXPIRE_MINUTES/60/24:.1f} days'); print(f'Refresh Token: {settings.REFRESH_TOKEN_EXPIRE_DAYS} days = {settings.REFRESH_TOKEN_EXPIRE_DAYS/365:.1f} years')"
```

Expected output:
```
Access Token: 525600 minutes = 365.0 days
Refresh Token: 36500 days = 100.0 years
```

---

## Configuration Files

### Primary Config File
📁 **Location:** `backend/app/core/config.py`

✅ **Lines 18-19:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600  # 1 year (unlimited)
REFRESH_TOKEN_EXPIRE_DAYS: int = 36500  # 100 years (effectively unlimited)
```

### How It's Used

**File:** `backend/app/core/security.py`
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # ... creates token valid for 525,600 minutes
```

---

## Environment Variables

The settings can be overridden via environment variables in `.env` file:

```bash
# Optional - if you want to change these, add to .env:
ACCESS_TOKEN_EXPIRE_MINUTES=525600
REFRESH_TOKEN_EXPIRE_DAYS=36500
```

Current status: **NOT overridden** - using defaults from config.py

---

## Testing Token Duration

### 1. Login and Check Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin@1234"
  }' | jq '.expires_in'
```

### 2. Decode Token to See Expiration
```bash
# Get the access_token from login response, then:
python -c "
import jwt
token = 'YOUR_ACCESS_TOKEN_HERE'
decoded = jwt.decode(token, options={'verify_signature': False})
print(f'Token expires: {decoded.get(\"exp\")}')
print(f'Current time: {int(__import__(\"time\").time())}')
print(f'Valid for: {(decoded.get(\"exp\") - int(__import__(\"time\").time())) / 60 / 60 / 24:.0f} days')
"
```

---

## Confirmation Checklist

✅ **Access Token Duration**
- Set to: 525,600 minutes
- Equals: 365 days
- Equals: 1 year

✅ **Refresh Token Duration**
- Set to: 36,500 days
- Equals: 100 years
- Status: Effectively unlimited

✅ **Configuration Source**
- File: `backend/app/core/config.py`
- Class: `Settings`
- Properties: Lines 18-19

✅ **Runtime Behavior**
- Tokens created with unlimited duration
- No automatic logout for 1 year
- Refresh token valid 100 years

✅ **Persistence Across Runs**
- Settings are hardcoded in config.py
- Loaded every time backend starts
- No need to reconfigure

---

## How This Persists Across Runs

The configuration is **hardcoded in the source code**, so:

✅ Every time you run: `python run.py`  
✅ Every time you run: `python -m uvicorn app.main:app`  
✅ Every time you start the backend service  

**The unlimited token timing is automatically loaded from `config.py`**

---

## Summary

| Aspect | Status | Details |
|--------|--------|---------|
| Access Token | ✅ Unlimited | 525,600 minutes = 1 year |
| Refresh Token | ✅ Unlimited | 36,500 days = 100 years |
| Configuration | ✅ Persistent | Hardcoded in config.py |
| Persists on Restart | ✅ Yes | Loaded every run |
| Current Status | ✅ UNLIMITED | Ready to use |

---

## Related Files

- 📁 **Configuration:** `backend/app/core/config.py`
- 📁 **Security:** `backend/app/core/security.py`
- 📁 **API Endpoint:** `backend/app/api/v1/auth.py`
- 📁 **Environment:** `backend/.env` (optional overrides)

---

**Status:** ✅ **PROMPT TIMING IS UNLIMITED AND PERSISTENT**

The unlimited token timing will be active every time you run the project - no additional configuration needed!

---

*Last Updated: January 23, 2026*
