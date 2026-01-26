// MainContent component containing the radial gradient and feature cards
// This component displays the three main feature cards: AI Mentor, Contests, and Doubt Solver
// Uses React Router Link components to navigate to respective pages
// Reference: Based on the landing page design with soft blue circular glow in center
import React from 'react'
import { Link } from 'react-router-dom'
import './MainContent.css'

function MainContent() {
  return (
    <main className="main-content">
      {/* Soft blue circular glow - creates the center effect like in the photo */}
      {/* Reference: This matches the soft blue circle shown in the design image */}
      <div className="gradient-overlay"></div>
      
      {/* Feature cards container - holds all three clickable buttons */}
      {/* Reference: These cards are positioned around the center circle */}
      <div className="cards-container">
        {/* AI Mentor card - positioned in upper-left quadrant */}
        {/* Reference: Links to /ai-mentor page when clicked */}
        {/* Animation: Moves in curved path with pulse effect on hover */}
        <Link to="/ai-mentor" className="feature-card card-1">
          <h2 className="card-title">AI Mentor</h2>
        </Link>
        
        {/* Contests card - positioned in upper-right quadrant */}
        {/* Reference: Links to /contests page when clicked */}
        {/* Animation: Moves in curved path with pulse effect on hover */}
        <Link to="/contests" className="feature-card card-2">
          <h2 className="card-title">Contests</h2>
        </Link>
        
        {/* Doubt Solver card - positioned at bottom-center */}
        {/* Reference: Links to /doubt-solver page when clicked */}
        {/* Animation: Moves in curved path with pulse effect on hover */}
        <Link to="/doubt-solver" className="feature-card card-3">
          <h2 className="card-title">Doubt Solver</h2>
        </Link>
      </div>
    </main>
  )
}

export default MainContent
