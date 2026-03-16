import React from 'react'
import '../styles/PasswordStrengthMeter.css'

function PasswordStrengthMeter({ password }) {
  const calculateStrength = (pwd) => {
    let strength = 0
    const checks = {
      length: pwd.length >= 8,
      hasLower: /[a-z]/.test(pwd),
      hasUpper: /[A-Z]/.test(pwd),
      hasNumber: /\d/.test(pwd),
      hasSpecial: /[!@#$%^&*]/.test(pwd)
    }

    // Count met criteria
    Object.values(checks).forEach(check => {
      if (check) strength++
    })

    return {
      score: strength,
      checks,
      level: strength <= 1 ? 'weak' : strength <= 2 ? 'fair' : strength <= 3 ? 'good' : strength <= 4 ? 'strong' : 'very-strong',
      percentage: (strength / 5) * 100
    }
  }

  if (!password) {
    return null
  }

  const strength = calculateStrength(password)

  return (
    <div className="password-strength-meter">
      <div className="strength-bar">
        <div
          className={`strength-fill strength-${strength.level}`}
          style={{ width: `${strength.percentage}%` }}
        ></div>
      </div>
      <div className="strength-label">
        <span className={`label-text strength-${strength.level}`}>
          Strength: <strong>{strength.level.charAt(0).toUpperCase() + strength.level.slice(1)}</strong>
        </span>
      </div>
      
      <ul className="strength-criteria">
        <li className={strength.checks.length ? 'met' : 'unmet'}>
          <span className="check-icon">
            {strength.checks.length ? '✓' : '○'}
          </span>
          At least 8 characters
        </li>
        <li className={strength.checks.hasLower ? 'met' : 'unmet'}>
          <span className="check-icon">
            {strength.checks.hasLower ? '✓' : '○'}
          </span>
          Lowercase letter (a-z)
        </li>
        <li className={strength.checks.hasUpper ? 'met' : 'unmet'}>
          <span className="check-icon">
            {strength.checks.hasUpper ? '✓' : '○'}
          </span>
          Uppercase letter (A-Z)
        </li>
        <li className={strength.checks.hasNumber ? 'met' : 'unmet'}>
          <span className="check-icon">
            {strength.checks.hasNumber ? '✓' : '○'}
          </span>
          Number (0-9)
        </li>
        <li className={strength.checks.hasSpecial ? 'met' : 'unmet'}>
          <span className="check-icon">
            {strength.checks.hasSpecial ? '✓' : '○'}
          </span>
          Special character (!@#$%^&*)
        </li>
      </ul>
    </div>
  )
}

export default PasswordStrengthMeter
