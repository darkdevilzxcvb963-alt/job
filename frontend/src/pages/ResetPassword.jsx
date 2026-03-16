import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import PasswordStrengthMeter from '../components/PasswordStrengthMeter'
import '../styles/ResetPassword.css'

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [validating, setValidating] = useState(true)
  const [tokenValid, setTokenValid] = useState(false)
  const [expiresIn, setExpiresIn] = useState(null)
  const { resetPassword } = useAuth()
  const token = searchParams.get('token')

  useEffect(() => {
    // Validate token on component mount
    const validateToken = async () => {
      if (!token) {
        setError('Invalid reset link. Please request a new password reset.')
        setTokenValid(false)
        setValidating(false)
        return
      }

      try {
        // Use central API service to validate token
        const { validateResetToken } = await import('../services/api')
        const response = await validateResetToken(token)

        setTokenValid(true)
        setExpiresIn(Math.ceil(response.data.expires_in_hours * 60)) // Convert to minutes
      } catch (err) {
        console.error('Token validation error:', err)
        const errorMessage = err.response?.data?.detail || 'Invalid or expired reset token'
        setError(errorMessage)
        setTokenValid(false)
      } finally {
        setValidating(false)
      }
    }

    validateToken()
  }, [token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation checks
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    if (!/[a-z]/.test(password)) {
      setError('Password must contain at least one lowercase letter')
      return
    }

    if (!/[A-Z]/.test(password)) {
      setError('Password must contain at least one uppercase letter')
      return
    }

    if (!/\d/.test(password)) {
      setError('Password must contain at least one number')
      return
    }

    setLoading(true)

    const result = await resetPassword(token, password)

    if (result.success) {
      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  if (validating) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Validating reset link...</p>
          </div>
        </div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card">
          <h2>✓ Password Reset Successful!</h2>
          <div className="success-message">
            <p>Your password has been reset successfully.</p>
            <p>You will be redirected to the login page in a moment...</p>
          </div>
          <Link to="/login" className="back-to-login">Go to Login Now</Link>
        </div>
      </div>
    )
  }

  if (!tokenValid) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card">
          <h2>Invalid Reset Link</h2>
          <div className="error-message">
            <p>This password reset link is invalid or has expired.</p>
            <p>Please request a new password reset to set a new password.</p>
          </div>
          <Link to="/forgot-password" className="action-button">Request New Reset Link</Link>
          <Link to="/login" className="back-to-login">Back to Login</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="reset-password-container">
      <div className="reset-password-card">
        <h2>Reset Password</h2>
        <p className="subtitle">Create a strong new password for your account.</p>

        {expiresIn && (
          <div className="info-banner">
            <span className="clock-icon">⏱</span>
            <span>Reset link expires in <strong>{expiresIn} minutes</strong></span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠</span>
              {error}
            </div>
          )}

          <div className="form-group">
            <label>New Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              placeholder="At least 8 characters"
              disabled={loading}
            />
            <small>Must be at least 8 characters with letters and numbers</small>
          </div>

          {password && <PasswordStrengthMeter password={password} />}

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
              placeholder="Confirm your password"
              disabled={loading}
            />
            {password && confirmPassword && password === confirmPassword && (
              <small className="match-success">✓ Passwords match</small>
            )}
            {password && confirmPassword && password !== confirmPassword && (
              <small className="match-error">✗ Passwords don't match</small>
            )}
          </div>

          <button type="submit" disabled={loading || !password || !confirmPassword}>
            {loading ? (
              <>
                <span className="spinner-inline"></span>
                Resetting...
              </>
            ) : (
              'Reset Password'
            )}
          </button>

          <Link to="/login" className="back-to-login">Back to Login</Link>
        </form>
      </div>
    </div>
  )
}

export default ResetPassword
