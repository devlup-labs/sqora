// Login page component
// Simple, styled login form (UI only – no backend yet)
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { ROLE_KEY } from '../authConfig'
import './Page.css'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || 'Login failed.')
        return
      }

      const data = await res.json()
      localStorage.setItem(ROLE_KEY, data.role)

      if (data.role === 'admin') {
        navigate('/admin')
      } else {
        navigate('/')
      }
    } catch (err) {
      console.error('Login error:', err)
      alert('Could not reach the server.')
    }
  }

  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />

      {/* Main content area for Login page */}
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Log In</h1>
          <p className="page-description">
            Access your SQORA account to continue with your preparation.
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <h2 className="auth-form-title">Welcome back</h2>

            <div className="auth-field">
              <label className="auth-label" htmlFor="login-email">
                Email
              </label>
              <input
                id="login-email"
                className="auth-input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="login-password">
                Password
              </label>
              <input
                id="login-password"
                className="auth-input"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            <div className="auth-actions">
              <button type="submit" className="auth-submit">
                Log In
              </button>
              <p className="auth-secondary-text">
                Don&apos;t have an account?
                <a href="/signup" className="auth-link">
                  Sign up
                </a>
              </p>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}

export default Login
