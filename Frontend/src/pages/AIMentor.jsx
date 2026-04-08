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
  // HeadTTS viseme schedule: array of { viseme, time } objects
  const [visemeSchedule, setVisemeSchedule] = useState(null)

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

  // HeadTTS URL (env var VITE_TTS_URL points to the HeadTTS server exposed via Cloudflare)
  const HEADTTS_URL = import.meta.env.VITE_TTS_URL || ''

  // ----- TTS: HeadTTS with Kokoro neural voice + viseme lip sync -----
  const speakTextPipelined = async (text) => {
    if (!voiceEnabled || !text.trim()) return
    setIsSpeaking(true)
    console.log('[TTS] Starting speech for:', text.slice(0, 60))

    const cleanText = stripForTTS(text)

    // Split into sentences
    const rawSentences = text.match(/[^.!?]+[.!?]+/g) || [text]
    const sentences = rawSentences.filter((s) => s.trim().length > 1)
    const finalSentences = sentences.length > 0 ? sentences : [text]

    // Try HeadTTS for first sentence to see if server is responsive
    const tryHeadTTS = async (sentence) => {
      const stripped = stripForTTS(sentence.trim())
      if (!stripped) return null
      try {
        const controller = new AbortController()
        const timer = setTimeout(() => controller.abort(), 5000)
        const res = await fetch(`${HEADTTS_URL}/v1/synthesize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({ input: stripped, voice: 'af_heart', language: 'en-us', speed: 1, audioEncoding: 'wav' }),
        })
        clearTimeout(timer)
        if (!res.ok) return null
        const data = await res.json()
        if (!data.audio) return null
        // Build blob URL from base64 WAV
        const binary = atob(data.audio)
        const bytes = new Uint8Array(binary.length)
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
        const blobUrl = URL.createObjectURL(new Blob([bytes], { type: 'audio/wav' }))
        const visemes = (data.visemes || []).map((v, i) => ({
          viseme: v,
          time: (data.vtimes?.[i] || 0) / 1000,
          duration: (data.vdurations?.[i] || 100) / 1000,
        }))
        return { blobUrl, visemes }
      } catch (e) {
        if (e.name === 'AbortError') console.warn('[TTS] HeadTTS timeout')
        else console.warn('[TTS] HeadTTS error:', e.message)
        return null
      }
    }

    // Play audio blob via <Audio> element (works even without user-gesture AudioContext)
    const playBlobUrl = (blobUrl, visemes) => new Promise((resolve) => {
      const audio = new Audio(blobUrl)
      activeAudioRef.current = audio
      setVisemeSchedule(visemes || null)
      audio.onended = () => { URL.revokeObjectURL(blobUrl); setVisemeSchedule(null); resolve() }
      audio.onerror = () => { URL.revokeObjectURL(blobUrl); setVisemeSchedule(null); resolve() }
      audio.play().catch(() => { setVisemeSchedule(null); resolve() })
    })

    // Try HeadTTS pipeline first
    let playedCount = 0
    let nextFetch = tryHeadTTS(finalSentences[0])

    for (let i = 0; i < finalSentences.length; i++) {
      const result = await nextFetch
      nextFetch = (i + 1 < finalSentences.length) ? tryHeadTTS(finalSentences[i + 1]) : null
      if (!result) continue
      console.log(`[TTS] ▶ HeadTTS sentence ${i + 1}/${finalSentences.length}, visemes: ${result.visemes.length}`)
      await playBlobUrl(result.blobUrl, result.visemes)
      playedCount++
    }

    // Fallback: Web Speech API (always works in browser, no server needed)
    if (playedCount === 0 && window.speechSynthesis) {
      console.log('[TTS] Using Web Speech API fallback')
      setIsSpeaking(true)
      await new Promise((resolve) => {
        window.speechSynthesis.cancel()
        const utterance = new SpeechSynthesisUtterance(cleanText)
        utterance.rate = 1
        utterance.pitch = 1.1
        // Pick a female voice if available
        const voices = window.speechSynthesis.getVoices()
        const femaleVoice = voices.find(v => /female|woman|girl|zira|samantha|victoria/i.test(v.name))
        if (femaleVoice) utterance.voice = femaleVoice
        utterance.onend = resolve
        utterance.onerror = resolve
        window.speechSynthesis.speak(utterance)
      })
      playedCount++
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
    // Resume audio context on user gesture
    if (audioAnalyser && audioAnalyser.context.state === 'suspended') {
      audioAnalyser.context.resume()
    }

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
    // Resume audio context on user gesture
    if (audioAnalyser && audioAnalyser.context.state === 'suspended') {
      audioAnalyser.context.resume()
    }

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