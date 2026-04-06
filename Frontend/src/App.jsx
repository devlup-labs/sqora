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
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import './App.css'

function ProtectedRoute({ children }) {
  const { currentUser } = useAuth()
  if (!currentUser) {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  return (
    <AuthProvider>
      <Router>
        {/* Router wrapper enables navigation between pages */}
        <Routes>
          {/* Landing page route - the main homepage */}
          <Route path="/" element={<Landing />} />
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />

          {/* Main App Routes - Protected */}
          <Route path="/ai-mentor" element={<ProtectedRoute><AIMentor /></ProtectedRoute>} />
          <Route path="/contests" element={<ProtectedRoute><Contests /></ProtectedRoute>} />
          <Route path="/exam/:code" element={<ProtectedRoute><Exam /></ProtectedRoute>} />
          <Route path="/doubt-solver" element={<ProtectedRoute><AIMentor /></ProtectedRoute>} />
          
          {/* Admin panel route */}
          <Route path="/admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
