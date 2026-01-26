// AI Mentor page component
// This is a simple page for the AI Mentor feature - will be expanded later
import React from 'react'
import Header from '../components/Header'
import './Page.css'

function AIMentor() {
  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />
      
      {/* Main content area for AI Mentor page */}
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">AI Mentor</h1>
          <p className="page-description">
            Welcome to AI Mentor. This page will be developed further.
          </p>
        </div>
      </main>
    </div>
  )
}

export default AIMentor
