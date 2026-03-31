# SQORA

SQORA is an AI-powered competitive exam preparation platform for JEE/NEET aspirants. It combines a real-time AI mentor, auto-generated math and science animations, mock exams, contest features, and local text-to-speech into one learning workspace.

## Features

| Feature | Description |
|---------|-------------|
| AI Mentor | Chat with a Gemini-powered tutor that explains concepts, solves doubts, and maintains context across turns |
| Manim Animations | AI explanations can trigger auto-generated animated videos rendered with [Manim](https://www.manim.community/) |
| Mock Exams | Take timed exams with auto-grading and review |
| Contest Arena | Browse upcoming and past contests with scheduling and registration support |
| Streaming Responses | Low-latency AI chat with streaming responses |
| Context Compaction | Rolling Gemini-based context summarization keeps long chats cheap while preserving full visible history |
| Text-to-Speech | Local TTS server delivers narrated audio explanations |
| Admin Panel | Configure mentor greetings, voice settings, exam highlights, and platform options |
| 3D Landing Page | React Three Fiber-powered landing page |

## Architecture

The platform is composed of four independent services that communicate through WebSockets, HTTP, and a file-based job queue:

| Service | Stack | Location |
|---------|-------|----------|
| Frontend | React 18, Vite, React Router, Three.js, KaTeX | `Frontend/` + root config |
| Backend | FastAPI, Gemini, Prometheus | `Unmute/` |
| Manim Worker | Python, Manim 0.19, Gemini code generation | `manim/` |
| TTS Server | Python (Pocket-TTS) | `Unmute/unmute/tts/` |

```text
Frontend (5173)  <-->  Backend (8000)  <-->  Manim Worker
                           |
                           +--> TTS Server (8089)
```

## Directory Overview

```text
sqora/
├── Frontend/              # React SPA
├── Unmute/                # FastAPI backend
│   └── unmute/
│       ├── llm/           # Gemini LLM integration
│       ├── tts/           # Text-to-speech server
│       ├── sqora_routes.py
│       ├── main_websocket.py
│       ├── quest_manager.py
│       └── metrics.py
├── manim/                 # Animation rendering worker
├── start_backend.sh       # Launch backend server
├── start_manim.sh         # Launch Manim worker
├── start_tts.sh           # Launch TTS server
├── requirements.txt       # Unified Python dependencies
├── package.json           # Frontend dependencies
└── vite.config.js         # Vite configuration
```

## Getting Started

### Prerequisites

- Node.js 18 or newer
- Python 3.12 or newer
- ffmpeg for Manim rendering

### 1. Install Dependencies

From the project root:

```bash
npm install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Application

Open four terminals and run the following commands from the project root:

```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
./start_backend.sh

# Terminal 3: Manim Worker
./start_manim.sh

# Terminal 4: Pocket-TTS Server
./start_tts.sh
```

Frontend runs at `http://localhost:5173`, backend at `http://localhost:8000`, and TTS at `http://localhost:8089`.

If port `8089` is already in use, `start_tts.sh` reuses the existing Pocket-TTS server instead of starting a duplicate.

### Optional: Run the Backend Manually

If you want to launch the backend directly instead of using the script:

```bash
cd Unmute
source ../.venv/bin/activate
uvicorn unmute.main_websocket:app --reload --port 8000 --app-dir .
```

## API Highlights

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/signup` | Register a new user |
| `POST` | `/api/login` | Authenticate and receive a token |
| `POST` | `/api/chat` | Send a message and get an AI response |
| `GET` | `/api/chat/stream?message=...` | Stream AI tokens over SSE |
| `GET` | `/api/chat/history` | Retrieve chat history |
| `GET` | `/api/video/{id}/status` | Check whether a video is ready |
| `GET` | `/api/video/{id}` | Stream a rendered `.mp4` |
| `GET` | `/api/contests` | List contests |
| `GET` | `/api/exam/{code}` | Fetch exam questions |
| `POST` | `/api/exam/{code}/submit` | Submit answers and get a score |
| `GET/PUT` | `/api/admin/config` | Read and update platform settings |

## LLM Context Compaction

Long conversations are compacted before sending context to Gemini (OpenAI-compatible endpoint):

1. Full chat history is still stored and returned to the UI.
2. The LLM receives compacted memory + unsummarized recent turns + the new user message.
3. When estimated context reaches `trigger_tokens`, the service summarizes old context into a new compacted memory block.
4. If still too large, it compacts again so requests stay under `max_context_tokens`.

Configure this in [Unmute/config.json](Unmute/config.json) under `llm.context_compaction`.

### Backend-only Manual Test (No Manim)

Use this flow to validate compaction without starting the Manim worker:

1. Start only the backend:

```bash
./start_backend.sh
```

2. Send a baseline chat request:

```bash
curl -sS -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Explain Newton\u0027s second law in two lines."}'
```

3. Send larger prompts to trigger compaction:

```bash
python - <<'PY'
import json, urllib.request

url = 'http://127.0.0.1:8000/api/chat'
for i in range(5):
    payload = {
        'message': f'Compaction test turn {i+1}. Keep the answer short. ' + ('context ' * 500)
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        print(f"turn={i+1} reply_chars={len(body.get('reply', ''))}")
PY
```

4. Inspect compaction state:

```bash
cat Unmute/chat_compaction_state.json
```

5. Confirm user-visible history is still full:

```bash
curl -sS http://127.0.0.1:8000/api/chat | python -m json.tool
```

## Tech Stack

Frontend: React 18, Vite, React Router, Three.js / React Three Fiber, KaTeX, react-markdown

Backend: FastAPI, Google Gemini, Prometheus, Redis, msgpack

Animation: Manim 0.19, Gemini code generation

TTS: Pocket-TTS

## License

MIT
