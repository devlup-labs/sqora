import React, { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './Exam.css'

const EXAM_CONFIGS = {
  JEE: { subjects: ['Physics', 'Chemistry', 'Mathematics'], qPerSubject: 25, totalQ: 75 },
  NEET: { subjects: ['Physics', 'Chemistry', 'Botany', 'Zoology'], qPerSubject: 45, totalQ: 180 }
}

function Exam() {
  const { code } = useParams()
  const navigate = useNavigate()
  const isNEET = code?.toUpperCase().startsWith('NEET');
  const fallbackConfig = isNEET ? EXAM_CONFIGS.NEET : EXAM_CONFIGS.JEE;

  // --- STATE ---
  const [darkMode, setDarkMode] = useState(true)
  const [currentGlobalQ, setCurrentGlobalQ] = useState(1)
  const [userAnswers, setUserAnswers] = useState({})
  const [status, setStatus] = useState({})
  const [timeLeft, setTimeLeft] = useState(10800) // 3 Hours
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [paused, setPaused] = useState(false)
  const [config, setConfig] = useState(fallbackConfig)
  const [questions, setQuestions] = useState([])

  // Fetch exam data from backend
  useEffect(() => {
    if (!code) return
    fetch(`/api/exams/${code}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.config) setConfig(data.config)
        if (data.questions) setQuestions(data.questions)
      })
      .catch((err) => console.error('Failed to load exam:', err))
  }, [code])

  // Current question from fetched data
  const currentQuestion = questions.find((q) => q.number === currentGlobalQ) || null

  // Determine active subject based on the current global question number
  const activeSubjectIdx = useMemo(() => {
    return Math.floor((currentGlobalQ - 1) / config.qPerSubject);
  }, [currentGlobalQ, config]);

  // Timer Logic
  useEffect(() => {
    if (paused || timeLeft <= 0) return
    const t = setInterval(() => setTimeLeft((prev) => Math.max(0, prev - 1)), 1000)
    return () => clearInterval(t)
  }, [paused, timeLeft])

  const formatTime = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const n = s % 60;
    return [h, m, n].map((x) => String(x).padStart(2, '0')).join(':');
  }

  const handleOptionSelect = (opt) => {
    setUserAnswers(prev => ({ ...prev, [currentGlobalQ]: opt }));
    setStatus(prev => ({ ...prev, [currentGlobalQ]: 'attempted' }));
  }

  return (
    <div className={`exam-page ${darkMode ? 'exam-dark' : 'exam-light'}`}>
      {/* HEADER: Contains Timer, Toggle, and Hamburger */}
      <header className="exam-header">
        <div className="exam-header-left">
          <button className="pause-btn" onClick={() => setPaused(!paused)}>
            {paused ? '▶️' : '⏸️'}
          </button>
          <div className="exam-timer">{formatTime(timeLeft)}</div>
        </div>
        <div className="exam-title-text">{code}</div>

        <div className="exam-header-actions">
          {/* SINGLE TOGGLE BUTTON: Sun when dark, Moon when light */}
          <button className="header-icon-btn theme-toggle" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? '☀️' : '🌙'}
          </button>

          <button className="hamburger-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <div className="hamburger-line"></div>
            <div className="hamburger-line"></div>
            <div className="hamburger-line"></div>
          </button>
        </div>
      </header>

      {/* SUBJECT TABS: Highlights automatically based on current question */}
      <nav className="exam-tabs">
        {config.subjects.map((s, i) => (
          <button
            key={s}
            className={`exam-tab ${i === activeSubjectIdx ? 'exam-tab-active' : ''}`}
            onClick={() => {
              setCurrentGlobalQ((i * config.qPerSubject) + 1);
              setStatus(prev => ({ ...prev, [(i * config.qPerSubject) + 1]: prev[(i * config.qPerSubject) + 1] || 'seen' }));
            }}
          >
            {s}
          </button>
        ))}
      </nav>

      <div className="exam-container-main">
        {/* QUESTION AREA: Independent Scrollbar */}
        <main className="exam-content-scroll">
          <div className="exam-q-header">
            <div className="q-badge">Question {currentGlobalQ}</div>
            <div className="q-scoring">{currentQuestion?.scoring || '+4  -1'}</div>
          </div>

          <div className="q-body">
            <p className="q-text">{currentQuestion?.text || 'Loading question…'}</p>
            <div className="options-vertical">
              {['A', 'B', 'C', 'D'].map((opt) => (
                <div
                  key={opt}
                  className={`option-box ${userAnswers[currentGlobalQ] === opt ? 'is-selected' : ''}`}
                  onClick={() => handleOptionSelect(opt)}
                >
                  <span className="opt-letter">{opt}</span>
                  <span className="opt-text">{currentQuestion?.options?.[opt] || `Option ${opt}`}</span>
                </div>
              ))}
            </div>
          </div>
        </main>

        {/* SIDEBAR: Independent Scrollbar */}
        {sidebarOpen && (
          <aside className="exam-sidebar-fixed">
            <div className="sidebar-scrollable-content">
              {config.subjects.map((subName, si) => (
                <div key={subName} className="sidebar-group">
                  <h4 className="sidebar-group-title">{subName}</h4>
                  <div className="q-palette-grid">
                    {Array.from({ length: config.qPerSubject }).map((_, i) => {
                      const qNum = (si * config.qPerSubject) + i + 1;
                      const qStatus = status[qNum] || 'not-seen';
                      return (
                        <button
                          key={qNum}
                          className={`palette-dot ${qStatus} ${currentGlobalQ === qNum ? 'active' : ''}`}
                          onClick={() => {
                            setCurrentGlobalQ(qNum);
                            setStatus(prev => ({ ...prev, [qNum]: prev[qNum] === 'attempted' ? 'attempted' : 'seen' }));
                          }}
                        >
                          {qNum}
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
            <div className="sidebar-fixed-footer">
              <button className="full-submit-btn" onClick={() => navigate('/contests')}>Submit Test</button>
            </div>
          </aside>
        )}
      </div>

      {/* FOOTER: Fixed at bottom */}
      <footer className="exam-footer-fixed">
        <button className="btn-secondary btn-small" onClick={() => {
          const n = { ...userAnswers };
          delete n[currentGlobalQ];
          setUserAnswers(n);
          // When clearing, we set it back to "seen" (Red)
          setStatus(prev => ({ ...prev, [currentGlobalQ]: 'seen' }));
        }}>
          Clear Response
        </button>

        <div className="footer-nav">
          <button className="btn-nav btn-small" onClick={() => {
            if (currentGlobalQ > 1) {
              // Logic: Mark current as 'seen' if not already 'attempted' before going back
              setStatus(prev => ({
                ...prev,
                [currentGlobalQ]: prev[currentGlobalQ] === 'attempted' ? 'attempted' : 'seen'
              }));
              setCurrentGlobalQ(q => q - 1);
            }
          }}>
            Previous
          </button>

          <button className="btn-nav btn-primary btn-small" onClick={() => {
            if (currentGlobalQ < config.totalQ) {
              // IMPORTANT: Mark current as 'seen' (Red) unless it's 'attempted' (Green)
              setStatus(prev => ({
                ...prev,
                [currentGlobalQ]: prev[currentGlobalQ] === 'attempted' ? 'attempted' : 'seen'
              }));
              setCurrentGlobalQ(q => q + 1);
            }
          }}>
            Next
          </button>
        </div>
      </footer>
    </div>
  )
}

export default Exam