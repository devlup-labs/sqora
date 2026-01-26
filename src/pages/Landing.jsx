// Landing page component - the main homepage
// This is the default page that displays the three feature cards and rotating sphere
import React from 'react'
import Header from '../components/Header'
import MainContent from '../components/MainContent'
import '../App.css'

function Landing() {
  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />
      
      {/* Main content area with gradient and feature cards */}
      <MainContent />
    </div>
  )
}

export default Landing
