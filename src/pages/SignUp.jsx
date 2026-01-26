// Sign Up page component
// This is a simple page for user registration - will be expanded later
import React from 'react'
import Header from '../components/Header'
import './Page.css'

function SignUp() {
  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />
      
      {/* Main content area for Sign Up page */}
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Sign Up</h1>
          <p className="page-description">
            Welcome to the Sign Up page. This page will be developed further.
          </p>
        </div>
      </main>
    </div>
  )
}

export default SignUp
