import React, { useEffect, useMemo, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './Exam.css'

const EXAM_CONFIGS = {
    JEE: { subjects: ['Physics', 'Chemistry', 'Mathematics'], qPerSubject: 25, totalQ: 75 },
    NEET: { subjects: ['Physics', 'Chemistry', 'Botany', 'Zoology'], qPerSubject: 45, totalQ: 180 },
}

function ExamReview() {
    const { code } = useParams()
    const navigate = useNavigate()
    const [attempt, setAttempt] = useState(null)

    useEffect(() => {
        try {
            const raw = localStorage.getItem('sqora_lastAttempt')
            if (!raw) {
                navigate(`/exam/${code}`)
                return
            }
            const parsed = JSON.parse(raw)
            if (!parsed || parsed.code !== code) {
                navigate(`/exam/${code}`)
                return
            }
            setAttempt(parsed)
        } catch {
            navigate(`/exam/${code}`)
        }
    }, [code, navigate])

    const config = useMemo(() => {
        if (!attempt) return null
        const type = attempt.configType === 'NEET' ? 'NEET' : 'JEE'
        return EXAM_CONFIGS[type]
    }, [attempt])

    if (!attempt || !config) {
        return null
    }

    const { userAnswers, answerKey } = attempt

    return (
        <div className="exam-page exam-dark">
            <header className="exam-header">
                <div className="exam-header-left">
                    <div className="exam-title-text">Review – {code}</div>
                </div>
                <div className="exam-header-actions">
                    <button className="btn-secondary btn-small" onClick={() => navigate('/')}>
                        Home
                    </button>
                </div>
            </header>

            <div className="exam-container-main">
                <main className="exam-content-scroll exam-review-scroll">
                    {config.subjects.map((subName, si) => (
                        <section key={subName} className="review-subject">
                            <h3 className="review-subject-title">{subName}</h3>
                            {Array.from({ length: config.qPerSubject }).map((_, i) => {
                                const qNum = si * config.qPerSubject + i + 1
                                const user = userAnswers[qNum]
                                const correct = answerKey[qNum]
                                const isCorrect = user && user === correct

                                return (
                                    <div
                                        key={qNum}
                                        className={`review-question ${isCorrect ? 'review-correct' : 'review-incorrect'}`}
                                    >
                                        <div className="review-q-header">
                                            <span className="review-q-number">Q{qNum}</span>
                                            <span className="review-q-status">
                                                {user ? (isCorrect ? 'Correct' : 'Incorrect') : 'Unanswered'}
                                            </span>
                                        </div>
                                        <div className="review-q-body">
                                            <div>
                                                <span className="review-label">Your answer:</span>{' '}
                                                <span className="review-value">{user || '—'}</span>
                                            </div>
                                            <div>
                                                <span className="review-label">Correct answer:</span>{' '}
                                                <span className="review-value">{correct}</span>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </section>
                    ))}
                </main>
            </div>
        </div>
    )
}

export default ExamReview