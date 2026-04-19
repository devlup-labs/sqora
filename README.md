# SQORA

SQORA is an AI-powered competitive exam preparation platform for JEE/NEET aspirants. It combines a real-time AI mentor, auto-generated math and science animations, mock exams, contest features, and local text-to-speech into one learning workspace.

## Features

| Feature | Description |
|---------|-------------|
| AI Mentor | Chat with a Gemini-powered tutor that explains concepts, solves doubts, and maintains context across turns |
| Manim Animations | AI explanations trigger auto-generated animated videos rendered with [Manim](https://www.manim.community/) |
| Mock Exams | Take timed exams with auto-grading and review |
| Contest Arena | Browse upcoming and past contests |
| Context Compaction | Rolling Gemini-based context summarization keeps long chats efficient |
| Text-to-Speech | Local TTS server delivers narrated audio explanations |
| Admin Panel | Configure mentor greetings, voice settings, and platform options |
| 3D Landing Page | React Three Fiber-powered interactive landing page |
| Google Auth | Firebase Google Sign-In — unified sign-in/sign-up, no passwords |
| Multi-User Support | Fully isolated data per Firebase UID on the server |
| Token Auth | Firebase ID tokens verified server-side — strict data isolation |

## Architecture

```text
┌──────────────────────────────┐       ┌─────────────────────────────────────┐
│        Vercel (CDN)          │       │         IITJ RAID Server            │
│                              │       │                                     │
│   React SPA (static build)   │──────▶│  FastAPI Backend  (port 8000)       │
│                              │       │  Manim Worker     (background)      │
│  VITE_API_URL = raid server  │       │  TTS Server       (port 8882)       │
└──────────────────────────────┘       └─────────────────────────────┬───────┘
                                                                     │
                                              ┌──────────────────────┘
                                              │  Firebase (Google Cloud)
                                              │    • Authentication (JWT)
                                              └──────────────────────
```

### Services

| Service | Stack | Deployment |
|---------|-------|------------|
| Frontend | React 18, Vite, React Router, Three.js, KaTeX | **Vercel** |
| Backend API | FastAPI, Gemini, Firebase Auth | **RAID Server** |
| Manim Worker | Python, Manim 0.19, Gemini code gen | **RAID Server** |
| TTS Server | HeadTTS (Node.js + WebSocket/REST) | **RAID Server** |

### User Data

```text
user_data/               ← on RAID server
└── {firebase_uid}/
    ├── chat_history.json
    ├── ai_cache.json
    ├── video_cache.json
    ├── incoming_jobs/        ← Manim job queue
    └── rendered_videos/      ← generated MP4 files
```

---

## Getting Started (Local Development)

### Prerequisites

- Node.js 18+
- Python 3.12+
- ffmpeg (required by Manim)

### 1. Clone and Install

```bash
git clone https://github.com/devlup-labs/sqora.git
cd sqora

# Frontend
cd Frontend && npm install && cd ..

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_api_key

VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_MEASUREMENT_ID=...

# For local dev: frontend hits backend on port 8000
VITE_API_URL=http://localhost:8000
```

### 3. Run Locally

```bash
# Terminal 1 — Frontend
cd Frontend && npm run dev

# Terminal 2 — Backend API
./start_backend.sh

# Terminal 3 — Manim Worker
./start_manim.sh

# Terminal 4 — HeadTTS Server (optional)
./start_tts.sh
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

---

## Deploying to Vercel (Frontend Only)

### 1. Push to GitHub

```bash
git push origin main
```

### 2. Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import the **sqora** repository
3. Vercel reads `vercel.json` automatically — no extra config needed

### 3. Set Environment Variables in Vercel Dashboard

Under **Project → Settings → Environment Variables**, add:

| Variable | Value |
|----------|-------|
| `VITE_FIREBASE_API_KEY` | From Firebase Console |
| `VITE_FIREBASE_AUTH_DOMAIN` | `your-project.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Your project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | `your-project.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Sender ID |
| `VITE_FIREBASE_APP_ID` | App ID |
| `VITE_FIREBASE_MEASUREMENT_ID` | Measurement ID |
| `VITE_API_URL` | Public URL of your RAID server backend, e.g. `https://sqora.iitj.ac.in` |

> **`VITE_API_URL` is required on Vercel** — it tells the frontend where to send API requests.

### 4. Add Vercel Domain to Firebase

Firebase Console → **Authentication** → **Authorized domains** → Add your `*.vercel.app` URL.

---

## Deploying the Backend on IITJ RAID Server

### 1. Clone and Install

```bash
git clone https://github.com/devlup-labs/sqora.git
cd sqora
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure `.env`

Same as local dev, but **without** `VITE_*` variables (those are frontend-only):

```env
GEMINI_API_KEY=your_key
```

### 3. Enable HTTPS + CORS via Nginx

The frontend is on Vercel and the backend is on the RAID server — this is a **cross-origin** setup. The backend already includes CORS middleware. Expose it through Nginx:

```nginx
server {
    listen 80;
    server_name your-raid-domain-or-ip;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # Required for SSE streaming
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        # Allow Vercel frontend
        add_header 'Access-Control-Allow-Origin' 'https://your-app.vercel.app' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }
}
```

> For HTTPS (strongly recommended): `sudo certbot --nginx -d your-domain.com`

### 4. Enable Full Token Verification

For production security, enable cryptographic token verification:

1. Firebase Console → Project Settings → **Service Accounts** → **Generate new private key**
2. Save as `Unmute/firebase-service-account.json`  
   ⚠️ **Never commit this file — it is in `.gitignore`**
3. `pip install firebase-admin`
4. Restart the backend

### 5. Run Services

```bash
nohup ./start_backend.sh &
nohup ./start_manim.sh &
nohup ./start_tts.sh &   # optional
```

Or use `tmux` / `systemd` for persistent sessions.

---

## Authentication

- Users authenticate with Google via Firebase — no passwords
- Firebase issues a short-lived JWT (ID token) on login
- Every API request carries it as `Authorization: Bearer <token>`
- Backend verifies the token and extracts `uid` to scope all data
- All data lives under `user_data/{uid}/` — users can only access their own

---

## API Reference

All chat and user endpoints require `Authorization: Bearer <firebase_id_token>`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/chat` | ✅ | Send a message, get AI reply + video_id |
| `GET` | `/api/chat/stream?message=...` | ✅ | SSE stream of AI response tokens |
| `GET` | `/api/users/{uid}/chat` | ✅ | Fetch user's chat history |
| `POST` | `/api/users/{uid}/chat` | ✅ | Save chat history |
| `GET` | `/api/users/{uid}/videos/{id}/status` | ✅ | Check if a video is rendered |
| `GET` | `/api/users/{uid}/videos/{id}/ready` | ✅ token param | SSE — fires `ready` when MP4 is done |
| `GET` | `/api/users/{uid}/videos/{id}` | ✅ token param | Stream rendered `.mp4` (byte-range) |
| `GET` | `/api/contests` | — | List contests |
| `GET` | `/api/exams/{code}` | — | Fetch exam questions |
| `GET/PUT` | `/api/admin/config` | — | Read/update platform settings |

---

## LLM Context Compaction

Long conversations are summarized before sending to Gemini:

1. Full history is always stored locally and shown in UI
2. LLM receives: compacted memory + recent turns + new message
3. When estimated token count exceeds `trigger_tokens`, old context is summarized via Gemini
4. Configure in `Unmute/config.json` → `llm.context_compaction`

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, React Router, Three.js / React Three Fiber, KaTeX, react-markdown |
| Backend | FastAPI, Google Gemini (`google-genai` SDK), Firebase Admin SDK |
| Animation | Manim 0.19, Gemini code generation, ffmpeg |
| Auth | Firebase Authentication (Google Sign-In) |
| TTS | HeadTTS |
| Deployment | Vercel (frontend), IITJ RAID Server (backend + worker) |

## License

MIT
