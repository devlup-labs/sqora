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

from fastapi import APIRouter, HTTPException, File, Form
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from unmute.llm.llm_service import llm_service
from pydantic import BaseModel
import requests

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# File-based caches (relative to Unmute/ working directory)
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).parents[2]          # SQ/
_UNMUTE_DIR = Path(__file__).parents[1]         # SQ/Unmute/
_MANIM_JOBS_DIR = _BASE_DIR / "manim" / "jobs" / "incoming"
_RENDERED_DIR = _BASE_DIR / "manim" / "media" / "rendered"

CHAT_HISTORY_FILE = str(_UNMUTE_DIR / "chat_history.json")
VIDEO_CACHE_FILE = str(_UNMUTE_DIR / "video_cache.json")
AI_RESPONSE_CACHE_FILE = str(_UNMUTE_DIR / "ai_response_cache.json")


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


chat_history: list = _load_json(CHAT_HISTORY_FILE, [])
video_cache: dict = _load_json(VIDEO_CACHE_FILE, {})
ai_response_cache: dict = _load_json(AI_RESPONSE_CACHE_FILE, {})

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


def _create_animation_job(response_text: str, topic: str = "Lesson") -> str:
    global video_cache
    key = _normalize_prompt(response_text)
    if key in video_cache:
        logger.info(f"Video cache hit for: {response_text[:50]}")
        return video_cache[key]

    lesson_id = str(uuid.uuid4())
    _MANIM_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    _save_json(str(_MANIM_JOBS_DIR / f"{lesson_id}.json"), {"topic": topic, "response_text": response_text})

    video_cache[key] = lesson_id
    _save_json(VIDEO_CACHE_FILE, video_cache)
    logger.info(f"Video cache miss. Created job {lesson_id}")
    return lesson_id


def _append_to_chat_history(role: str, text: str, video_id: str | None = None):
    global chat_history
    entry: dict = {"role": role, "text": text}
    if video_id:
        entry["video_id"] = video_id
    chat_history.append(entry)
    _save_json(CHAT_HISTORY_FILE, chat_history)

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

    questions = []
    for si, subj in enumerate(cfg["subjects"]):
        for qi in range(cfg["qPerSubject"]):
            q_num = si * cfg["qPerSubject"] + qi + 1
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
    return {"token": "demo-token", "role": user["role"]}

# ---------------------------------------------------------------------------
@router.post("/api/chat")
async def api_chat(body: ChatRequest):
    global ai_response_cache
    
    key = _normalize_prompt(body.message)
    if key in ai_response_cache:
        reply = ai_response_cache[key]
        logger.info(f"AI cache hit: {body.message[:50]}")
        lesson_id = _create_animation_job(reply, _extract_topic(body.message))
        _append_to_chat_history("user", body.message, video_id=lesson_id)
        _append_to_chat_history("assistant", reply)
        return {"reply": reply, "video_id": lesson_id}

    # Use the modular LLM service to get the response
    reply = await llm_service.get_response(body.message, chat_history)
    
    # Save to cache
    ai_response_cache[key] = reply
    _save_json(AI_RESPONSE_CACHE_FILE, ai_response_cache)
    
    # Create animation job and record history
    lesson_id = _create_animation_job(reply, _extract_topic(body.message))
    _append_to_chat_history("user", body.message, video_id=lesson_id)
    _append_to_chat_history("assistant", reply)

    return {"reply": reply, "video_id": lesson_id}


@router.get("/api/chat")
async def api_chat_history():
    return {"history": chat_history}


@router.get("/api/chat/stream")
async def api_chat_stream(message: str):
    """
    SSE streaming endpoint. Yields:
      data: <token>          — one or more raw text tokens
      data: [DONE] <json>   — final event with full reply + video_id
    """
    from fastapi.responses import StreamingResponse as _SR

    key = _normalize_prompt(message)

    # Cache hit – send all at once but still as SSE
    if key in ai_response_cache:
        cached = ai_response_cache[key]
        lesson_id = _create_animation_job(cached, _extract_topic(message))
        _append_to_chat_history("user", message, video_id=lesson_id)
        _append_to_chat_history("assistant", cached)

        async def _cached_gen():
            yield f"data: {json.dumps({'token': cached})}\n\n"
            yield f"data: [DONE] {json.dumps({'video_id': lesson_id, 'reply': cached})}\n\n"
        return _SR(_cached_gen(), media_type="text/event-stream")

    # Streaming from Gemini
    async def _stream_gen():
        global ai_response_cache
        full_reply = []

        def _iter():
            return llm_service.stream_response(message, chat_history)

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
        _save_json(AI_RESPONSE_CACHE_FILE, ai_response_cache)

        lesson_id = _create_animation_job(reply, _extract_topic(message))
        _append_to_chat_history("user", message, video_id=lesson_id)
        _append_to_chat_history("assistant", reply)

        yield f"data: [DONE] {json.dumps({'video_id': lesson_id, 'reply': reply})}\n\n"

    return _SR(
        _stream_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Routes – Videos
# ---------------------------------------------------------------------------

@router.get("/api/videos/{video_id}/status")
async def api_video_status(video_id: str):
    ready = (_RENDERED_DIR / f"{video_id}.mp4").exists()
    return {"ready": ready}


@router.get("/api/videos/{video_id}")
async def api_video(video_id: str):
    path = _RENDERED_DIR / f"{video_id}.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video not found or still rendering.")
    return FileResponse(str(path), media_type="video/mp4")

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
async def proxy_tts(text: str = Form(...), voice: str = Form("alba")):
    config = _load_json(_UNMUTE_DIR / "config.json", {})
    tts_url = config.get("tts", {}).get("url", "http://localhost:8089/tts")
    print(f"[Proxy TTS] voice={voice} text={text[:50]}... -> {tts_url}")

    def fetch_tts():
        return requests.post(tts_url, data={"text": text, "voice_url": voice}, stream=True)

    try:
        response = await asyncio.to_thread(fetch_tts)
        if response.status_code == 200:
            return StreamingResponse(
                response.iter_content(chunk_size=8192),
                media_type="audio/wav"
            )
        else:
            print(f"[Proxy TTS] Error Body: {response.text}")
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

