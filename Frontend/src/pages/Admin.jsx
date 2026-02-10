import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import { ROLE_KEY } from '../authConfig'
import './Page.css'
import './Admin.css'

function Admin() {
  const navigate = useNavigate()
  const [config, setConfig] = useState({
    mentorGreeting: '',
    voiceEnabled: true,
    highlightedExam: '',
    showContestsOnHome: true,
    aiOnlyAnswers: true,
    flagSensitive: false,
  })

  useEffect(() => {
    const role = localStorage.getItem(ROLE_KEY)
    if (role !== 'admin') {
      navigate('/login')
      return
    }
    fetch('/api/admin/config')
      .then((res) => res.json())
      .then((data) => setConfig((prev) => ({ ...prev, ...data })))
      .catch((err) => console.error('Failed to load admin config:', err))
  }, [navigate])

  const updateConfig = (patch) => {
    const next = { ...config, ...patch }
    setConfig(next)
    fetch('/api/admin/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    }).catch((err) => console.error('Failed to save admin config:', err))
  }

  return (
    <div className="app admin-page">
      <Header />

      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">Admin Panel</h1>
          <p className="page-description">
            Configure your SQORA experience here. Changes are saved to the
            backend automatically.
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
                  value={config.mentorGreeting}
                  onChange={(e) => updateConfig({ mentorGreeting: e.target.value })}
                />
              </label>
              <label className="admin-field-label admin-inline">
                <span>Enable voice replies</span>
                <input
                  type="checkbox"
                  checked={config.voiceEnabled}
                  onChange={(e) => updateConfig({ voiceEnabled: e.target.checked })}
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
                  value={config.highlightedExam}
                  onChange={(e) => updateConfig({ highlightedExam: e.target.value })}
                />
              </label>
              <label className="admin-field-label admin-inline">
                <span>Show contests on home</span>
                <input
                  type="checkbox"
                  checked={config.showContestsOnHome}
                  onChange={(e) => updateConfig({ showContestsOnHome: e.target.checked })}
                />
              </label>
            </section>

            <section className="admin-card">
              <h2 className="admin-card-title">Doubt Solver & Safety</h2>
              <p className="admin-card-subtitle">
                Configure how doubts are routed and reviewed.
              </p>
              <label className="admin-field-label admin-inline">
                <span>Enable AI-only answers</span>
                <input
                  type="checkbox"
                  checked={config.aiOnlyAnswers}
                  onChange={(e) => updateConfig({ aiOnlyAnswers: e.target.checked })}
                />
              </label>
              <label className="admin-field-label admin-inline">
                <span>Flag sensitive questions for manual review</span>
                <input
                  type="checkbox"
                  checked={config.flagSensitive}
                  onChange={(e) => updateConfig({ flagSensitive: e.target.checked })}
                />
              </label>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Admin

