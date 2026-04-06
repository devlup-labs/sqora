import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Page.css'

function Login() {
  const { loginWithGoogle } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGoogleSignIn = async () => {
    setError('')
    setLoading(true)
    try {
      await loginWithGoogle()
      navigate('/', { replace: true })
    } catch (err) {
      setError('Failed to sign in with Google. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Logo / Brand */}
        <div className="auth-brand">
          <span className="auth-brand-icon">⚡</span>
          <h1 className="auth-brand-name">SQORA</h1>
          <p className="auth-brand-tagline">Your AI-powered JEE &amp; NEET prep companion</p>
        </div>

        <div className="auth-divider" />

        <h2 className="auth-card-title">Welcome</h2>
        <p className="auth-card-subtitle">
          Sign in to access your personalised AI mentor, animated lessons, and more.
        </p>

        {error && (
          <div className="auth-error">
            <span>⚠️</span> {error}
          </div>
        )}

        <button
          id="google-signin-btn"
          className={`auth-google-btn${loading ? ' loading' : ''}`}
          onClick={handleGoogleSignIn}
          disabled={loading}
        >
          {loading ? (
            <span className="auth-spinner" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M44.5 20H24v8.5h11.8C34.7 33.9 29.7 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 5.1 29.6 3 24 3 12.4 3 3 12.4 3 24s9.4 21 21 21c10.5 0 20-7.8 20-21 0-1.4-.1-2.7-.5-4z" fill="#FFC107"/>
              <path d="M6.3 14.7l7 5.1C15.1 16.1 19.2 13 24 13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 5.1 29.6 3 24 3c-7.6 0-14.2 4.4-17.7 10.7z" fill="#FF3D00"/>
              <path d="M24 45c5.5 0 10.5-2 14.3-5.3l-6.6-5.6C29.7 35.9 26.9 37 24 37c-5.7 0-10.5-3.8-12.2-9l-7 5.3C8.3 40.8 15.5 45 24 45z" fill="#4CAF50"/>
              <path d="M44.5 20H24v8.5h11.8c-.9 2.8-2.7 5-5.1 6.6l6.6 5.6C41.3 37.2 45 31 45 24c0-1.4-.1-2.7-.5-4z" fill="#1976D2"/>
            </svg>
          )}
          {loading ? 'Signing in…' : 'Continue with Google'}
        </button>

        <p className="auth-footer-note">
          New to SQORA? Your account will be created automatically on first sign-in.
        </p>
      </div>
    </div>
  )
}

export default Login
