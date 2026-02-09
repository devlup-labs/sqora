import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { ROLE_KEY } from '../authConfig'
import { useAppConfig } from '../store/useAppConfig'
import './Page.css'
import './Admin.css'

function Admin() {
  const navigate = useNavigate()
  const {
    mentorGreeting,
    voiceEnabled,
    setMentorGreeting,
    setVoiceEnabled,
  } = useAppConfig()

  useEffect(() => {
    const role = localStorage.getItem(ROLE_KEY)
    if (role !== 'admin') {
      navigate('/login')
    }
  }, [navigate])

  return (
    <div className="app admin-page">
      <Header />

      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Admin Panel</h1>
          <p className="page-description">
            Configure your SQORA experience here. This is a demo UI – later you
            can connect it to your backend to persist changes.
          </p>

          <div className="admin-grid">
            <section className="admin-card">
              <h2 className="admin-card-title">Mentor Settings</h2>
              <p className="admin-card-subtitle">
                Control how the AI mentor greets and responds to students.
              </p>
              <label className="admin-field-label">
                Default greeting message
                <input
                  className="admin-input"
                  type="text"
                  placeholder="Hi, I am your AI mentor. How can I help you today?"
                  value={mentorGreeting}
                  onChange={(e) => setMentorGreeting(e.target.value)}
                />
              </label>
              <label className="admin-field-label admin-inline">
                <span>Enable voice replies</span>
                <input
                  type="checkbox"
                  checked={voiceEnabled}
                  onChange={(e) => setVoiceEnabled(e.target.checked)}
                />
              </label>
            </section>

            <section className="admin-card">
              <h2 className="admin-card-title">Exam & Contest Controls</h2>
              <p className="admin-card-subtitle">
                Plan upcoming tests, difficulty levels, and visibility.
              </p>
              <label className="admin-field-label">
                Highlighted upcoming exam
                <input
                  className="admin-input"
                  type="text"
                  placeholder="JEE Main Mock Test – Sunday 9 AM"
                />
              </label>
              <label className="admin-field-label admin-inline">
                <span>Show contests on home</span>
                <input type="checkbox" defaultChecked />
              </label>
            </section>

            <section className="admin-card">
              <h2 className="admin-card-title">Doubt Solver & Safety</h2>
              <p className="admin-card-subtitle">
                Configure how doubts are routed and reviewed.
              </p>
              <label className="admin-field-label admin-inline">
                <span>Enable AI-only answers</span>
                <input type="checkbox" defaultChecked />
              </label>
              <label className="admin-field-label admin-inline">
                <span>Flag sensitive questions for manual review</span>
                <input type="checkbox" />
              </label>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Admin

