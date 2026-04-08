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
import { useAuth } from '../contexts/AuthContext'
import { apiFetch, buildAuthUrl } from '../lib/apiFetch'
import './aimentor.css'

// Strip markdown, LaTeX, and symbols for clean text-to-speech
function stripForTTS(text) {
  return text
    .replace(/\$\$[\s\S]*?\$\$/g, ', math expression,')
    .replace(/\$[^$]+?\$/g, ', math expression,')
    .replace(/\\[a-zA-Z]+\{[^}]*\}/g, '')
    .replace(/```[\s\S]*?```/g, ', code block,')
    .replace(/`[^`]+`/g, '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_]{1,3}/g, '')
    .replace(/^[-*_]{3,}$/gm, '')
    .replace(/^\s*[-*+•]\s+/gm, ', ')   // handle - * + • bullets → pause
    .replace(/•/g, ', ')                 // stray unicode bullets
    .replace(/^\s*\d+\.\s+/gm, ', ')    // numbered lists
    .replace(/:\s*\n/g, '. ')            // colon+newline → period
    .replace(/[~|>]/g, '')
    .replace(/\n{2,}/g, '. ')
    .replace(/\n/g, ' ')
    .replace(/,\s*,/g, ',')
    .replace(/\.\s*\./g, '.')
    .replace(/\s{2,}/g, ' ')
    .trim()
}


function AIMentor() {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [lastQuestion, setLastQuestion] = useState('')
  const [lastAnswer, setLastAnswer] = useState('')
  const [isChatOpen, setIsChatOpen] = useState(false)
  const chatInputRef = useRef(null)
  const { mentorGreeting, voiceEnabled } = useAppConfig()
  const { currentUser } = useAuth()
  
  const initialGreeting = mentorGreeting || 'Hi! I am your AI mentor. Tap the mic or open chat to ask anything about your prep.'
  
  const [chatMessages, setChatMessages] = useState(() => [
    { role: 'assistant', text: initialGreeting },
  ])
  const recognitionRef = useRef(null)
  const chatMessagesRef = useRef(null)

  // --- Video panel state ---
  const [activeVideoId, setActiveVideoId] = useState(null)
  const [videoReady, setVideoReady] = useState(false)
  const [videoPolling, setVideoPolling] = useState(false)
  const videoRef = useRef(null)
  const pollingRef = useRef(null)
  const activeAudioRef = useRef(null)
  const sttRef = useRef(null)                           // SpeechRecognition instance
  const transcriptRef = useRef('')
  const [liveTranscript, setLiveTranscript] = useState('')
  const [videoToken, setVideoToken] = useState('')
  const [videoSrc, setVideoSrc] = useState('')
  const [audioAnalyser, setAudioAnalyser] = useState(null)
  // HeadTTS viseme schedule
  const [visemeSchedule, setVisemeSchedule] = useState(null)
  // HeadTTS WebSocket refs
  const htWsRef = useRef(null)          // WebSocket instance
  const htReadyRef = useRef(false)      // WS is connected + setup-confirmed
  const htResolveRef = useRef(null)     // resolve pending speak() promise

  // Keep a fresh token for video/SSE URLs (refreshed whenever user changes)
  useEffect(() => {
    if (!currentUser) return
    currentUser.getIdToken(false).then(setVideoToken).catch(() => {})
  }, [currentUser])

  // Rebuild the authenticated video src whenever the active video or token changes
  useEffect(() => {
    if (!activeVideoId || !currentUser) { setVideoSrc(''); return }
    buildAuthUrl(`/api/users/${currentUser.uid}/videos/${activeVideoId}`).then(setVideoSrc)
  }, [activeVideoId, currentUser, videoToken])

  // Watch for video readiness via SSE (fires within ~1 s of render finishing)
  useEffect(() => {
    if (!activeVideoId) {
      setVideoReady(false)
      setVideoPolling(false)
      return
    }

    setVideoReady(false)
    setVideoPolling(true)

    if (!currentUser) return
    const userId = currentUser.uid

    // Optimistic check — if the video is already rendered (cache hit) show it instantly
    apiFetch(`/api/users/${userId}/videos/${activeVideoId}/status`)
      .then((r) => r.json())
      .then((d) => {
        if (d.ready) {
          setVideoReady(true)
          setVideoPolling(false)
        }
      })
      .catch(() => { })

    // SSE stream: server fires "ready" the instant the .mp4 file appears
    // EventSource can't send headers, so pass token as query param via buildAuthUrl
    let es
    const startSSE = async () => {
      try {
        const sseUrl = await buildAuthUrl(`/api/users/${userId}/videos/${activeVideoId}/ready`)
        es = new EventSource(sseUrl)
        pollingRef.current = es
        es.onmessage = (e) => {
          if (e.data === 'ready') {
            setVideoReady(true)
            setVideoPolling(false)
            es.close()
          }
        }
        es.onerror = () => es.close()
      } catch (err) {
        console.warn('SSE setup failed:', err)
      }
    }
    startSSE()
  }, [activeVideoId, currentUser])

  // Auto-play video when ready
  useEffect(() => {
    if (videoReady && videoRef.current) {
      videoRef.current.load()
      videoRef.current.play().catch(() => { })
    }
  }, [videoReady])

  // ── HeadTTS WebSocket ──────────────────────────────────────────────────────
  const TTS_WS_URL = (import.meta.env.VITE_TTS_URL || '')
    .replace(/^https/, 'wss').replace(/^http/, 'ws')

  useEffect(() => {
    if (!TTS_WS_URL) return
    let ws, dead = false
    const connect = () => {
      if (dead) return
      ws = new WebSocket(TTS_WS_URL)
      htWsRef.current = ws
      htReadyRef.current = false
      ws.onopen = () => ws.send(JSON.stringify({
        type: 'setup', voice: 'af_heart', language: 'en-us', speed: 1, audioEncoding: 'wav',
      }))
      ws.onmessage = async (evt) => {
        let msg; try { msg = JSON.parse(evt.data) } catch { return }
        if (msg.type === 'setup') { htReadyRef.current = true; console.log('[HeadTTS WS] Ready'); return }
        if (msg.type === 'audio' && htResolveRef.current) {
          try {
            const d = msg.data
            const bin = atob(d.audio); const bytes = new Uint8Array(bin.length)
            for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
            const blobUrl = URL.createObjectURL(new Blob([bytes], { type: 'audio/wav' }))
            const visemes = (d.visemes || []).map((v, i) => ({
              viseme: v, time: (d.vtimes?.[i] || 0) / 1000, duration: (d.vdurations?.[i] || 100) / 1000,
            }))
            htResolveRef.current({ blobUrl, visemes })
          } catch { htResolveRef.current(null) }
          htResolveRef.current = null
        }
        if (msg.type === 'error') {
          console.warn('[HeadTTS WS]', msg.data)
          if (htResolveRef.current) { htResolveRef.current(null); htResolveRef.current = null }
        }
      }
      ws.onclose = () => {
        htReadyRef.current = false
        if (htResolveRef.current) { htResolveRef.current(null); htResolveRef.current = null }
        if (!dead) setTimeout(connect, 3000)
      }
      ws.onerror = () => ws.close()
    }
    connect()
    return () => { dead = true; ws?.close() }
  }, [TTS_WS_URL]) // eslint-disable-line

  const htSynthesize = (text) => {
    if (!htWsRef.current || !htReadyRef.current) return Promise.resolve(null)
    return new Promise((resolve) => {
      htResolveRef.current = resolve
      htWsRef.current.send(JSON.stringify({ type: 'synthesize', input: text }))
      setTimeout(() => {
        if (htResolveRef.current === resolve) { resolve(null); htResolveRef.current = null }
      }, 5000)
    })
  }

  // ── speakTextPipelined ────────────────────────────────────────────────────
  // Web Speech starts INSTANTLY as primary. HeadTTS parallel — takes over
  // with Kokoro voice + real phoneme visemes if it responds in time.
  const speakTextPipelined = async (text) => {
    if (!voiceEnabled || !text.trim()) return
    setIsSpeaking(true)
    const cleanText = stripForTTS(text)
    if (!cleanText.trim()) { setIsSpeaking(false); return }
    console.log('[TTS]', cleanText.slice(0, 80))

    const htPromise = htSynthesize(cleanText)
    const synth = window.speechSynthesis
    let wsFinished = false

    const wsDone = new Promise((resolve) => {
      if (!synth) { resolve(); return }
      synth.cancel()
      const utt = new SpeechSynthesisUtterance(cleanText)
      utt.rate = 1; utt.pitch = 1.1
      const vs = synth.getVoices()
      const fv = vs.find(v => /zira|samantha|victoria|female/i.test(v.name) && v.lang?.startsWith('en'))
        || vs.find(v => v.lang?.startsWith('en'))
      if (fv) utt.voice = fv
      utt.onboundary = (e) => {
        if (e.name !== 'word') return
        const w = cleanText.slice(e.charIndex, e.charIndex + (e.charLength || 3))
        setVisemeSchedule([{ viseme: /[aeiou]/i.test(w) ? 'aa' : 'nn', time: 0, duration: 0.12 }])
        setTimeout(() => setVisemeSchedule(null), 130)
      }
      utt.onend = () => { wsFinished = true; setVisemeSchedule(null); resolve() }
      utt.onerror = () => { wsFinished = true; setVisemeSchedule(null); resolve() }
      synth.speak(utt)
    })

    const winner = await Promise.race([htPromise, wsDone.then(() => 'done')])

    if (winner && winner !== 'done' && winner.blobUrl) {
      synth?.cancel()
      console.log('[TTS] HeadTTS Kokoro, visemes:', winner.visemes.length)
      setVisemeSchedule(winner.visemes)
      await new Promise((resolve) => {
        const audio = new Audio(winner.blobUrl)
        activeAudioRef.current = audio
        audio.onended = () => { URL.revokeObjectURL(winner.blobUrl); setVisemeSchedule(null); resolve() }
        audio.onerror = () => { URL.revokeObjectURL(winner.blobUrl); setVisemeSchedule(null); resolve() }
        audio.play().catch(() => { setVisemeSchedule(null); resolve() })
      })
    } else {
      if (!wsFinished) await wsDone
    }

    setIsSpeaking(false)
    setVisemeSchedule(null)
    activeAudioRef.current = null
  }


  // ----- AI Response: show dots while thinking, reveal all at once -----
  const handleAIResponse = async (questionText) => {
    if (!currentUser) return
    const userId = currentUser.uid
    const currentHistory = [...chatMessages]
    
    setChatMessages((prev) => [
      ...prev,
      { role: 'user', text: questionText },
      { role: 'assistant', text: '__thinking__' },
    ])

    try {
      const res = await apiFetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ 
          message: questionText,
          history: currentHistory
        }),
      })
      const data = await res.json()
      const reply = data.reply || 'Sorry, something went wrong.'
      const videoId = data.video_id

      const finalHistory = [
        ...currentHistory,
        { role: 'user', text: questionText },
        { role: 'assistant', text: reply, video_id: videoId }
      ]
      
      setChatMessages(finalHistory)
      if (videoId) setActiveVideoId(videoId)

      // Save to Server Local API
      if (currentUser) {
        try {
          apiFetch(`/api/users/${userId}/chat`, {
            method: 'POST',
            body: JSON.stringify({ history: finalHistory }),
          })
        } catch (e) {
          console.error("Failed to save history to local server:", e)
        }
      }

      // Start pipelined TTS (all sentences in parallel, play in order)
      speakTextPipelined(reply)
    } catch (err) {
      console.error('Chat error:', err)
      const fallback = 'Could not reach the server.'
      setChatMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', text: fallback }
        return updated
      })
      speakTextPipelined(fallback)
    }
  }

  // ----- STT: browser Web Speech API (Chrome → Google cloud, best quality) -----
  const stopRecordingAndSend = () => {
    setIsListening(false)
    transcriptRef.current = liveTranscript.trim()
    setLiveTranscript('')
    if (sttRef.current) {
      sttRef.current.stop()
      sttRef.current = null
    }
  }

  const startRecording = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }

    const recognition = new SR()
    sttRef.current = recognition
    recognition.lang = 'en-IN'
    recognition.continuous = false     // auto-stops after natural pause
    recognition.interimResults = true  // show live partial results
    recognition.maxAlternatives = 1

    let finalText = ''

    recognition.onresult = (event) => {
      let interim = ''
      finalText = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalText += event.results[i][0].transcript
        } else {
          interim += event.results[i][0].transcript
        }
      }
      const latestTranscript = (finalText || interim).trim()
      transcriptRef.current = latestTranscript
      setLiveTranscript(latestTranscript)
    }

    recognition.onend = () => {
      setIsListening(false)
      setLiveTranscript('')
      sttRef.current = null
      const text = (finalText || transcriptRef.current || '').trim()
      transcriptRef.current = ''
      if (text) {
        setLastQuestion(text)
        handleAIResponse(text)
      }
    }

    recognition.onerror = (event) => {
      console.error('[STT] Error:', event.error)
      setIsListening(false)
      setLiveTranscript('')
      transcriptRef.current = ''
      sttRef.current = null
    }

    recognition.start()
    setIsListening(true)
    transcriptRef.current = ''
    setLiveTranscript('')
  }


  useEffect(() => {
    const fetchHistory = async () => {
      if (!currentUser) return
      try {
        const res = await apiFetch(`/api/users/${currentUser.uid}/chat`)
        const data = await res.json()
        
        if (data.history && data.history.length > 0) {
          const history = data.history
          setChatMessages(history)
          const lastWithVideo = [...history].reverse().find((m) => m.video_id)
          if (lastWithVideo) {
            setActiveVideoId(lastWithVideo.video_id)
          }
        }
      } catch (err) {
        console.error('Failed to fetch chat history from server:', err)
      }
    }
    fetchHistory()
  }, [currentUser])

  const handleMicClick = () => {
    primeAudioContext()  // prime on gesture

    if (isSpeaking) {

      // Stop current audio immediately
      if (activeAudioRef.current) {
        activeAudioRef.current.pause()
        activeAudioRef.current = null
      }
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
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
    const val = chatInputRef.current?.value || ''
    const trimmed = val.trim()
    if (!trimmed) return
    if (chatInputRef.current) chatInputRef.current.value = ''
    setLastQuestion(trimmed)
    await handleAIResponse(trimmed)
  }

  // When chat messages update, auto-select the latest video
  useEffect(() => {
    const lastWithVideo = [...chatMessages].reverse().find((m) => m.video_id)
    if (lastWithVideo && lastWithVideo.video_id !== activeVideoId) {
      setActiveVideoId(lastWithVideo.video_id)
    }
  }, [chatMessages])

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight
    }
  }, [chatMessages, isChatOpen])

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
                src={videoSrc}
              />
            )}
          </div>

          {/* List of past videos from chat */}
          <div className="mentor-video-list">
            {chatMessages
              .filter((m) => m.video_id)
              .slice(-10)
                .reverse()
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
        <div className={`mentor-center-area ${isChatOpen ? 'is-chat-open' : ''}`}>
          <div className="mentor-canvas-wrapper">
            <Canvas camera={{ position: [0, 1.2, 4.5], fov: 35 }}>
              <ambientLight intensity={0.7} />
              <spotLight position={[10, 10, 10]} angle={1.8} penumbra={1} />
              <React.Suspense fallback={null}>
                <MentorModel isSpeaking={isSpeaking} visemeSchedule={visemeSchedule} position={[0, -4, 0]} scale={3} />
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

            {/* Live partial transcript while recording */}
            {isListening && liveTranscript && (
              <div className="mentor-live-transcript">
                {liveTranscript}
              </div>
            )}
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
            <div className="mentor-chat-messages" ref={chatMessagesRef}>
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`mentor-chat-bubble ${msg.role}`}
                >
                  {msg.role === 'assistant' ? (
                    <>
                      {msg.text === '__thinking__' ? (
                        <span className="thinking-dots">
                          <span /><span /><span />
                        </span>
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                          {msg.text}
                        </ReactMarkdown>
                      )}
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
                ref={chatInputRef}
                type="text"
                placeholder="Type your question..."
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