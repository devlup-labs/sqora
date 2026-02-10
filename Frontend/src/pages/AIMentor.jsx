import React, { useState, useRef, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { Environment, ContactShadows } from '@react-three/drei'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import Header from '../components/Header'
import { MentorModel } from './MentorModel'
import { useAppConfig } from '../store/useAppConfig'
import './aimentor.css'

// Strip markdown, LaTeX, and symbols for clean text-to-speech
function stripForTTS(text) {
  return text
    // Remove LaTeX display blocks: $$...$$
    .replace(/\$\$[\s\S]*?\$\$/g, ' math expression ')
    // Remove inline LaTeX: $...$
    .replace(/\$[^$]+?\$/g, ' math expression ')
    // Remove LaTeX commands like \frac{}{}, \sqrt{}, etc.
    .replace(/\\[a-zA-Z]+\{[^}]*\}/g, '')
    // Remove code blocks: ```...```
    .replace(/```[\s\S]*?```/g, ' code block ')
    // Remove inline code: `...`
    .replace(/`[^`]+`/g, '')
    // Remove markdown images: ![alt](url)
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    // Remove markdown links but keep text: [text](url)
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    // Remove headers: # ## ### etc.
    .replace(/^#{1,6}\s+/gm, '')
    // Remove bold/italic markers: ** __ * _
    .replace(/[*_]{1,3}/g, '')
    // Remove horizontal rules: --- *** ___
    .replace(/^[-*_]{3,}$/gm, '')
    // Remove bullet/list markers
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    // Remove remaining special symbols
    .replace(/[~|>]/g, '')
    // Collapse multiple spaces/newlines
    .replace(/\n{2,}/g, '. ')
    .replace(/\n/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .trim()
}

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
      role: 'assistant',
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
      const utterance = new SpeechSynthesisUtterance(stripForTTS(text))
      utterance.onend = () => setIsSpeaking(false) // Stop animation when done talking
      window.speechSynthesis.speak(utterance)
    } else {
      // Fallback: stop animation after a short delay
      setTimeout(() => setIsSpeaking(false), 3000)
    }
  }

  const handleAIResponse = async (questionText) => {
    // Add user question to chat when speaking
    setChatMessages((prev) => [...prev, { role: 'user', text: questionText }])

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: questionText }),
      })
      const data = await res.json()
      const aiResponse = data.reply || 'Sorry, something went wrong.'

      // Add AI response to chat
      setChatMessages((prev) => [...prev, { role: 'assistant', text: aiResponse }])

      setLastAnswer(aiResponse)
      triggerMentorResponse(aiResponse)
    } catch (err) {
      console.error('Chat error:', err)
      const fallback = 'Could not reach the server.'
      setChatMessages((prev) => [...prev, { role: 'assistant', text: fallback }])
      setLastAnswer(fallback)
      triggerMentorResponse(fallback)
    }
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

  useEffect(() => {
    // Fetch existing chat history from backend
    const fetchHistory = async () => {
      try {
        const res = await fetch('/api/chat')
        const data = await res.json()
        if (data.history && data.history.length > 0) {
          setChatMessages(data.history)
        }
      } catch (err) {
        console.error('Failed to fetch chat history:', err)
      }
    }
    fetchHistory()
  }, [])

  const handleMicClick = () => {
    // If speaking, stop talking immediately
    if (isSpeaking) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      return
    }

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

  const handleChatSend = async () => {
    const trimmed = chatInput.trim()
    if (!trimmed) return

    setChatMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setChatInput('')

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed }),
      })
      const data = await res.json()
      const aiResponse = data.reply || 'Sorry, something went wrong.'
      setChatMessages((prev) => [...prev, { role: 'assistant', text: aiResponse }])
      setLastQuestion(trimmed)
      setLastAnswer(aiResponse)
      triggerMentorResponse(aiResponse)
    } catch (err) {
      console.error('Chat error:', err)
      setChatMessages((prev) => [...prev, { role: 'assistant', text: 'Could not reach the server.' }])
    }
  }

  return (
    <div className="app">
      <Header />
      <main className="mentor-main">
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
            className={`mic-button ${isListening ? 'listening' : ''
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
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                      {msg.text}
                    </ReactMarkdown>
                  ) : (
                    msg.text
                  )}
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