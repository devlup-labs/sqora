// Sign Up page component
// Simple, styled registration form (UI only – no backend yet)
import React, { useState } from 'react'
import Header from '../components/Header'
import './Page.css'

function SignUp() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      alert('Passwords do not match.')
      return
    }

    // Placeholder – replace with real signup call later
    console.log('Signing up with:', { name, email, password })
    alert('Sign up submitted (demo only).')
  }

  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />
      
      {/* Main content area for Sign Up page */}
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Sign Up</h1>
          <p className="page-description">
            Create your SQORA account to get started with your learning journey.
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <h2 className="auth-form-title">Create your account</h2>

            <div className="auth-field">
              <label className="auth-label" htmlFor="signup-name">
                Full name
              </label>
              <input
                id="signup-name"
                className="auth-input"
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="signup-email">
                Email
              </label>
              <input
                id="signup-email"
                className="auth-input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="signup-password">
                Password
              </label>
              <input
                id="signup-password"
                className="auth-input"
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="signup-confirm-password">
                Confirm password
              </label>
              <input
                id="signup-confirm-password"
                className="auth-input"
                type="password"
                placeholder="Repeat your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            <div className="auth-actions">
              <button type="submit" className="auth-submit">
                Create account
              </button>
              <p className="auth-secondary-text">
                Already have an account?
                <a href="/login" className="auth-link">
                  Log in
                </a>
              </p>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}

export default SignUp
