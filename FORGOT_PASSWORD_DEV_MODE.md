# Forgot Password - Development Mode Solutions

## Problem
Email service is not configured in development mode, so password reset emails are not being sent.

## Solution 1: Development Mode Display (Recommended for Testing)

The backend now provides the reset link directly in the response when email is not configured.

### How to Use:

1. **Go to Forgot Password page**
   - Visit: `http://localhost:3000/forgot-password`
   - Enter your email address
   - Click "Send Reset Link"

2. **Get the Reset Link**
   - You'll see a success message
   - In development mode, a yellow box will appear with:
     - ✅ A clickable button to reset password
     - ✅ The full reset link (copy-paste option)
     - ✅ Copy to clipboard button

3. **Reset Your Password**
   - Click the "Reset Password" button or paste the link
   - Enter your new password
   - Submit the form
   - Done! ✓

### Example Response (Development Mode):
```json
{
  "message": "If an account exists with this email, a password reset link has been sent. Please check your email.",
  "dev_reset_link": "http://localhost:3000/reset-password?token=PyMyPBlapQ123abc..."
}
```

## Solution 2: Configure Real Email Service

If you want to test with real emails, configure Gmail SMTP:

### Step 1: Get Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password

### Step 2: Update `.env` file

```env
# Email Configuration
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
MAIL_FROM=your.email@gmail.com
MAIL_FROM_NAME=Resume Matching Platform
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_TLS=true
MAIL_SSL=false
```

### Step 3: Restart Backend
The email configuration will be automatically detected.

## Solution 3: Console Logging (Alternative)

If you're a developer, you can check the backend console logs:

1. Look at backend terminal output
2. Search for "password reset email"
3. The log will show:
   ```
   Email service disabled - password reset email for user@example.com (token: abc123...)
   ```

## Testing Checklist

### Test Forgot Password Flow:
- [ ] Go to login page → click "Forgot Password?"
- [ ] Enter valid email
- [ ] See success message with dev reset link
- [ ] Copy or click the reset link
- [ ] Enter new password
- [ ] Confirm password matches
- [ ] Click Reset Password
- [ ] See success message
- [ ] Redirected to login page
- [ ] Can login with new password

### Test Error Handling:
- [ ] Try with invalid email format → see error
- [ ] Try with non-existent email → see generic message (security feature)
- [ ] Try weak password → see validation errors
- [ ] Try mismatched passwords → see error
- [ ] Try same as old password → see error

### Test Rate Limiting:
- [ ] Send 3 reset requests within 1 hour → works
- [ ] Send 4th request within 1 hour → "Too many requests" error
- [ ] Wait 1 hour and try again → works (rate limit resets)

## Troubleshooting

### Reset link not appearing?
1. Check browser console for errors (F12)
2. Check backend logs for "forgot-password"
3. Verify the response includes "dev_reset_link"
4. Make sure email service credentials are NOT set

### Link doesn't work?
1. Make sure you're copying the entire link
2. Check if token has expired (24-hour window)
3. Try requesting a new password reset

### Backend not starting?
1. Comment out spacy/NLP imports if causing issues
2. Or use a simpler auth endpoint without NLP

## For Production

When deploying to production:
1. Configure real email service (Gmail, SendGrid, etc.)
2. Set MAIL_USERNAME and MAIL_PASSWORD in environment
3. The dev_reset_link will NOT be included in response (security)
4. Users will only see the standard message

## Quick Commands

### Restart Backend
```powershell
# Kill any Python processes
taskkill /F /IM python.exe

# Start backend fresh
cd c:\Users\ADMIN\new-project\backend
.\venv\Scripts\python.exe run_server.py
```

### Test API Directly
```powershell
# Using curl or Postman
POST http://localhost:8000/api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

## Backend Logs Location

Check logs in the running terminal where backend is started:
```
2026-01-23 16:13:20.954 | INFO | app.core.email:... | Email service disabled
```

Look for lines containing:
- "forgot-password" - for password reset requests
- "dev_reset_link" - for development mode links
- "Email service disabled" - confirms dev mode active
