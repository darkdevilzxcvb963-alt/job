import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../styles/VerifyEmail.css'

function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const { verifyEmail } = useAuth()
  const token = searchParams.get('token')

  useEffect(() => {
    if (token) {
      handleVerify()
    } else {
      // If no token provided and using simplified auth, redirect to login
      setMessage('Using simplified authentication - no email verification required.')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    }
  }, [token, navigate])

  const handleVerify = async () => {
    if (!token) {
      setError('No verification token provided')
      return
    }

    setLoading(true)
    setError('')

    const result = await verifyEmail(token)
    
    if (result.success) {
      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  if (success) {
    return (
      <div className="verify-email-container">
        <div className="verify-email-card">
          <div className="success-icon">✓</div>
          <h2>Email Verified!</h2>
          <div className="success-message">
            <p>Your email has been successfully verified.</p>
            <p>You can now access all features of the platform.</p>
            <p>Redirecting to login...</p>
          </div>
          <Link to="/login" className="back-to-login">Go to Login</Link>
        </div>
      </div>
    )
  }

  if (message) {
    return (
      <div className="verify-email-container">
        <div className="verify-email-card">
          <h2>Email Verification</h2>
          <div className="info-message">
            <p>{message}</p>
            <p>Redirecting to login...</p>
          </div>
          <Link to="/login" className="back-to-login">Go to Login</Link>
        </div>
      </div>
    )
  }

  if (!token) {
    return (
      <div className="verify-email-container">
        <div className="verify-email-card">
          <h2>Email Verification</h2>
          <div className="error-message">
            <p>No verification token provided.</p>
            <p>Please check your email for the verification link.</p>
          </div>
          <Link to="/login" className="back-to-login">Go to Login</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="verify-email-container">
      <div className="verify-email-card">
        <h2>Verifying Email</h2>
        {loading && <div className="loading-spinner">Verifying...</div>}
        {error && (
          <>
            <div className="error-message">
              <p>{error}</p>
              <p>The verification link may have expired. Please request a new one.</p>
            </div>
            <Link to="/login" className="back-to-login">Go to Login</Link>
          </>
        )}
      </div>
    </div>
  )
}

export default VerifyEmail
