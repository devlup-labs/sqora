// Login page component
// This is a simple page for user login - will be expanded later
import React from 'react'
import Header from '../components/Header'
import './Page.css'

function Login() {
  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />
      
      {/* Main content area for Login page */}
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Log In</h1>
          <p className="page-description">
            Welcome to the Login page. This page will be developed further.
          </p>
        </div>
      </main>
    </div>
  )
}

export default Login
