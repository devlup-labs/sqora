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
    .replace(/\$\$[\s\S]*?\$\$/g, ' math expression ')
    .replace(/\$[^$]+?\$/g, ' math expression ')
    .replace(/\\[a-zA-Z]+\{[^}]*\}/g, '')
    .replace(/```[\s\S]*?```/g, ' code block ')
    .replace(/`[^`]+`/g, '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_]{1,3}/g, '')
    .replace(/^[-*_]{3,}$/gm, '')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .replace(/[~|>]/g, '')
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

  // --- Video panel state ---
  const [activeVideoId, setActiveVideoId] = useState(null)
  const [videoReady, setVideoReady] = useState(false)
  const [videoPolling, setVideoPolling] = useState(false)
  const videoRef = useRef(null)
  const pollingRef = useRef(null)
  const activeAudioRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  // Poll for video readiness when activeVideoId changes
  useEffect(() => {
    if (!activeVideoId) {
      setVideoReady(false)
      setVideoPolling(false)
      return
    }

    setVideoReady(false)
    setVideoPolling(true)

    const poll = async () => {
      try {
        const res = await fetch(`/api/videos/${activeVideoId}/status`)
        const data = await res.json()
        if (data.ready) {
          setVideoReady(true)
          setVideoPolling(false)
          clearInterval(pollingRef.current)
        }
      } catch (err) {
        console.error('Video status poll error:', err)
      }
    }

    poll() // check immediately
    pollingRef.current = setInterval(poll, 3000)

    return () => clearInterval(pollingRef.current)
  }, [activeVideoId])

  // Auto-play video when ready
  useEffect(() => {
    if (videoReady && videoRef.current) {
      videoRef.current.load()
      videoRef.current.play().catch(() => { })
    }
  }, [videoReady])

  const triggerMentorResponse = async (text) => {
    setIsSpeaking(true)

    if (voiceEnabled) {
      try {
        const formData = new FormData()
        formData.append('text', stripForTTS(text))

        const res = await fetch('http://localhost:8000/tts', {
          method: 'POST',
          body: formData,
        })

        if (res.ok) {
          const blob = await res.blob()
          const url = URL.createObjectURL(blob)
          const audio = new Audio(url)
          activeAudioRef.current = audio

          audio.onended = () => {
            setIsSpeaking(false)
            URL.revokeObjectURL(url)
            activeAudioRef.current = null
          }

          audio.play().catch(console.error)
        } else {
          console.error('Pocket TTS generated an error:', res.statusText)
          setTimeout(() => setIsSpeaking(false), 3000)
        }
      } catch (err) {
        console.error('Failed to connect to Pocket TTS local server.', err)
        setTimeout(() => setIsSpeaking(false), 3000)
      }
    } else {
      setTimeout(() => setIsSpeaking(false), 3000)
    }
  }

  const handleAIResponse = async (questionText) => {
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: questionText }),
      })
      const data = await res.json()
      const aiResponse = data.reply || 'Sorry, something went wrong.'
      const videoId = data.video_id

      // Add user message with video_id (for parallel manim generation)
      setChatMessages((prev) => [...prev, { role: 'user', text: questionText, video_id: videoId }])

      // Add AI response
      setChatMessages((prev) => [...prev, { role: 'assistant', text: aiResponse }])
      setLastAnswer(aiResponse)
      triggerMentorResponse(aiResponse)

      // Set active video to the newly created one
      if (videoId) {
        setActiveVideoId(videoId)
      }
    } catch (err) {
      console.error('Chat error:', err)
      const fallback = 'Could not reach the server.'
      setChatMessages((prev) => [
        ...prev,
        { role: 'user', text: questionText },
        { role: 'assistant', text: fallback }
      ])
      setLastAnswer(fallback)
      triggerMentorResponse(fallback)
    }
  }

  const stopRecordingAndSend = () => {
    setIsListening(false)
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        const formData = new FormData()
        formData.append('audio', audioBlob, 'record.webm')

        try {
          const res = await fetch('http://localhost:8090/stt', {
            method: 'POST',
            body: formData,
          })
          if (res.ok) {
            const data = await res.json()
            if (data.text) {
              setLastQuestion(data.text)
              handleAIResponse(data.text)
            } else {
              console.warn('STT returned empty text.')
            }
          } else {
            console.error('STT API failed', res.statusText)
          }
        } catch (e) {
          console.error('STT network error', e)
        }

        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsListening(true)
      setLastAnswer('')
    } catch (err) {
      console.error('Error accessing microphone', err)
      alert('Could not access microphone.')
    }
  }

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('/api/chat')
        const data = await res.json()
        if (data.history && data.history.length > 0) {
          setChatMessages(data.history)
          // Set the latest video if available
          const lastWithVideo = [...data.history].reverse().find((m) => m.video_id)
          if (lastWithVideo) {
            setActiveVideoId(lastWithVideo.video_id)
          }
        }
      } catch (err) {
        console.error('Failed to fetch chat history:', err)
      }
    }
    fetchHistory()
  }, [])

  const handleMicClick = () => {
    if (isSpeaking) {
      if (activeAudioRef.current) {
        activeAudioRef.current.pause()
        activeAudioRef.current.currentTime = 0
        activeAudioRef.current = null
      }
      setIsSpeaking(false)
      return
    }

    if (isListening) {
      stopRecordingAndSend()
    } else {
      startRecording()
    }
  }

  const handleChatSend = async () => {
    const trimmed = chatInput.trim()
    if (!trimmed) return

    setChatInput('')

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed }),
      })
      const data = await res.json()
      const aiResponse = data.reply || 'Sorry, something went wrong.'
      const videoId = data.video_id

      // Add user message with video_id (for parallel manim generation)
      setChatMessages((prev) => [...prev, { role: 'user', text: trimmed, video_id: videoId }])

      // Add AI response
      setChatMessages((prev) => [...prev, { role: 'assistant', text: aiResponse }])
      setLastQuestion(trimmed)
      setLastAnswer(aiResponse)
      triggerMentorResponse(aiResponse)

      // Set active video to the newly created one
      if (videoId) {
        setActiveVideoId(videoId)
      }
    } catch (err) {
      console.error('Chat error:', err)
      setChatMessages((prev) => [
        ...prev,
        { role: 'user', text: trimmed },
        { role: 'assistant', text: 'Could not reach the server.' }
      ])
    }
  }

  // When chat messages update, auto-select the latest video
  useEffect(() => {
    const lastWithVideo = [...chatMessages].reverse().find((m) => m.video_id)
    if (lastWithVideo && lastWithVideo.video_id !== activeVideoId) {
      setActiveVideoId(lastWithVideo.video_id)
    }
  }, [chatMessages])

  return (
    <div className="app">
      <Header />
      <main className="mentor-main">
        {/* ========== LEFT: VIDEO PANEL ========== */}
        <div className="mentor-video-panel">
          <div className="mentor-video-header">
            <span className="mentor-video-header-dot" />
            <span>Lesson Animation</span>
          </div>
          <div className="mentor-video-body">
            {!activeVideoId && (
              <div className="mentor-video-empty">
                <div className="mentor-video-empty-icon">▶</div>
                <p>Ask a question to generate an animated lesson</p>
              </div>
            )}
            {activeVideoId && !videoReady && videoPolling && (
              <div className="mentor-video-empty">
                <div className="mentor-video-spinner" />
                <p>Rendering animation…</p>
              </div>
            )}
            {activeVideoId && videoReady && (
              <video
                ref={videoRef}
                className="mentor-video-player"
                controls
                autoPlay
                src={`/api/videos/${activeVideoId}`}
              />
            )}
          </div>

          {/* List of past videos from chat */}
          <div className="mentor-video-list">
            {chatMessages
              .filter((m) => m.video_id)
              .map((m, i) => (
                <button
                  key={m.video_id}
                  className={`mentor-video-list-item ${m.video_id === activeVideoId ? 'active' : ''}`}
                  onClick={() => setActiveVideoId(m.video_id)}
                >
                  <span className="mentor-video-list-num">{i + 1}</span>
                  <span className="mentor-video-list-label">
                    {m.text?.substring(0, 60)}…
                  </span>
                </button>
              ))}
          </div>
        </div>

        {/* ========== CENTER: 3D MODEL & HUD ========== */}
        <div className="mentor-center-area">
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
        </div>

        {/* Chat toggle */}
        <button
          type="button"
          className="mentor-chat-toggle"
          onClick={() => setIsChatOpen((open) => !open)}
        >
          {isChatOpen ? 'Close Chat' : 'Open Chat'}
        </button>

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
                    <>
                      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                        {msg.text}
                      </ReactMarkdown>
                    </>
                  ) : (
                    <>
                      {msg.text}
                      {msg.video_id && (
                        <button
                          className="mentor-video-inline-btn"
                          onClick={() => setActiveVideoId(msg.video_id)}
                        >
                          ▶ Watch Animation
                        </button>
                      )}
                    </>
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