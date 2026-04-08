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

function decodeBase64ToBlobUrl(base64Audio, mimeType = 'audio/wav') {
  if (!base64Audio || typeof base64Audio !== 'string') return null
  const bin = atob(base64Audio)
  const bytes = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
  return URL.createObjectURL(new Blob([bytes], { type: mimeType }))
}

function toSeconds(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return 0
  return n > 20 ? n / 1000 : n
}

function normalizeVisemeSchedule(data) {
  const rawVisemes = data?.visemes

  if (Array.isArray(rawVisemes) && rawVisemes.length > 0 && typeof rawVisemes[0] === 'object') {
    return rawVisemes
      .map((item) => ({
        viseme: item?.viseme || item?.name || item?.id || 'sil',
        time: toSeconds(item?.time ?? item?.start ?? 0),
        duration: Math.max(toSeconds(item?.duration ?? item?.len ?? 0.1), 0.04),
      }))
      .sort((a, b) => a.time - b.time)
  }

  if (Array.isArray(rawVisemes) && rawVisemes.length > 0) {
    return rawVisemes.map((v, idx) => ({
      viseme: v,
      time: toSeconds(data?.vtimes?.[idx] ?? 0),
      duration: Math.max(toSeconds(data?.vdurations?.[idx] ?? 0.1), 0.04),
    }))
  }

  return []
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
  const activeFetchAbortRef = useRef(null)

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

  // cancellation flag — set true to abort speaking mid-way
  const stopSpeakRef = useRef(false)

  // ── speakTextPipelined (Sequential HeadTTS Chunking) ──────────────────────
  const speakTextPipelined = async (text) => {
    if (!voiceEnabled || !text.trim()) return
    stopSpeakRef.current = false
    setIsSpeaking(true)

    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
    const HEADTTS_TIMEOUT_MS = Number(import.meta.env.VITE_HEADTTS_TIMEOUT_MS || 45000)
    const HEADTTS_MAX_RETRIES = Number(import.meta.env.VITE_HEADTTS_MAX_RETRIES || 5)
    const HEADTTS_BACKOFF_MS = Number(import.meta.env.VITE_HEADTTS_BACKOFF_MS || 1200)
    
    const rawSentences = text.match(/[^.!?]+[.!?]*\s*/g) || [text]
    const sentences = rawSentences.filter(s => s.trim().length > 1)
    const finalSentences = sentences.length > 0 ? sentences : [text]

    console.log(`[TTS] Sequential HeadTTS for ${finalSentences.length} chunks`)

    const HEADTTS_URL = import.meta.env.VITE_TTS_URL || (import.meta.env.DEV ? 'http://localhost:8882' : '')
    if (!HEADTTS_URL) {
      console.warn('[TTS] VITE_TTS_URL is not configured; skipping speech.')
      setIsSpeaking(false)
      setVisemeSchedule(null)
      return
    }

    const synthesizeChunkWithRetry = async (chunkText, chunkIndex) => {
      let lastError = null

      for (let attempt = 1; attempt <= HEADTTS_MAX_RETRIES; attempt++) {
        if (stopSpeakRef.current) return null

        const controller = new AbortController()
        activeFetchAbortRef.current = controller
        const timeoutMs = HEADTTS_TIMEOUT_MS + (attempt - 1) * 3000
        const timer = setTimeout(() => controller.abort(), timeoutMs)

        try {
          const res = await fetch(`${HEADTTS_URL}/v1/synthesize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal,
            body: JSON.stringify({
              input: chunkText,
              voice: 'af_heart',
              language: 'en-us',
              speed: 1,
              audioEncoding: 'wav'
            })
          })

          if (!res.ok) {
            throw new Error(`HTTP ${res.status}`)
          }

          const data = await res.json()
          const blobUrl = decodeBase64ToBlobUrl(data?.audio, 'audio/wav')
          if (!blobUrl) {
            throw new Error('No audio payload in HeadTTS response')
          }

          const visemes = normalizeVisemeSchedule(data)
          return { blobUrl, visemes }
        } catch (e) {
          lastError = e
          if (stopSpeakRef.current) return null
          if (attempt < HEADTTS_MAX_RETRIES) {
            const backoff = HEADTTS_BACKOFF_MS * attempt
            console.warn(`[TTS] Chunk ${chunkIndex + 1} attempt ${attempt} failed; retrying in ${backoff}ms`, e)
            await wait(backoff)
          }
        } finally {
          clearTimeout(timer)
          if (activeFetchAbortRef.current === controller) {
            activeFetchAbortRef.current = null
          }
        }
      }

      console.error(`[TTS] Chunk ${chunkIndex + 1} failed after ${HEADTTS_MAX_RETRIES} attempts`, lastError)
      return null
    }

    try {
      for (let i = 0; i < finalSentences.length; i++) {
        if (stopSpeakRef.current) break
        const sentence = finalSentences[i]
        const cleanSentence = stripForTTS(sentence)
        if (!cleanSentence.trim()) continue

        const result = await synthesizeChunkWithRetry(cleanSentence, i)
        if (stopSpeakRef.current) break

        if (!result) {
          if (i === 0) {
            console.error('[TTS] Unable to synthesize first chunk with HeadTTS. Skipping voice instead of browser fallback.')
            break
          }
          console.warn('[TTS] Skipping broken chunk and continuing with next sentence...')
          continue
        }

        await new Promise((resolve) => {
          setVisemeSchedule(result.visemes)
          const audio = new Audio(result.blobUrl)
          activeAudioRef.current = audio
          audio.onended = () => {
            URL.revokeObjectURL(result.blobUrl)
            setVisemeSchedule(null)
            resolve()
          }
          audio.onerror = () => {
            URL.revokeObjectURL(result.blobUrl)
            setVisemeSchedule(null)
            resolve()
          }
          audio.play().catch(resolve)
        })
      }
    } finally {
      setIsSpeaking(false)
      setVisemeSchedule(null)
      activeAudioRef.current = null
      activeFetchAbortRef.current = null
    }
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
    if (isSpeaking) {
      // Stop all audio immediately
      stopSpeakRef.current = true
      try { activeFetchAbortRef.current?.abort() } catch {}
      if (activeAudioRef.current) {
        try { activeAudioRef.current.pause() } catch {}
        activeAudioRef.current = null
      }
      setIsSpeaking(false)
      setVisemeSchedule(null)
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