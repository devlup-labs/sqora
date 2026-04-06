// Main App component that sets up React Router
import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import AIMentor from './pages/AIMentor'
import Contests from './pages/Contests'
import Exam from './pages/Exam'
import Login from './pages/Login'
import Admin from './pages/Admin'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './App.css'

/** Redirect authenticated users away from auth pages */
function PublicOnlyRoute({ children }) {
  const { currentUser } = useAuth()
  if (currentUser) {
    return <Navigate to="/" replace />
  }
  return children
}

/** Redirect unauthenticated users to login */
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
        <Routes>
          {/* Landing page */}
          <Route path="/" element={<Landing />} />

          {/* Auth — redirect to "/" if already logged in */}
          <Route
            path="/login"
            element={<PublicOnlyRoute><Login /></PublicOnlyRoute>}
          />
          {/* /signup is the same as /login — unified */}
          <Route path="/signup" element={<Navigate to="/login" replace />} />

          {/* Protected app routes */}
          <Route path="/ai-mentor"    element={<ProtectedRoute><AIMentor /></ProtectedRoute>} />
          <Route path="/contests"     element={<ProtectedRoute><Contests /></ProtectedRoute>} />
          <Route path="/exam/:code"   element={<ProtectedRoute><Exam /></ProtectedRoute>} />
          <Route path="/doubt-solver" element={<ProtectedRoute><AIMentor /></ProtectedRoute>} />
          <Route path="/admin"        element={<ProtectedRoute><Admin /></ProtectedRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
