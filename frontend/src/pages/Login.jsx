import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Eye, EyeOff, Mail, Lock, Zap, ShieldCheck } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { verifyMFA } from '../services/api'
import '../styles/Login.css'

function Login() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [showMfa, setShowMfa] = useState(false)
  const [mfaToken, setMfaToken] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { login, login: authLogin } = useAuth()
  const navigate = useNavigate()

  const handleRoleRedirect = (user) => {
    if (user?.role === 'admin') {
      navigate('/admin')
    } else if (user?.role === 'recruiter') {
      navigate('/jobs')
    } else {
      navigate('/career-dashboard')
    }
  }

  const handlePasswordLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = await login(identifier, password)
      if (result.success) {
        if (result.mfa_required) {
          setShowMfa(true)
          setMfaToken(result.mfa_token)
          setInfo('Verification code sent to your email and phone.')
        } else {
          handleRoleRedirect(result.user)
        }
      } else {
        setError(result.error || 'Invalid credentials or account locked.')
      }
    } catch (err) {
      setError('Connection failed. Please check if the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleMfaVerify = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const response = await verifyMFA({ mfa_token: mfaToken, code: mfaCode })
      const { access_token, refresh_token, user } = response.data
      
      // Update AuthContext (we use authLogin as a shorthand to set tokens)
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      // We don't have a direct "set authenticated" in context easily from here 
      // without modifying context more, but authLogin is usually just handleLogin.
      // Let's reload or redirect which triggers checkAuth.
      handleRoleRedirect(user)
      window.location.reload() // Ensure context picks up the new state
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid or expired verification code.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container premium-page">
      <div className="decorative-blobs">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>
      <div className="login-card glass-panel premium-border">
        <div className="login-header">
          <h2>{showMfa ? 'Second Factor' : 'Welcome Back'}</h2>
          <p>{showMfa ? 'Verify your identity to continue' : 'Login to your Career Intelligence Hub'}</p>
        </div>

        {error && <div className="auth-alert error">{error}</div>}
        {info && <div className="auth-alert info">{info}</div>}

        {!showMfa ? (
          /* PASSWORD LOGIN */
          <form onSubmit={handlePasswordLogin}>
            <div className="form-group">
              <label><Mail size={16} /> Email or Username</label>
              <input
                type="text"
                name="identifier"
                autoComplete="username"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
                placeholder="email@example.com or username"
              />
            </div>

            <div className="form-group">
              <label><Lock size={16} /> Password</label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                />
                <button 
                  type="button" 
                  className="password-toggle" 
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <Link to="/forgot-password" style={{ display: 'block', margin: '0.5rem 0 1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Forgot Password?
            </Link>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Authenticating...' : 'Login with Password'}
            </button>
          </form>
        ) : (
          /* MFA VERIFICATION */
          <form onSubmit={handleMfaVerify}>
            <div className="form-group animate-slide-up">
              <div className="mfa-header-compact">
                <ShieldCheck size={28} className="mfa-icon" />
                <label>Secondary Verification Required</label>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: '1.5' }}>
                For your security, we've sent a <strong>6-digit code</strong> to your verified email and mobile device.
              </p>
              <div className="otp-input-container">
                <input
                  type="text"
                  value={mfaCode}
                  onChange={(e) => {
                    const val = e.target.value.replace(/\D/g, '');
                    if (val.length <= 6) setMfaCode(val);
                  }}
                  required
                  maxLength={6}
                  placeholder="000000"
                  className="otp-input"
                  autoFocus
                  autoComplete="one-time-code"
                />
              </div>
            </div>

            <button type="submit" className="btn-primary" disabled={loading || mfaCode.length !== 6}>
              {loading ? 'Verifying Identity...' : 'Confirm & Access Dashboard'}
            </button>
            
            <div className="mfa-footer">
              <span className="resend-text">Didn't receive the code?</span>
              <button 
                type="button" 
                className="btn-link-small" 
                onClick={() => { setShowMfa(false); setError(''); setInfo(''); }}
              >
                Go back & try again
              </button>
            </div>
          </form>
        )}

        <p className="signup-link">
          Don't have an account? <Link to="/signup">Sign up for free</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
