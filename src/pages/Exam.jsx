// Exam page – shown when user clicks "Enter >>" on a contest
// Layout: header (title, timer, sun/moon toggle), subject tabs, question area + sidebar, bottom buttons
// Theme: SQORA colors; sun/moon toggles light/dark mode
import React, { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import './Exam.css'

// Mock contest title by code; in real app, fetch from API
const contestTitleByCode = {
  'JEE-M1': 'JEE Main 2025 (Online) 8th April Evening Shift',
  'NEET-P1': 'NEET 2025 Previous Year Paper 1',
  'JEE-A1': 'JEE Advanced Mock 1',
  'NEET-M1': 'NEET Mock 1 – Physics, Chemistry, Biology',
  'JEE-M2': 'JEE Main Mock 2 – PCM',
  'NEET-M2': 'NEET Mock 2 – Full syllabus',
}

const SUBJECTS = ['Chemistry', 'Physics', 'Mathematics']
const QUESTIONS_PER_SUBJECT = 25

// Sample MCQ
const SAMPLE_QUESTION = {
  id: 1,
  type: 'MCQ Single Answer',
  text: 'The atomic number of the element from the following with lowest 1st ionisation enthalpy is:',
  options: [
    { key: 'A', value: '32' },
    { key: 'B', value: '35' },
    { key: 'C', value: '19' },
    { key: 'D', value: '87' },
  ],
}

function Exam() {
  const { code } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const title = state?.name || contestTitleByCode[code] || `${code} – Contest`

  const [darkMode, setDarkMode] = useState(() => {
    try {
      return localStorage.getItem('sqora-exam-theme') !== 'light'
    } catch {
      return true
    }
  })
  const [subject, setSubject] = useState(0)
  const [qIndex, setQIndex] = useState(0)
  const [selected, setSelected] = useState(null)
  const [status, setStatus] = useState({})
  const [timeLeft, setTimeLeft] = useState(2 * 60 * 60 + 56 * 60 + 25)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    if (paused) return
    const t = setInterval(() => {
      setTimeLeft((prev) => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(t)
  }, [paused])

  useEffect(() => {
    localStorage.setItem('sqora-exam-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const toggleTheme = () => setDarkMode((d) => !d)
  const formatTime = (s) => {
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    const n = s % 60
    return [h, m, n].map((x) => String(x).padStart(2, '0')).join(':')
  }

  const qKey = `${subject}-${qIndex}`
  const markSeen = (s, q) => {
    const k = `${s}-${q}`
    setStatus((prev) => ({ ...prev, [k]: prev[k] === 'attempted' || prev[k] === 'attempted-marked' ? prev[k] : 'seen' }))
  }
  const markAttempted = () => {
    setStatus((prev) => ({ ...prev, [qKey]: 'attempted' }))
  }
  const goTo = (s, q) => {
    setSubject(s)
    setQIndex(q)
    markSeen(s, q)
    setSidebarOpen(false)
  }

  return (
    <div className={`exam-page ${darkMode ? 'exam-dark' : 'exam-light'}`}>
      <header className="exam-header">
        <div className="exam-header-center">
          <h1 className="exam-title">{title}</h1>
          <div className="exam-timer">{formatTime(timeLeft)}</div>
        </div>
        <div className="exam-header-actions">
          <button
            type="button"
            className="exam-btn-pause-resume"
            onClick={() => setPaused((p) => !p)}
            aria-label={paused ? 'Resume' : 'Pause'}
          >
            {paused ? 'Resume' : 'Pause'}
          </button>
          <button type="button" className="exam-header-btn" aria-label="Fullscreen">
            <span className="exam-header-icon">⛶</span>
          </button>
          <button type="button" className="exam-header-btn" aria-label="Instructions">
            <span className="exam-header-icon">💡</span>
          </button>
          <button
            type="button"
            className="exam-header-btn exam-theme-toggle"
            onClick={toggleTheme}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            title={darkMode ? 'Light mode' : 'Dark mode'}
          >
            {darkMode ? (
              <svg className="exam-icon-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <circle cx="12" cy="12" r="5" />
                <line x1="12" y1="1" x2="12" y2="3" />
                <line x1="12" y1="21" x2="12" y2="23" />
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                <line x1="1" y1="12" x2="3" y2="12" />
                <line x1="21" y1="12" x2="23" y2="12" />
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
              </svg>
            ) : (
              <svg className="exam-icon-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
          <button type="button" className="exam-header-btn" aria-label="Settings">
            <span className="exam-header-icon">⚙</span>
          </button>
          <button
            type="button"
            className="exam-header-btn exam-hamburger"
            onClick={() => setSidebarOpen((o) => !o)}
            aria-label="Toggle question list"
            aria-expanded={sidebarOpen}
          >
            <span className="exam-hamburger-lines" />
          </button>
        </div>
      </header>

      {/* Subject tabs */}
      <nav className="exam-tabs">
        {SUBJECTS.map((s, i) => (
          <button
            key={s}
            type="button"
            className={`exam-tab ${i === subject ? 'exam-tab-active' : ''}`}
            onClick={() => goTo(i, 0)}
          >
            {s}
          </button>
        ))}
      </nav>

      <div className="exam-body">
        {sidebarOpen && (
          <button
            type="button"
            className="exam-drawer-backdrop"
            aria-label="Close"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        <main className="exam-main">
          <div className="exam-q-meta">
            <span className="exam-q-time">03:35 | +4 -1</span>
          </div>
          <div className="exam-q-head">
            <span className="exam-q-num">{qIndex + 1}</span>
            <span className="exam-q-type">{SAMPLE_QUESTION.type}</span>
          </div>
          <p className="exam-q-text">{SAMPLE_QUESTION.text}</p>
          <div className="exam-options">
            {SAMPLE_QUESTION.options.map((opt) => (
              <label key={opt.key} className={`exam-option ${selected === opt.key ? 'exam-option-selected' : ''}`}>
                <input
                  type="radio"
                  name="mcq"
                  value={opt.key}
                  checked={selected === opt.key}
                  onChange={() => {
                    setSelected(opt.key)
                    markAttempted()
                  }}
                />
                <span className="exam-option-letter">{opt.key}</span>
                <span className="exam-option-value">{opt.value}</span>
              </label>
            ))}
          </div>
        </main>

        {/* Side panel: opens via hamburger (top right). Question numbers, attempt status, Submit. Only this scrolls. */}
        <aside className={`exam-sidebar exam-drawer ${sidebarOpen ? 'exam-drawer-open' : ''}`}>
          <div className="exam-drawer-header">
            <span>Questions</span>
            <button type="button" className="exam-drawer-close" onClick={() => setSidebarOpen(false)} aria-label="Close">
              ×
            </button>
          </div>
          <div className="exam-drawer-scroll">
            <div className="exam-legend">
              <span className="exam-legend-item attempted">Attempted</span>
              <span className="exam-legend-item attempted-marked">Attempted & Marked</span>
              <span className="exam-legend-item marked">Marked</span>
              <span className="exam-legend-item seen">Seen</span>
              <span className="exam-legend-item not-seen">Not Seen</span>
            </div>
            {SUBJECTS.map((sub, si) => (
              <div key={sub} className="exam-subject-block">
                <div className="exam-subject-stats">
                  <span>0 Attempted</span>
                  <span>0 Attempted & Marked</span>
                  <span>0 Marked</span>
                  <span>{si === 0 && qIndex === 0 ? 1 : 0} Seen</span>
                  <span>{QUESTIONS_PER_SUBJECT - (si === 0 && qIndex === 0 ? 1 : 0)} Not Seen</span>
                </div>
                <div className="exam-q-grid">
                  {Array.from({ length: QUESTIONS_PER_SUBJECT }, (_, i) => {
                    const key = `${si}-${i}`
                    const st = status[key] || (si === subject && i === qIndex ? 'seen' : 'not-seen')
                    const active = si === subject && i === qIndex
                    return (
                      <button
                        key={key}
                        type="button"
                        className={`exam-q-dot ${st} ${active ? 'exam-q-dot-active' : ''}`}
                        onClick={() => goTo(si, i)}
                      >
                        {i + 1}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
          <div className="exam-drawer-footer">
            <button type="button" className="exam-btn exam-btn-submit" onClick={() => navigate('/contests')}>
              Submit Test
            </button>
          </div>
        </aside>
      </div>

      {/* Bottom: Clear, Previous, Next only */}
      <footer className="exam-footer">
        <button type="button" className="exam-btn exam-btn-clear" onClick={() => setSelected(null)}>
          Clear Response
        </button>
        <button
          type="button"
          className="exam-btn exam-btn-prev"
          onClick={() => goTo(subject, Math.max(0, qIndex - 1))}
        >
          Previous
        </button>
        <button
          type="button"
          className="exam-btn exam-btn-next"
          onClick={() => goTo(subject, Math.min(QUESTIONS_PER_SUBJECT - 1, qIndex + 1))}
        >
          Next
        </button>
      </footer>
    </div>
  )
}

export default Exam
