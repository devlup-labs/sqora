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

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Gemini AI client
# ---------------------------------------------------------------------------

_gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
_gemini_client: OpenAI | None = None
if _gemini_api_key:
    _gemini_client = OpenAI(
        api_key=_gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
else:
    logger.warning("GEMINI_API_KEY is not set. /api/chat will return fallback responses.")

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
# Routes – AI Chat
# ---------------------------------------------------------------------------

@router.post("/api/chat")
async def api_chat(body: ChatRequest):
    global ai_response_cache
    if not _gemini_client:
        return {"reply": "AI is not configured. Please set GEMINI_API_KEY."}

    key = _normalize_prompt(body.message)
    if key in ai_response_cache:
        reply = ai_response_cache[key]
        logger.info(f"AI cache hit: {body.message[:50]}")
        lesson_id = _create_animation_job(body.message, _extract_topic(body.message))
        _append_to_chat_history("user", body.message, video_id=lesson_id)
        _append_to_chat_history("assistant", reply)
        return {"reply": reply, "video_id": lesson_id}

    lesson_id = _create_animation_job(body.message, _extract_topic(body.message))
    _append_to_chat_history("user", body.message, video_id=lesson_id)

    try:
        response = await asyncio.to_thread(
            _gemini_client.chat.completions.create,
            model="gemini-2.5-flash",
            reasoning_effort="low",
            messages=[
                {"role": "system", "content": (
                    "You are a friendly and knowledgeable JEE/NEET tutor. "
                    "Give clear, concise explanations with examples. "
                    "Use simple language suitable for Indian high-school students preparing for competitive exams."
                )},
                *[
                    {"role": "assistant" if m["role"] == "ai" else m["role"], "content": m["text"]}
                    for m in chat_history[-10:]
                ],
            ],
            temperature=0,
        )
        reply = response.choices[0].message.content
        ai_response_cache[key] = reply
        _save_json(AI_RESPONSE_CACHE_FILE, ai_response_cache)
        _append_to_chat_history("assistant", reply)
    except Exception as e:
        logger.error("Gemini chat error: %s", e)
        reply = "Sorry, I couldn't process your question right now. Please try again."

    return {"reply": reply, "video_id": lesson_id}


@router.get("/api/chat")
async def api_chat_history():
    return {"history": chat_history}

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

@router.get("/api/admin/config")
async def api_admin_config_get():
    return _admin_config


@router.put("/api/admin/config")
async def api_admin_config_put(body: AdminConfigUpdate):
    for key, value in body.model_dump(exclude_none=True).items():
        _admin_config[key] = value
    return _admin_config
