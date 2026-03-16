# How to Test Forgot Password in Development Mode

## Quick Start (30 seconds)

### Step 1: Go to Forgot Password Page
- Open: `http://localhost:3000/forgot-password`

### Step 2: Enter Any Email
- Example: `test@example.com`
- Click "Send Reset Link"

### Step 3: Get Development Mode Link
- You'll see a yellow box with:
  - ✅ **"Click Here to Reset Password"** button
  - 📋 Copy-paste link
  - 📝 Copy to clipboard button

### Step 4: Click the Button or Use the Link
- It will take you to the reset password page
- You'll see a countdown timer showing the link validity

### Step 5: Reset Your Password
- Enter new password
- Watch the strength meter update in real-time
- Confirm password matches
- Click "Reset Password"
- Success! ✓

---

## Detailed Testing Guide

### Test Case 1: Basic Forgot Password Flow
**Purpose**: Verify the complete forgot password process works

**Steps**:
1. Go to login page → Click "Forgot Password?"
2. Enter a valid email (e.g., `user@example.com`)
3. Click "Send Reset Link"
4. **Expected Result**: 
   - ✅ Success message appears
   - ✅ Yellow development mode box shows
   - ✅ Reset link is visible and clickable

**Success Indicator**: You can see the reset link and can click it

---

### Test Case 2: Email Validation
**Purpose**: Verify email format validation works

**Test 1a - Invalid Email Format**:
- Enter: `invalid.email`
- Click "Send Reset Link"
- **Expected**: Error message "Please enter a valid email address"

**Test 1b - Empty Email**:
- Leave email blank
- Click "Send Reset Link"
- **Expected**: Button is disabled or error shown

**Success Indicator**: Form validates email format before submission

---

### Test Case 3: Password Reset Form
**Purpose**: Verify password reset page works with token from dev link

**Steps**:
1. From forgot password page, get the dev reset link
2. Click the link (or copy and paste in new tab)
3. Reset password page loads

**Expected Results**:
- ✅ Form shows "Reset Password"
- ✅ Two password input fields
- ✅ "New Password" field
- ✅ "Confirm Password" field
- ✅ Show/hide password toggles appear
- ✅ Password strength meter shows

**Success Indicator**: Form displays properly with all expected elements

---

### Test Case 4: Password Strength Meter
**Purpose**: Verify real-time password strength feedback

**Steps**:
1. On reset password form, start typing in "New Password" field
2. Type different passwords and observe

**Test Cases**:
- `pass` → Strength: Weak (red)
- `Pass1` → Strength: Fair (orange)  
- `Pass123` → Strength: Good (yellow)
- `Password123` → Strength: Strong (green)
- `SecurePass@2024` → Strength: Very Strong (dark green)

**Expected**:
- ✅ Meter updates as you type
- ✅ Color changes based on strength
- ✅ Criteria list shows checkmarks for met requirements
- ✅ Unmet requirements show as unchecked

**Success Indicator**: Strength meter provides accurate real-time feedback

---

### Test Case 5: Password Validation
**Purpose**: Verify password requirements are enforced

**Test 5a - Too Short**:
- Enter: `Pass1`
- Click "Reset Password"
- **Expected**: Error "Password must be at least 8 characters"

**Test 5b - No Numbers**:
- Enter: `Password`
- Click "Reset Password"
- **Expected**: Error about needing numbers

**Test 5c - No Letters**:
- Enter: `12345678`
- Click "Reset Password"
- **Expected**: Error about needing letters

**Test 5d - Passwords Don't Match**:
- Password: `SecurePass123`
- Confirm: `DifferentPass456`
- Click "Reset Password"
- **Expected**: Error "Passwords don't match" or submit button disabled

**Success Indicator**: All validation checks work correctly

---

### Test Case 6: Successful Reset
**Purpose**: Verify password can actually be reset

**Steps**:
1. Go to forgot password
2. Enter valid email
3. Click reset link
4. Enter matching strong password (e.g., `NewPass@2024`)
5. Click "Reset Password"

**Expected**:
- ✅ Success message appears: "Password Reset Successful!"
- ✅ Message shows "Redirecting to login..."
- ✅ After 2 seconds, redirected to `/login`
- ✅ Can now login with new password

**Success Indicator**: Password successfully changed and can login

---

### Test Case 7: Invalid Token Handling
**Purpose**: Verify proper error handling for invalid tokens

**Test 7a - Invalid Token in URL**:
- Manually go to: `http://localhost:3000/reset-password?token=invalid123`
- **Expected**: Error message "This password reset link is invalid or has expired"
- **Expected**: Button to "Request New Reset Link"

**Test 7b - No Token in URL**:
- Go to: `http://localhost:3000/reset-password`
- **Expected**: Error message about invalid link
- **Expected**: Prompt to request new reset

**Success Indicator**: Invalid tokens are handled gracefully with helpful messages

---

### Test Case 8: Token Expiration
**Purpose**: Verify expired tokens are rejected

**Steps**:
1. Get reset link from forgot password
2. Wait... just kidding, 24-hour expiration makes this impractical to test in dev
3. Instead, check the countdown timer shows remaining time

**Alternative Test**:
- Get the reset link
- Check the page shows: "Reset link expires in X minutes"
- **Expected**: Timer counts down appropriately

**Success Indicator**: Expiration information is displayed to user

---

## Backend API Testing

### Direct API Test with Postman/curl

**Endpoint**: `POST http://localhost:8000/api/v1/auth/forgot-password`

**Request**:
```json
{
  "email": "test@example.com"
}
```

**Response (Development Mode)**:
```json
{
  "message": "If an account exists with this email...",
  "dev_reset_link": "http://localhost:3000/reset-password?token=abc123...",
  "message": "Development Mode: ... Or use this link: http://..."
}
```

**Check**:
- ✅ Status code: 200
- ✅ Response includes `dev_reset_link`
- ✅ Message mentions development mode
- ✅ Link is a valid URL

---

## Backend Logs to Check

When testing, look for these log messages in backend terminal:

**Successful Request**:
```
INFO     | app.api.v1.auth:forgot_password
Development mode: Reset link generated for [email]
```

**Email Service Status**:
```
WARNING  | app.core.email:... | Email not configured - using mock email sending
```

**Token Validation**:
```
INFO | validate-reset-token
Token validated successfully
```

---

## Checklist for Complete Testing

- [ ] Forgot password form loads
- [ ] Email validation works
- [ ] Dev reset link appears in success message
- [ ] Can click reset link
- [ ] Reset password form loads
- [ ] Password strength meter works
- [ ] Password validation enforced
- [ ] Password mismatch detected
- [ ] Success message shown
- [ ] Redirected to login
- [ ] Can login with new password
- [ ] Invalid tokens rejected
- [ ] Backend logs show no errors

---

## Expected Browser Console Output

When testing, open DevTools (F12) and check Console tab. You should see:
- No red errors
- Possibly some warnings (these are normal)
- XHR/Fetch requests to `/api/v1/auth/forgot-password`
- Successful responses

---

## Screenshots to Take

1. **Forgot Password Page**: Form with email input
2. **Success with Dev Link**: Yellow box showing reset link
3. **Reset Password Form**: Shows all fields and strength meter
4. **Strong Password**: Strength meter at maximum with all checks
5. **Success Message**: "Password Reset Successful!" message
6. **Backend Logs**: Showing "Email not configured" and reset link

---

## Troubleshooting

### Issue: Reset link not appearing
- **Solution**: Check that email service is NOT configured (confirm "Email not configured" in backend logs)
- **Check**: Open DevTools → Network tab → see response includes `dev_reset_link`

### Issue: Link is dead/doesn't work
- **Solution**: Make sure token in URL is complete (copy full link)
- **Check**: Look for token in backend logs to match

### Issue: Frontend not showing dev mode box
- **Solution**: Clear browser cache (Ctrl+Shift+Del) and reload
- **Check**: Make sure you're using updated ForgotPassword.jsx

### Issue: Backend not restarted with new code
- **Solution**: Kill Python and restart backend process
- **Check**: Look for log line showing when backend started

---

## Next Steps

Once testing is complete:
1. Document any issues found
2. Configure real email if needed (see FORGOT_PASSWORD_DEV_MODE.md)
3. Test with production email service
4. Update deployment configuration
