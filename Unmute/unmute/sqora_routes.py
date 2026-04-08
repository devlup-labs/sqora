"""
SQORA REST API routes — auth, chat, contests, exams, admin config.
Mounted onto the main FastAPI app in main_websocket.py.
"""

import asyncio
import json
import logging
import os
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, File, Form, Request, Depends
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from unmute.llm.llm_service import llm_service
from unmute.firebase_auth import verify_token
from pydantic import BaseModel
import requests

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Per-request auth — extracts uid from Bearer token
# Falls back to X-User-Id header in dev mode (when no service account)
# ---------------------------------------------------------------------------

def get_current_uid(request: Request) -> str:
    """FastAPI dependency: returns the verified Firebase uid for the caller."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        uid = verify_token(token)
        if uid:
            return uid
        # Token present but invalid
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Dev fallback: allow X-User-Id header when Firebase Admin is not configured
    dev_uid = request.headers.get("X-User-Id", "")
    if dev_uid:
        return dev_uid

    raise HTTPException(status_code=401, detail="Authentication required")

# ---------------------------------------------------------------------------
# File-based caches (relative to Unmute/ working directory)
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).parents[2]          # SQ/
USER_DATA_ROOT = _BASE_DIR / "user_data"

def _load_json(path: str, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
    return default

def _save_json(path: str, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving {path}: {e}")

def get_user_dir(user_id: str) -> Path:
    d = USER_DATA_ROOT / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_video_cache(user_id: str) -> dict:
    return _load_json(str(get_user_dir(user_id) / "video_cache.json"), {})

def save_video_cache(user_id: str, cache: dict):
    _save_json(str(get_user_dir(user_id) / "video_cache.json"), cache)

def get_ai_cache(user_id: str) -> dict:
    return _load_json(str(get_user_dir(user_id) / "ai_cache.json"), {})

def save_ai_cache(user_id: str, cache: dict):
    _save_json(str(get_user_dir(user_id) / "ai_cache.json"), cache)

def get_chat_cache(user_id: str) -> list:
    return _load_json(str(get_user_dir(user_id) / "chat_history.json"), [])

def save_chat_cache(user_id: str, cache: list):
    _save_json(str(get_user_dir(user_id) / "chat_history.json"), cache)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_prompt(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return " ".join(text.lower().strip().split())


def _extract_topic(text: str) -> str:
    lower = text.lower()
    if "ohm" in lower:
        return "Ohm's Law"
    if "maxwell" in lower:
        return "Maxwell's Equations"
    if "integration" in lower:
        return "Integration"
    if "chemical" in lower:
        return "Chemical Reaction"
    if "photosynthesis" in lower:
        return "Photosynthesis"
    return "JEE/NEET Lesson"


def _create_animation_job(response_text: str, user_id: str, topic: str = "Lesson") -> str:
    cache = get_video_cache(user_id)
    key = _normalize_prompt(response_text)
    if key in cache:
        logger.info(f"Video cache hit for: {str(response_text)[:50]}")
        return cache[key]

    lesson_id = str(uuid.uuid4())
    job_dir = get_user_dir(user_id) / "incoming_jobs"
    job_dir.mkdir(parents=True, exist_ok=True)
    _save_json(str(job_dir / f"{lesson_id}.json"), {"topic": topic, "response_text": response_text})

    cache[key] = lesson_id
    save_video_cache(user_id, cache)
    logger.info(f"Video cache miss. Created job {lesson_id}")
    return lesson_id


# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------

_users_db: dict[str, dict] = {
    "admin@sqora.com": {
        "name": "Admin",
        "email": "admin@sqora.com",
        "password": "Admin@5410",
        "role": "admin",
    },
}

_admin_config: dict[str, object] = {
    "mentorGreeting": "Hi! I am your AI mentor. Tap the mic or open chat to ask anything about your prep.",
    "voiceEnabled": True,
    "highlightedExam": "",
    "showContestsOnHome": True,
    "aiOnlyAnswers": True,
    "flagSensitive": False,
}

_contests_upcoming = [
    {"code": "JEE-DEMO",  "name": "JEE Main Demo Paper – Full PCM Syllabus", "start": "Live Now", "length": "03:00", "beforeStart": "Started", "beforeReg": "Open"},
    {"code": "NEET-DEMO", "name": "NEET Demo Paper – Full Syllabus",        "start": "Live Now", "length": "03:00", "beforeStart": "Started", "beforeReg": "Open"},
    {"code": "NEET-M1", "name": "NEET Mock 1 – Physics, Chemistry, Biology", "start": "Jan/29/2026 20:05 UTC+5.5", "length": "03:00", "beforeStart": "2 days", "beforeReg": "1 day"},
    {"code": "JEE-M2",  "name": "JEE Main Mock 2 – PCM",                    "start": "Feb/02/2026 17:30 UTC+5.5", "length": "03:00", "beforeStart": "6 days", "beforeReg": "5 days"},
    {"code": "NEET-M2", "name": "NEET Mock 2 – Full syllabus",               "start": "Feb/05/2026 21:00 UTC+5.5", "length": "03:00", "beforeStart": "9 days", "beforeReg": "8 days"},
]

_contests_past = [
    {"code": "JEE-M1",  "name": "JEE Main Mock 1 – PCM",        "start": "Jan/26/2026 20:05 UTC+5.5", "length": "03:00", "participants": "43326", "unrated": True},
    {"code": "NEET-P1", "name": "NEET Previous Year 1",          "start": "Jan/22/2026 19:30 UTC+5.5", "length": "03:00", "participants": "28104", "unrated": False},
    {"code": "JEE-A1",  "name": "JEE Advanced Mock 1",           "start": "Jan/18/2026 21:00 UTC+5.5", "length": "03:00", "participants": "8912",  "unrated": False},
]

_exam_store: dict[str, dict] = {}


def _get_exam(code: str) -> dict:
    if code in _exam_store:
        return _exam_store[code]
    is_neet = code.upper().startswith("NEET")
    if is_neet:
        cfg = {"subjects": ["Physics", "Chemistry", "Botany", "Zoology"], "qPerSubject": 45, "totalQ": 180}
    else:
        cfg = {"subjects": ["Physics", "Chemistry", "Mathematics"], "qPerSubject": 25, "totalQ": 75}

    subjects: list[str] = cfg["subjects"] # type: ignore
    q_per_subj: int = cfg["qPerSubject"] # type: ignore

    questions = []
    for si, subj in enumerate(subjects):
        for qi in range(q_per_subj):
            q_num = si * q_per_subj + qi + 1
            questions.append({
                "number": q_num, "subject": subj,
                "text": f"[{subj} Q{qi+1}] Which of the following best describes the concept?",
                "options": {"A": f"Option A for {subj} Q{qi+1}", "B": f"Option B for {subj} Q{qi+1}",
                             "C": f"Option C for {subj} Q{qi+1}", "D": f"Option D for {subj} Q{qi+1}"},
                "correct": "A", "scoring": "+4 / -1",
            })
    _exam_store[code] = {"code": code, "config": cfg, "questions": questions}
    return _exam_store[code]

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AuthSignup(BaseModel):
    name: str
    email: str
    password: str

class AuthLogin(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str
    history: list = []
    # user_id removed: now extracted from verified Bearer token


class AdminConfigUpdate(BaseModel):
    mentorGreeting: str | None = None
    voiceEnabled: bool | None = None
    highlightedExam: str | None = None
    showContestsOnHome: bool | None = None
    aiOnlyAnswers: bool | None = None
    flagSensitive: bool | None = None

# ---------------------------------------------------------------------------
# Routes – Auth
# ---------------------------------------------------------------------------

@router.post("/api/auth/signup")
async def api_signup(body: AuthSignup):
    if body.email in _users_db:
        raise HTTPException(status_code=400, detail="Email already registered.")
    _users_db[body.email] = {"name": body.name, "email": body.email, "password": body.password, "role": "user"}
    return {"token": "demo-token", "role": "user"}


@router.post("/api/auth/login")
async def api_login(body: AuthLogin):
    user = _users_db.get(body.email)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return JSONResponse({"token": "demo-token", "role": user["role"]})

# ---------------------------------------------------------------------------
@router.post("/api/chat")
async def api_chat(body: ChatRequest, uid: str = Depends(get_current_uid)):
    user_id = uid
    ai_response_cache = get_ai_cache(user_id)
    key = _normalize_prompt(body.message)
    
    # 1. Cache hit – send all at once
    if key in ai_response_cache:
        reply = ai_response_cache[key]
        logger.info(f"AI cache hit: {str(body.message)[:50]}")
        lesson_id = _create_animation_job(reply, user_id, _extract_topic(body.message))
        return {"reply": reply, "video_id": lesson_id}

    try:
        # 2. Call LLM with timeout
        reply = await asyncio.wait_for(
            llm_service.get_response(body.message, body.history),
            timeout=25
        )
    except asyncio.TimeoutError:
        logger.error("TIMEOUT: Gemini response taking too long")
        reply = "Sorry, AI is taking too long. Please try again."
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        reply = f"AI error occurred: {str(e)}"

    # 3. Save to cache if valid
    if reply and "AI error" not in reply:
        ai_response_cache[key] = reply
        save_ai_cache(user_id, ai_response_cache)
    
    # 4. Create animation job
    lesson_id = _create_animation_job(reply, user_id, _extract_topic(body.message))
    return {"reply": reply, "video_id": lesson_id}


@router.get("/api/users/{user_id}/chat")
async def api_chat_history(user_id: str, uid: str = Depends(get_current_uid)):
    if uid != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"history": get_chat_cache(user_id)}

@router.post("/api/users/{user_id}/chat")
async def api_chat_history_sync(user_id: str, request: Request, uid: str = Depends(get_current_uid)):
    if uid != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    data = await request.json()
    save_chat_cache(user_id, data.get("history", []))
    return {"success": True}


@router.get("/api/chat/stream")
async def api_chat_stream(message: str, request: Request, uid: str = Depends(get_current_uid)):
    user_id = uid
    """
    SSE streaming endpoint. Yields:
      data: <token>          — one or more raw text tokens
      data: [DONE] <json>   — final event with full reply + video_id
    """
    key = _normalize_prompt(message)
    ai_response_cache = get_ai_cache(user_id)

    # Cache hit – send all at once but still as SSE
    if key in ai_response_cache:
        cached = ai_response_cache[key]
        lesson_id = _create_animation_job(cached, user_id, _extract_topic(message))

        async def _cached_gen():
            yield f"data: {json.dumps({'token': cached})}\n\n"
            yield f"data: [DONE] {json.dumps({'video_id': lesson_id, 'reply': cached})}\n\n"
        return StreamingResponse(_cached_gen(), media_type="text/event-stream")

    # Streaming from Gemini
    async def _stream_gen():
        full_reply = []

        def _iter():
            return llm_service.stream_response(message, [])

        loop = asyncio.get_event_loop()
        q: asyncio.Queue = asyncio.Queue()

        def _producer():
            try:
                for token in _iter():
                    loop.call_soon_threadsafe(q.put_nowait, token)
            finally:
                loop.call_soon_threadsafe(q.put_nowait, None)  # sentinel

        import threading
        threading.Thread(target=_producer, daemon=True).start()

        while True:
            token = await q.get()
            if token is None:
                break
            full_reply.append(token)
            yield f"data: {json.dumps({'token': token})}\n\n"

        reply = "".join(full_reply)
        ai_response_cache[key] = reply
        save_ai_cache(user_id, ai_response_cache)

        lesson_id = _create_animation_job(reply, user_id, _extract_topic(message))

        yield f"data: [DONE] {json.dumps({'video_id': lesson_id, 'reply': reply})}\n\n"

    return StreamingResponse(
        _stream_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Routes – Videos
# ---------------------------------------------------------------------------

@router.get("/api/users/{user_id}/videos/{video_id}/status")
async def api_video_status(user_id: str, video_id: str, uid: str = Depends(get_current_uid)):
    if uid != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    path = get_user_dir(user_id) / "rendered_videos" / f"{video_id}.mp4"
    return {"ready": path.exists()}


@router.get("/api/users/{user_id}/videos/{video_id}/ready")
async def api_video_ready_sse(user_id: str, video_id: str, request: Request, token: str = ""):
    """SSE endpoint: holds open until the mp4 exists, then fires 'ready'.
    Accepts auth via Bearer header OR ?token= query param (needed for EventSource).
    """
    from unmute.firebase_auth import verify_token, _unverified_decode
    # Auth: prefer header, fall back to query param for EventSource clients
    auth_header = request.headers.get("Authorization", "")
    raw_token = auth_header[7:] if auth_header.startswith("Bearer ") else token
    uid = verify_token(raw_token) if raw_token else None
    if not uid:
        uid = request.headers.get("X-User-Id", "")
    if not uid or uid != user_id:
        from fastapi.responses import Response
        return Response(status_code=401)

    path = get_user_dir(user_id) / "rendered_videos" / f"{video_id}.mp4"

    async def _watch():
        for _ in range(240):          # max ~4 minutes
            if path.exists():
                yield "data: ready\n\n"
                return
            yield "data: waiting\n\n"
            await asyncio.sleep(1)
        yield "data: timeout\n\n"

    return StreamingResponse(
        _watch(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/api/users/{user_id}/videos/{video_id}")
async def api_video(user_id: str, video_id: str, request: Request, token: str = ""):
    """Byte-range streaming endpoint. Accepts auth via Bearer header or ?token= query param."""
    # Auth: header preferred, fallback to query param (needed for <video> src)
    auth_header = request.headers.get("Authorization", "")
    raw_token = auth_header[7:] if auth_header.startswith("Bearer ") else token
    from unmute.firebase_auth import verify_token
    uid = verify_token(raw_token) if raw_token else None
    if not uid:
        uid = request.headers.get("X-User-Id", "")
    if not uid or uid != user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    path = get_user_dir(user_id) / "rendered_videos" / f"{video_id}.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video not found or still rendering.")

    file_size = path.stat().st_size
    range_header = request.headers.get("range")

    start, end = 0, file_size - 1
    status_code = 200
    if range_header:
        match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            status_code = 206

    chunk_size = 256 * 1024  # 256 KB

    async def _iter():
        with open(path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                data = f.read(min(chunk_size, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Type": "video/mp4",
    }
    return StreamingResponse(_iter(), status_code=status_code, headers=headers)

# ---------------------------------------------------------------------------
# Routes – Contests
# ---------------------------------------------------------------------------

@router.get("/api/contests")
async def api_contests():
    return {"upcoming": _contests_upcoming, "past": _contests_past}

# ---------------------------------------------------------------------------
# Routes – Exams
# ---------------------------------------------------------------------------

@router.get("/api/exams/{code}")
async def api_exam(code: str):
    return _get_exam(code)

# ---------------------------------------------------------------------------
# Routes – Admin config
# ---------------------------------------------------------------------------

@router.post("/api/tts")
async def proxy_tts(text: str = Form(...), voice: str = Form("af_bella")):
    _UNMUTE_DIR = Path(__file__).parents[1]
    config = _load_json(str(_UNMUTE_DIR / "config.json"), {})
    tts_url: str = config.get("tts", {}).get("url", "http://localhost:8089/tts")
    logger.info(f"[Proxy TTS] voice={voice} text={str(text)[:50]}... -> {tts_url}")

    def fetch_tts():
        # Pocket-TTS HTTP API expects `voice` (not `voice_url`) for named voices.
        return requests.post(tts_url, data={"text": text, "voice": voice}, stream=True)

    try:
        response = await asyncio.to_thread(fetch_tts)
        if response.status_code == 200:
            return StreamingResponse(
                response.iter_content(chunk_size=8192),
                media_type="audio/wav"
            )
        else:
            logger.error(f"[Proxy TTS] Error Body: {str(response.text)}")
            raise HTTPException(status_code=response.status_code, detail="Configured TTS Server Error")
    except Exception as e:
        logger.error(f"TTS Proxy request failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to TTS server")

@router.get("/api/admin/config")
async def api_admin_config_get():
    return _admin_config


@router.put("/api/admin/config")
async def api_admin_config_put(body: AdminConfigUpdate):
    for key, value in body.model_dump(exclude_none=True).items():
        _admin_config[key] = value
    return _admin_config
