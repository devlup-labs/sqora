# SQORA

SQORA is an AI-powered competitive exam preparation platform for JEE/NEET aspirants. It combines a real-time AI mentor, auto-generated math and science animations, mock exams, contest features, and local text-to-speech into one learning workspace.

## Features

| Feature | Description |
|---------|-------------|
| AI Mentor | Chat with a Gemini-powered tutor that explains concepts, solves doubts, and maintains context across turns |
| Manim Animations | AI explanations trigger auto-generated animated videos rendered with [Manim](https://www.manim.community/) |
| Mock Exams | Take timed exams with auto-grading and review |
| Contest Arena | Browse upcoming and past contests with scheduling and registration support |
| Streaming Responses | Low-latency AI chat with SSE streaming |
| Context Compaction | Rolling Gemini-based context summarization keeps long chats cheap while preserving full visible history |
| Text-to-Speech | Local TTS server delivers narrated audio explanations |
| Admin Panel | Configure mentor greetings, voice settings, exam highlights, and platform options |
| 3D Landing Page | React Three Fiber-powered interactive landing page |
| Google Auth | Firebase-based Google Sign-In — no passwords needed |
| Multi-User Support | Each user gets a fully isolated folder on the server for chat history, video cache, and rendered animations |
| Token Auth | Firebase ID tokens verified server-side — no user can access another user's data |

## Architecture

The platform is composed of four independent services:

| Service | Stack | Location |
|---------|-------|----------|
| Frontend | React 18, Vite, React Router, Three.js, KaTeX | `Frontend/` |
| Backend | FastAPI, Gemini, Prometheus | `Unmute/` |
| Manim Worker | Python, Manim 0.19, Gemini code generation | `manim/` |
| TTS Server | Python (Pocket-TTS) | `Unmute/unmute/tts/` |

```text
Browser  ──(Firebase Auth)──▶  Google
   │
   │  Bearer Token (JWT)
   ▼
Frontend (5173)  ◀──▶  Backend (8000)  ◀──▶  Manim Worker
                            │
                            └──▶  TTS Server (8089)
```

### User Data Architecture

All user data is stored locally on the server, isolated per user:

```text
user_data/
└── {firebase_uid}/
    ├── chat_history.json     # Persistent chat messages
    ├── ai_cache.json         # Cached AI responses
    ├── video_cache.json      # Video ID lookup cache
    └── rendered_videos/      # Generated Manim MP4 files
```

Manim worker monitors `user_data/*/incoming_jobs/` and renders animations for all users in parallel.

## Getting Started

### Prerequisites

- Node.js 18 or newer
- Python 3.12 or newer
- ffmpeg (required by Manim)

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/devlup-labs/sqora.git
cd sqora
npm install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example and fill in your values:

```bash
cp .env.example .env   # if available, or create .env manually
```

Required variables in `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key

# Firebase (client-side) — get from Firebase Console > Project Settings > General
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_MEASUREMENT_ID=...
```

### 3. Run the Application

Open four terminals from the project root:

```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend API
./start_backend.sh

# Terminal 3: Manim Animation Worker
./start_manim.sh

# Terminal 4: TTS Server (optional)
./start_tts.sh
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- TTS: `http://localhost:8089`

## Authentication

Authentication is handled entirely by **Firebase Google Sign-In** — no passwords or local user database.

- Users sign in with their Google account
- Firebase issues a short-lived JWT (ID token) on login
- Every API request carries this token in the `Authorization: Bearer <token>` header
- The backend verifies the token using the Firebase Admin SDK and extracts the user's `uid`
- All data (chat, videos) is stored under `user_data/{uid}/` — users can only access their own data

### Enabling Full Token Verification (Production)

In development, the backend falls back to accepting an `X-User-Id` header if no service account is configured. To enable cryptographic token verification in production:

1. Firebase Console → `sqora-devlups` → Project Settings → **Service Accounts**
2. Click **"Generate new private key"** and download the JSON
3. Save it as `Unmute/firebase-service-account.json`  
   ⚠️ **Never commit this file — it is in `.gitignore`**
4. Run: `pip install firebase-admin`
5. Restart the backend server

## API Reference

All chat and user endpoints require `Authorization: Bearer <firebase_id_token>`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/chat` | ✅ | Send a message, get AI reply + video_id |
| `GET` | `/api/chat/stream?message=...` | ✅ | SSE stream of AI response tokens |
| `GET` | `/api/users/{uid}/chat` | ✅ | Fetch user's chat history |
| `POST` | `/api/users/{uid}/chat` | ✅ | Save chat history |
| `GET` | `/api/users/{uid}/videos/{id}/status` | ✅ | Check if a video is rendered |
| `GET` | `/api/users/{uid}/videos/{id}` | ✅ | Stream a rendered `.mp4` (byte-range) |
| `GET` | `/api/contests` | — | List contests |
| `GET` | `/api/exams/{code}` | — | Fetch exam questions |
| `GET/PUT` | `/api/admin/config` | — | Read/update platform settings |
| `POST` | `/api/tts` | — | TTS proxy (form: text, voice) |

## Deployment on IITJ RAID Server (No Vercel Required)

The entire stack can be self-hosted behind Nginx. No cloud hosting needed.

### 1. Build the Frontend

```bash
cd Frontend && npm run build   # outputs to Frontend/dist/
```

### 2. Configure Nginx

```nginx
server {
    listen 80;
    server_name your-ip-or-domain;

    # Serve the built React SPA
    location / {
        root /path/to/sqora/Frontend/dist;
        try_files $uri /index.html;
    }

    # Proxy all API calls to the FastAPI backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # For SSE (streaming)
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 3. Enable HTTPS (optional but recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Add Domain to Firebase

Firebase Console → Authentication → **Authorized Domains** → add your server's IP or domain.

### 5. Run Services in Background

```bash
nohup ./start_backend.sh &
nohup ./start_manim.sh &
nohup ./start_tts.sh &
```

Or use `systemd` / `tmux` / `screen` for persistent background services.

## LLM Context Compaction

Long conversations are compacted automatically before sending to Gemini:

1. Full chat history is always stored locally and shown in the UI
2. The LLM receives: compacted memory + recent uncompacted turns + new message
3. When estimated token count reaches `trigger_tokens`, old context is summarized
4. Configure in `Unmute/config.json` under `llm.context_compaction`

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, Vite, React Router, Three.js / React Three Fiber, KaTeX, react-markdown |
| Backend | FastAPI, Google Gemini (new `google-genai` SDK), Firebase Admin SDK |
| Animation | Manim 0.19, Gemini code generation, ffmpeg |
| Auth | Firebase Authentication (Google Sign-In) |
| TTS | Pocket-TTS |

## License

MIT
