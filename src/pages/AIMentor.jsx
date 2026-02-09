import React, { useState, useRef, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { Environment, ContactShadows } from '@react-three/drei'
import Header from '../components/Header'
import { MentorModel } from './MentorModel'
import { useAppConfig } from '../store/useAppConfig'
import './aimentor.css'

function AIMentor() {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [lastQuestion, setLastQuestion] = useState('')
  const [lastAnswer, setLastAnswer] = useState('')
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const { mentorGreeting, voiceEnabled } = useAppConfig()
  const [chatMessages, setChatMessages] = useState(() => [
    {
      role: 'ai',
      text:
        mentorGreeting ||
        'Hi! I am your AI mentor. Tap the mic or open chat to ask anything about your prep.',
    },
  ])
  const recognitionRef = useRef(null)

  const triggerMentorResponse = (text) => {
    // Start Animation
    setIsSpeaking(true)

    if (voiceEnabled && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onend = () => setIsSpeaking(false) // Stop animation when done talking
      window.speechSynthesis.speak(utterance)
    } else {
      // Fallback: stop animation after a short delay
      setTimeout(() => setIsSpeaking(false), 3000)
    }
  }

  const createDemoResponse = (questionText) => {
    return "This is a demo answer. Later, I'll be powered by your backend to give detailed JEE/NEET guidance."
  }

  const handleAIResponse = (questionText) => {
    // Placeholder logic – replace with real backend call later
    const aiResponse = createDemoResponse(questionText)

    setLastAnswer(aiResponse)
    triggerMentorResponse(aiResponse)
  }

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      console.warn('Speech recognition is not supported in this browser.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-IN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onstart = () => {
      setIsListening(true)
      setLastAnswer('')
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognition.onerror = () => {
      setIsListening(false)
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setLastQuestion(transcript)
      handleAIResponse(transcript)
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      recognitionRef.current = null
    }
  }, [])

  const handleMicClick = () => {
    const recognition = recognitionRef.current

    if (!recognition) {
      alert('Speech recognition is not supported in this browser.')
      return
    }

    if (isListening) {
      recognition.stop()
    } else {
      recognition.start()
    }
  }

  const handleChatSend = () => {
    const trimmed = chatInput.trim()
    if (!trimmed) return

    setChatMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setChatInput('')

    const aiResponse = createDemoResponse(trimmed)
    setChatMessages((prev) => [...prev, { role: 'user', text: trimmed }, { role: 'ai', text: aiResponse }])
    setLastQuestion(trimmed)
    setLastAnswer(aiResponse)
    triggerMentorResponse(aiResponse)
  }

  return (
    <div className="app">
      <Header />
      <main className="mentor-main">
        {/* Reuse the same soft blue glow as on the landing page */}
        <div className="gradient-overlay" />

        {/* Optional chat panel toggle, similar glassmorphism to landing cards */}
        <button
          type="button"
          className="mentor-chat-toggle"
          onClick={() => setIsChatOpen((open) => !open)}
        >
          {isChatOpen ? 'Close Chat' : 'Open Chat'}
        </button>

        {/* Centered 3D Mentor model – full body, front view (no crop) */}
        <div className="mentor-canvas-wrapper">
          <Canvas camera={{ position: [0, 1.2, 4.5], fov: 35 }}>
            <ambientLight intensity={0.7} />
            <spotLight position={[10, 10, 10]} angle={1.8} penumbra={1} />
            <React.Suspense fallback={null}>
              <MentorModel isSpeaking={isSpeaking} position={[0, -4, 0]} scale={3} />
              <ContactShadows opacity={0.4} scale={5} blur={2} far={4.5} />
              <Environment preset="city" />
            </React.Suspense>
          </Canvas>
        </div>

        {/* Mic control and subtle status text – no chat sidebar */}
        <div className="mentor-hud">
          <button
            type="button"
            className={`mic-button ${
              isListening ? 'listening' : ''
            } ${isSpeaking ? 'speaking' : ''}`}
            onClick={handleMicClick}
          >
            <span className="mic-icon" />
          </button>

          <div className="mentor-status">
            {isListening && <span className="status-pill listening">Listening…</span>}
            {!isListening && isSpeaking && (
              <span className="status-pill speaking">Responding…</span>
            )}
            {!isListening && !isSpeaking && (
              <span className="status-pill idle">Tap the mic to ask</span>
            )}

            {lastQuestion && (
              <p className="mentor-caption">
                You said: <span className="mentor-text">{lastQuestion}</span>
              </p>
            )}
            {lastAnswer && (
              <p className="mentor-caption">
                Mentor: <span className="mentor-text">{lastAnswer}</span>
              </p>
            )}
          </div>
        </div>

        {isChatOpen && (
          <div className="mentor-chat-panel">
            <div className="mentor-chat-header">
              <span>Chat with Mentor</span>
              <button
                type="button"
                className="mentor-chat-close"
                onClick={() => setIsChatOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="mentor-chat-messages">
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`mentor-chat-bubble ${msg.role}`}
                >
                  {msg.text}
                </div>
              ))}
            </div>
            <div className="mentor-chat-input">
              <input
                type="text"
                placeholder="Type your question..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
              />
              <button type="button" onClick={handleChatSend}>
                Send
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default AIMentor