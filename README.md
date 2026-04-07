# SQORA

SQORA is an AI-powered competitive exam preparation platform for JEE/NEET aspirants. It combines a real-time AI mentor, auto-generated math and science animations, mock exams, contest features, and local text-to-speech into one learning workspace.

## Features

| Feature | Description |
|---------|-------------|
| AI Mentor | Chat with a Gemini-powered tutor that explains concepts, solves doubts, and maintains context across turns |
| Manim Animations | AI explanations trigger auto-generated animated videos rendered with [Manim](https://www.manim.community/) |
| Mock Exams | Take timed exams with auto-grading and review |
| Contest Arena | Browse upcoming and past contests with scheduling and registration support |
| Context Compaction | Rolling Gemini-based context summarization keeps long chats cheap while preserving full visible history |
| Text-to-Speech | Local TTS server delivers narrated audio explanations |
| Admin Panel | Configure mentor greetings, voice settings, exam highlights, and platform options |
| 3D Landing Page | React Three Fiber-powered interactive landing page |
| Google Auth | Firebase-based Google Sign-In — no passwords needed, sign-in and sign-up unified |
| Multi-User Support | Each user gets fully isolated data scoped by Firebase UID |
| Token Auth | Firebase ID tokens verified server-side — no user can access another user's data |

## Architecture

```text
                    ┌─────────────┐
                    │   Vercel    │
                    │  (Frontend  │
                    │  + Backend) │
                    └──────┬──────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
   React SPA (Static)           FastAPI Serverless (/api/*)
     (Frontend/dist)              (api/index.py → Unmute/)
          │                                 │
          └──── Firebase Auth ──────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
    Firestore (chat)    Firebase Auth (tokens)
          
          ┌────────────────────────┐
          │  Manim Worker          │
          │  (RAID server / VPS)   │
          │  Watches incoming_jobs/│
          │  Serves video files    │
          └────────────────────────┘
```

### Services

| Service | Stack | Deployment |
|---------|-------|------------|
| Frontend | React 18, Vite, React Router, Three.js, KaTeX | Vercel (static) |
| Backend API | FastAPI, Gemini, Firebase Admin | Vercel (serverless Python) |
| Manim Worker | Python, Manim 0.19, Gemini code gen | RAID server / any VPS |
| TTS Server | Python (Pocket-TTS) | RAID server / any VPS |

> **Note:** Manim requires LaTeX, FFmpeg, and long-running processes — it cannot run on Vercel. The worker runs on a persistent server and serves video files through its own endpoint or uploads to cloud storage.

### User Data Architecture

```text
user_data/             ← lives on the Manim/RAID server
└── {firebase_uid}/
    ├── chat_history.json     # Synced to Firestore on every message
    ├── ai_cache.json         # AI response cache
    ├── video_cache.json      # Video ID lookup cache
    ├── incoming_jobs/        # Manim job queue
    └── rendered_videos/      # Generated MP4 files
```

## Getting Started (Local Development)

### Prerequisites

- Node.js 18+
- Python 3.12+
- ffmpeg (required by Manim for video generation)

### 1. Clone and Install

```bash
git clone https://github.com/devlup-labs/sqora.git
cd sqora

# Frontend
cd Frontend && npm install && cd ..

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-dotenv google-genai requests
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# ── AI ─────────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key

# ── Firebase Client SDK ─────────────────────────
# Get from Firebase Console → Project Settings → General → Your apps
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_MEASUREMENT_ID=...

# ── Local dev only ──────────────────────────────
# URL of locally running backend (so frontend can hit it on a different port)
VITE_API_URL=http://localhost:8000
```

### 3. Run Locally

```bash
# Terminal 1 — Frontend dev server
cd Frontend && npm run dev

# Terminal 2 — Backend API
./start_backend.sh

# Terminal 3 — Manim Animation Worker
./start_manim.sh

# Terminal 4 — TTS Server (optional)
./start_tts.sh
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- TTS: `http://localhost:8089`

## Deploying to Vercel

### 1. Push to GitHub

```bash
git push origin main
```

### 2. Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import the **sqora** repository
3. Vercel will auto-detect `vercel.json` at the root

### 3. Set Environment Variables in Vercel Dashboard

Under **Project → Settings → Environment Variables**, add all of the following:

| Variable | Value |
|----------|-------|
| `GEMINI_API_KEY` | Your Gemini API key |
| `VITE_FIREBASE_API_KEY` | From Firebase Console |
| `VITE_FIREBASE_AUTH_DOMAIN` | `your-project.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Your Firebase project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | `your-project.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Sender ID |
| `VITE_FIREBASE_APP_ID` | App ID |
| `VITE_FIREBASE_MEASUREMENT_ID` | Measurement ID |

> **Do NOT set `VITE_API_URL`** — on Vercel the frontend and API share the same domain, so relative `/api/*` paths work automatically.

### 4. Add Your Vercel Domain to Firebase

Firebase Console → **Authentication** → **Authorized domains** → Add your `*.vercel.app` domain.

### 5. Enable Full Token Verification (Recommended for Production)

By default the backend falls back to accepting unverified JWT claims in dev mode. To enable cryptographic verification:

1. Firebase Console → `sqora-devlups` → Project Settings → **Service Accounts**
2. Click **"Generate new private key"** and download the JSON
3. Add the entire JSON as an env variable `FIREBASE_SERVICE_ACCOUNT_JSON` in Vercel (**never commit it**)
4. Add `pip install firebase-admin` to `api/requirements.txt`

### 6. Deploy the Manim Worker Separately

The Manim animation worker must run on a persistent server (RAID, VPS, etc.):

```bash
# On your server
git clone https://github.com/devlup-labs/sqora.git
cd sqora
source .venv/bin/activate
./start_manim.sh
```

The worker watches `user_data/*/incoming_jobs/` and renders videos that are served via the backend's `/api/users/{uid}/videos/{id}` endpoint — which also runs on the same server if you self-host the backend.

## Authentication

- Users sign in with Google via Firebase — no passwords
- Firebase issues a short-lived JWT (ID token)  
- Every API request carries it in `Authorization: Bearer <token>`
- Backend verifies it and extracts `uid` to scope all data access

## API Reference

All endpoints under `/api/` require `Authorization: Bearer <firebase_id_token>` unless otherwise noted.

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
| `POST` | `/api/tts` | — | TTS proxy |

## Self-Hosting on IITJ RAID Server (without Vercel)

If you prefer to self-host the full stack behind Nginx:

### 1. Build the Frontend

```bash
cd Frontend && npm run build   # outputs to Frontend/dist/
```

### 2. Configure Nginx

```nginx
server {
    listen 80;
    server_name your-ip-or-domain;

    location / {
        root /path/to/sqora/Frontend/dist;
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 3. Run Services

```bash
nohup ./start_backend.sh &
nohup ./start_manim.sh &
nohup ./start_tts.sh &
```

## LLM Context Compaction

Long conversations are compacted before sending to Gemini:

1. Full chat history is always stored and shown in UI
2. LLM receives: compacted memory + recent turns + new message
3. When estimated token count exceeds `trigger_tokens`, old context is summarized
4. Configure in `Unmute/config.json` under `llm.context_compaction`

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, React Router, Three.js / React Three Fiber, KaTeX, react-markdown |
| Backend | FastAPI, Google Gemini (`google-genai` SDK), Firebase Admin SDK |
| Animation | Manim 0.19, Gemini code generation, ffmpeg |
| Auth | Firebase Authentication (Google Sign-In) |
| TTS | Pocket-TTS |

## License

MIT
