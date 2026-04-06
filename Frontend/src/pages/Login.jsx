import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { useAuth } from '../contexts/AuthContext'
import './Page.css'

function Login() {
  const { loginWithGoogle } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  const handleGoogleLogin = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await loginWithGoogle()
      navigate('/')
    } catch (err) {
      setError('Failed to log in with Google.')
      console.error(err)
    }
  }

  return (
    <div className="app">
      <Header />
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Log In</h1>
          <p className="page-description">
            Access your SQORA account to continue with your preparation.
          </p>

          <form className="auth-form">
            <h2 className="auth-form-title">Welcome back</h2>
            
            {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

            <div className="auth-actions" style={{ marginTop: '1rem' }}>
              <button type="button" onClick={handleGoogleLogin} className="auth-submit">
                Sign in with Google
              </button>
            </div>
            
            <div className="auth-actions" style={{ marginTop: '1rem' }}>
              <p className="auth-secondary-text">
                Don&apos;t have an account?
                <a href="/signup" className="auth-link" style={{ marginLeft: '0.5rem' }}>
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
