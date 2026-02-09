// Main App component that sets up React Router
// This component defines all the routes for the application
import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import AIMentor from './pages/AIMentor'
import Contests from './pages/Contests'
import Exam from './pages/Exam'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Admin from './pages/Admin'
import './App.css'

function App() {
  return (
    <Router>
      {/* Router wrapper enables navigation between pages */}
      <Routes>
        {/* Landing page route - the main homepage */}
        <Route path="/" element={<Landing />} />
        
        {/* AI Mentor page route */}
        <Route path="/ai-mentor" element={<AIMentor />} />
        
        {/* Contests page route */}
        <Route path="/contests" element={<Contests />} />
        
        {/* Exam page – opened when user clicks "Enter >>" on a contest */}
        <Route path="/exam/:code" element={<Exam />} />
        
        {/* Doubt Solver page route - currently reuses AI Mentor UI */}
        <Route path="/doubt-solver" element={<AIMentor />} />
        
        {/* Login page route */}
        <Route path="/login" element={<Login />} />
        
        {/* Sign Up page route */}
        <Route path="/signup" element={<SignUp />} />

        {/* Admin panel route – protected in Admin component */}
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Router>
  )
}

export default App
