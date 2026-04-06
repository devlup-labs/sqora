import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Header.css'

function Header() {
  const { currentUser, logout } = useAuth()

  return (
    <header className="header">
      {/* Logo section with SQORA text and blue dot indicator */}
      {/* Reference: Logo links to landing page (/) when clicked */}
      {/* Animation: Logo has hover effect for better interactivity */}
      <Link to="/" className="logo-link">
        <div className="logo-container">
          <span className="logo-dot"></span> {/* Blue dot positioned above the Q */}
          <h1 className="logo-text">SQORA</h1>
        </div>
      </Link>
      
      {/* Authentication buttons section */}
      {/* Reference: Buttons are clickable and navigate to respective pages */}
      {/* Animation: Buttons have hover and active state animations */}
      <div className="auth-buttons">
        {currentUser ? (
          <button onClick={logout} className="btn btn-secondary">
            Log Out ({currentUser.displayName?.split(' ')[0] || 'User'})
          </button>
        ) : (
          <>
            {/* Primary Log In button with blue background */}
            {/* Reference: Links to /login page when clicked */}
            <Link to="/login" className="btn btn-primary">
              Log In
            </Link>
            
            {/* Secondary Sign Up button with gray background */}
            {/* Reference: Links to /signup page when clicked */}
            <Link to="/signup" className="btn btn-secondary">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </header>
  )
}

export default Header
