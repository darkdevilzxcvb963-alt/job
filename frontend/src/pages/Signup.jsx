import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import { Eye, EyeOff, ShieldCheck } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { verifyMFA } from '../services/api'
import '../styles/Signup.css'

function Signup() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    username: '',
    phone: '',
    password: '',
    confirm_password: '',
    role: 'job_seeker'
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [showMfa, setShowMfa] = useState(false)
  const [mfaCode, setMfaCode] = useState('')
  const [mfaToken, setMfaToken] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const { signup, loginWithGoogle } = useAuth()
  const navigate = useNavigate()

  // Form validation rules
  const validateForm = () => {
    const newErrors = {}

    // Full Name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required'
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters'
    } else if (formData.full_name.trim().length > 255) {
      newErrors.full_name = 'Full name must not exceed 255 characters'
    } else if (!/^[a-zA-Z\s\-']+$/.test(formData.full_name.trim())) {
      newErrors.full_name = 'Full name can only contain letters, spaces, hyphens, and apostrophes'
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!emailRegex.test(formData.email.trim())) {
      newErrors.email = 'Please enter a valid email address'
    }

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required'
    } else if (formData.username.trim().length < 3) {
      newErrors.username = 'Username must be at least 3 characters'
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username.trim())) {
      newErrors.username = 'Username can only contain letters, numbers, and underscores'
    }

    // Phone validation (optional but if provided must be valid)
    if (formData.phone.trim()) {
      if (formData.phone.trim().length < 10) {
        newErrors.phone = 'Phone number must be at least 10 characters'
      } else if (formData.phone.trim().length > 50) {
        newErrors.phone = 'Phone number must not exceed 50 characters'
      } else if (!/^[0-9\s\-\(\)\+]*$/.test(formData.phone.trim())) {
        newErrors.phone = 'Phone number can only contain digits, spaces, hyphens, parentheses, and plus sign'
      }
    }

    // Password validation (Strong)
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    } else if (formData.password.length > 100) {
      newErrors.password = 'Password must not exceed 100 characters'
    } else if (!/\d/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one digit (0-9)'
    } else if (!/[a-zA-Z]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one letter'
    } else if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one special character (!@#$%^&*)'
    }

    // Confirm password validation
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password'
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match'
    }

    // Role validation
    if (!formData.role) {
      newErrors.role = 'Please select your role'
    }

    return newErrors
  }

  const calculatePasswordStrength = (password) => {
    let score = 0
    if (password.length >= 8) score++
    if (password.length >= 12) score++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
    if (/\d/.test(password)) score++
    if (/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password)) score++
    return score
  }

  const getStrengthLabel = (score) => {
    if (score <= 1) return { label: 'Weak', color: '#f87171' }
    if (score <= 2) return { label: 'Fair', color: '#fbbf24' }
    if (score <= 4) return { label: 'Good', color: '#38bdf8' }
    return { label: 'Strong', color: '#4ade80' }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)

    // Validate form
    const validationErrors = validateForm()
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      setLoading(false)
      return
    }

    // Prepare data for API (don't send confirm_password)
    const signupData = {
      full_name: formData.full_name.trim(),
      email: formData.email.trim(),
      username: formData.username.trim(),
      phone: formData.phone.trim() || null,
      password: formData.password,
      role: formData.role
    }

    const result = await signup(signupData)

    if (result.success) {
      const respData = result.data;
      if (respData.mfa_required) {
        setMfaToken(respData.mfa_token)
        setShowMfa(true)
        setSuccessMessage('Account created! Please verify your identity with the OTP sent to your email.')
      } else {
        setSuccess(true)
        setSuccessMessage(`Welcome! Your account has been created successfully. Redirecting to login...`)
        setTimeout(() => navigate('/login'), 2000)
      }
    } else {
      setErrors({ submit: result.error || 'Signup failed. Please try again.' })
    }
    setLoading(false)
  }

  const handleMfaVerify = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      const response = await verifyMFA({ mfa_token: mfaToken, code: mfaCode })
      const { access_token, refresh_token, user } = response.data
      
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      setSuccess(true)
      setSuccessMessage(`Verification successful! Welcome, ${user.full_name}.`)
      
      setTimeout(() => {
        if (user.role === 'admin') navigate('/admin')
        else if (user.role === 'recruiter') navigate('/jobs')
        else navigate('/candidate')
        window.location.reload()
      }, 2000)
    } catch (err) {
      setErrors({ mfa: err.response?.data?.detail || 'Invalid or expired verification code.' })
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true)
    setErrors({})

    const result = await loginWithGoogle(credentialResponse.credential, formData.role)

    if (result.success) {
      // Check if MFA is required (for new Google signups)
      if (result.mfa_required) {
        setMfaToken(result.mfa_token)
        setShowMfa(true)
      } else {
        setSuccess(true)
        setSuccessMessage(`Welcome! You've successfully signed up with Google.`)
        setTimeout(() => {
          if (result.user.role === 'admin') navigate('/admin')
          else if (result.user.role === 'recruiter') navigate('/jobs')
          else navigate('/candidate')
        }, 2000)
      }
    } else {
      setErrors({ submit: result.error })
    }
    setLoading(false)
  }

  const handleGoogleError = () => {
    setErrors({ submit: 'Google Sign-in failed. Please try again.' })
  }

  if (success) {
    return (
      <div className="signup-container">
        <div className="signup-card">
          <div className="success-card">
            <h2>✓ Registration Successful!</h2>
            <div className="success-message">
              <p>{successMessage}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="signup-container premium-page">
      <div className="decorative-blobs">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>
      <div className="signup-card glass-panel premium-border">
        <h2>Create Your Account</h2>
        <p className="subtitle">Join our resume matching platform</p>

        <form onSubmit={handleSubmit}>
          {errors.submit && <div className="error-banner">{errors.submit}</div>}

          <div className="form-group">
            <label htmlFor="full_name">Full Name *</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="e.g., John Doe"
              required
              className={errors.full_name ? 'input-error' : ''}
            />
            {errors.full_name && <span className="field-error">{errors.full_name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="e.g., john@example.com"
              required
              className={errors.email ? 'input-error' : ''}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>
          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="e.g., johndoe_123"
              required
              className={errors.username ? 'input-error' : ''}
            />
            {errors.username && <span className="field-error">{errors.username}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone (Optional)</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="e.g., +1 (555) 123-4567"
              className={errors.phone ? 'input-error' : ''}
            />
            {errors.phone && <span className="field-error">{errors.phone}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="At least 8 characters"
                required
                minLength={8}
                className={errors.password ? 'input-error' : ''}
              />
              <button 
                type="button" 
                className="password-toggle" 
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.password && <span className="field-error">{errors.password}</span>}
            

          </div>

          <div className="form-group">
            <label htmlFor="confirm_password">Confirm Password *</label>
            <div className="password-input-wrapper">
              <input
                type={showConfirmPassword ? "text" : "password"}
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="Re-enter your password"
                required
                className={errors.confirm_password ? 'input-error' : ''}
              />
              <button 
                type="button" 
                className="password-toggle" 
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.confirm_password && <span className="field-error">{errors.confirm_password}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="role">Account Type *</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              className={errors.role ? 'input-error' : ''}
            >
              <option value="">-- Select Account Type --</option>
              <option value="job_seeker">Job Seeker / Candidate</option>
              <option value="recruiter">Recruiter / Employer</option>
            </select>
            {errors.role && <span className="field-error">{errors.role}</span>}
          </div>


          {!showMfa ? (
            <>
              <button
                type="submit"
                disabled={loading}
                className="submit-button"
              >
                {loading ? 'Creating Account...' : 'Sign Up'}
              </button>
              
              <div className="google-divider">OR</div>
              <div className="google-login-container">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={handleGoogleError}
                  text="signup_with"

                  theme="outline"
                  size="large"
                  width="100%"
                />
              </div>
            </>
          ) : (
            <div className="mfa-signup-section animate-slide-up">
              <div className="mfa-header-compact">
                <ShieldCheck size={32} className="mfa-icon" />
                <label>Verify Your Account</label>
              </div>
              <p className="mfa-instruction">
                We've sent a 6-digit code to your email to complete your registration.
              </p>
              
              {errors.mfa && <div className="field-error">{errors.mfa}</div>}
              
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
                />
              </div>

              <button 
                type="button" 
                className="submit-button"
                onClick={handleMfaVerify}
                disabled={loading || mfaCode.length !== 6}
              >
                {loading ? 'Verifying...' : 'Complete Registration'}
              </button>
              
              <button 
                type="button" 
                className="btn-link-small" 
                style={{ marginTop: '1rem', width: '100%' }}
                onClick={() => setShowMfa(false)}
              >
                Back to signup
              </button>
            </div>
          )}

          <div className="form-footer">
            <p>Already have an account? <Link to="/login">Login here</Link></p>
          </div>        </form>
      </div>
    </div>
  )
}

export default Signup