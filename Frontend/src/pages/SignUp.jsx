import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { useAuth } from '../contexts/AuthContext'
import './Page.css'

function SignUp() {
  const { loginWithGoogle } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  const handleGoogleSignup = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await loginWithGoogle()
      navigate('/')
    } catch (err) {
      setError('Failed to sign up with Google.')
      console.error(err)
    }
  }

  return (
    <div className="app">
      <Header />
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Sign Up</h1>
          <p className="page-description">
            Create your SQORA account using Google Auth to get started with your learning journey.
          </p>

          <form className="auth-form">
            <h2 className="auth-form-title">Create your account</h2>

            {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

            <div className="auth-actions" style={{ marginTop: '1rem' }}>
              <button type="button" onClick={handleGoogleSignup} className="auth-submit">
                Sign up with Google
              </button>
            </div>

            <div className="auth-actions" style={{ marginTop: '1rem' }}>
              <p className="auth-secondary-text">
                Already have an account?
                <a href="/login" className="auth-link" style={{ marginLeft: '0.5rem' }}>
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
