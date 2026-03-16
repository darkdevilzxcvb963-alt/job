import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../styles/ForgotPassword.css'

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [emailSent, setEmailSent] = useState('')
  const [devResetLink, setDevResetLink] = useState('')
  const { forgotPassword } = useAuth()

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validate email format
    if (!email.trim()) {
      setError('Please enter your email address')
      return
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address')
      return
    }

    setLoading(true)

    const result = await forgotPassword(email)

    if (result.success) {
      setSuccess(true)
      setEmailSent(email)
      setDevResetLink(result.dev_reset_link || '')
      // Auto-clear form
      setEmail('')
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  if (success) {
    return (
      <div className="forgot-password-container">
        <div className="forgot-password-card">
          <h2>✓ Check Your Email</h2>
          <div className="success-message">
            <p>If an account exists with <strong>{emailSent}</strong>, we've sent a password reset link.</p>
            <p>Please check your email (including spam folder) and follow the instructions.</p>
            <div className="email-tips">
              <strong>Tips:</strong>
              <ul>
                <li>Check your spam/junk folder if you don't see the email</li>
                <li>The reset link will expire in 24 hours</li>
                <li>Click the link to proceed with password reset</li>
              </ul>
            </div>
          </div>

          {devResetLink && (
            <div className="dev-mode-notice">
              <strong>⚙️ Development Mode:</strong>
              <p>Email service is not configured. Use this link to reset your password:</p>
              <div className="dev-link-box">
                <a href={devResetLink} className="dev-reset-button" target="_self">
                  Click Here to Reset Password
                </a>
                <p className="copy-hint">Or copy this link:</p>
                <code className="dev-link-code">{devResetLink}</code>
                <button
                  className="copy-button"
                  onClick={() => {
                    navigator.clipboard.writeText(devResetLink)
                    alert('Link copied to clipboard!')
                  }}
                >
                  Copy Link
                </button>
              </div>
            </div>
          )}

          <button
            className="reset-button"
            onClick={() => setSuccess(false)}
          >
            Try Another Email
          </button>
          <Link to="/login" className="back-to-login">Back to Login</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <h2>Forgot Password</h2>
        <p className="subtitle">Enter your email address and we'll send you a secure link to reset your password.</p>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠</span>
              {error}
            </div>
          )}

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your.email@example.com"
              disabled={loading}
              autoComplete="email"
            />
            <small>We'll never share your email address</small>
          </div>

          <button type="submit" disabled={loading || !email.trim()}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Sending...
              </>
            ) : (
              'Send Reset Link'
            )}
          </button>

          <div className="info-box">
            <p><strong>How it works:</strong></p>
            <ol>
              <li>Enter your email address</li>
              <li>We'll send you a secure reset link</li>
              <li>Click the link and set a new password</li>
              <li>Log in with your new password</li>
            </ol>
          </div>

          <Link to="/login" className="back-to-login">Back to Login</Link>
        </form>
      </div>
    </div>
  )
}

export default ForgotPassword
