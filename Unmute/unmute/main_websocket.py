import asyncio
import base64
import json
import logging
import os
import uuid
from functools import cache, partial
from typing import Annotated


import numpy as np
import requests
from openai import OpenAI
import sphn
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketState
from fastrtc import AdditionalOutputs, CloseStream, audio_to_float32
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field, TypeAdapter, ValidationError, computed_field
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

import unmute.openai_realtime_api_events as ora
from unmute import metrics as mt
from unmute.exceptions import (
    MissingServiceAtCapacity,
    MissingServiceTimeout,
    WebSocketClosedError,
    make_ora_error,
)
from unmute.kyutai_constants import (
    KYUTAI_LLM_API_KEY,
    LLM_SERVER,
    MAX_VOICE_FILE_SIZE_MB,
    SAMPLE_RATE,
    STT_SERVER,
    TTS_SERVER,
)
from unmute.service_discovery import async_ttl_cached
from unmute.timer import Stopwatch
from unmute.tts.voices import VoiceList
from unmute.unmute_handler import UnmuteHandler

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# We prefer to scale this by running more instances of the server than having a single
# server handle more. This is to avoid the GIL.
MAX_CLIENTS = 4
SEMAPHORE = asyncio.Semaphore(MAX_CLIENTS)



ClientEventAdapter = TypeAdapter(
    Annotated[ora.ClientEvent, Field(discriminator="type")]
)

# Allow CORS for local development
CORS_ALLOW_ORIGINS = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "You've reached the Unmute backend server."}


def _ws_to_http(ws_url: str) -> str:
    """Convert a WebSocket URL to an HTTP URL."""
    return ws_url.replace("ws://", "http://").replace("wss://", "https://")


def _check_server_status(server_url: str, headers: dict | None = None) -> bool:
    """Check if the server is up by sending a GET request."""
    try:
        response = requests.get(
            server_url,
            timeout=2,
            headers=headers or {},
        )
        logger.info(f"Response from {server_url}: {response}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.info(f"Couldn't connect to {server_url}: {e}")
        return False





class HealthStatus(BaseModel):
    tts_up: bool
    stt_up: bool
    llm_up: bool

    @computed_field
    @property
    def ok(self) -> bool:
        # Note that voice cloning is not required for the server to be healthy.
        return self.tts_up and self.stt_up and self.llm_up


@partial(async_ttl_cached, ttl_sec=0.5)
async def _get_health(
    _none: None,
):  # dummy param _none because caching function expects a single param as cache key.
    async with asyncio.TaskGroup() as tg:
        tts_up = tg.create_task(
            asyncio.to_thread(
                _check_server_status, _ws_to_http(TTS_SERVER) + "/api/build_info"
            )
        )
        stt_up = tg.create_task(
            asyncio.to_thread(
                _check_server_status, _ws_to_http(STT_SERVER) + "/api/build_info"
            )
        )
        llm_up = tg.create_task(
            asyncio.to_thread(
                _check_server_status,
                _ws_to_http(LLM_SERVER) + "/v1/models",
                # The default vLLM server doesn't use auth, but this is needed if you
                # use OpenAI or another LLM server.
                headers={"Authorization": f"Bearer {KYUTAI_LLM_API_KEY}"},
            )
        )
        tts_up_res = await tts_up
        stt_up_res = await stt_up
        llm_up_res = await llm_up

    return HealthStatus(
        tts_up=tts_up_res,
        stt_up=stt_up_res,
        llm_up=llm_up_res,
    )


@app.get("/v1/health")
async def get_health():
    health = await _get_health(None)
    mt.HEALTH_OK.observe(health.ok)
    return health





@app.websocket("/v1/realtime")
async def websocket_route(websocket: WebSocket):
    mt.SESSIONS.inc()
    mt.ACTIVE_SESSIONS.inc()
    session_watch = Stopwatch()
    async with SEMAPHORE:
        try:
            # The `subprotocol` argument is important because the client specifies what
            # protocol(s) it supports and OpenAI uses "realtime" as the value. If we
            # don't set this, the client will think this is not the right endpoint and
            # will not connect.
            await websocket.accept(subprotocol="realtime")

            handler = UnmuteHandler()
            async with handler:
                await handler.start_up()
                await _run_route(websocket, handler)

        except Exception as exc:
            await _report_websocket_exception(websocket, exc)
        finally:
            mt.ACTIVE_SESSIONS.dec()
            mt.SESSION_DURATION.observe(session_watch.time())


async def _report_websocket_exception(websocket: WebSocket, exc: Exception):
    if isinstance(exc, ExceptionGroup):
        exceptions = exc.exceptions
    else:
        exceptions = [exc]

    error_message = None

    for exc in exceptions:
        if isinstance(exc, (MissingServiceAtCapacity)):
            mt.FATAL_SERVICE_MISSES.inc()
            error_message = (
                f"Too many people are connected to service '{exc.service}'. "
                "Please try again later."
            )
        elif isinstance(exc, MissingServiceTimeout):
            mt.FATAL_SERVICE_MISSES.inc()
            error_message = (
                f"Service '{exc.service}' timed out. Please try again later."
            )
        elif isinstance(exc, WebSocketClosedError):
            logger.debug("Websocket was closed.")
        else:
            logger.exception("Unexpected error: %r", exc)
            mt.HARD_ERRORS.inc()
            error_message = "Internal server error :( Complain to Kyutai"

    if error_message is not None:
        mt.FORCE_DISCONNECTS.inc()

        try:
            await websocket.send_text(
                make_ora_error(type="fatal", message=error_message).model_dump_json()
            )
        except WebSocketDisconnect:
            logger.warning("Failed to send error message due to disconnect.")

        try:
            await websocket.close(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=error_message,
            )
        except RuntimeError:
            logger.warning("Socket already closed.")


async def _run_route(websocket: WebSocket, handler: UnmuteHandler):
    health = await get_health()
    if not health.ok:
        logger.info("Health check failed, closing WebSocket connection.")
        await websocket.close(
            code=status.WS_1011_INTERNAL_ERROR,
            reason=f"Server is not healthy: {health}",
        )
        return

    emit_queue: asyncio.Queue[ora.ServerEvent] = asyncio.Queue()
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                receive_loop(websocket, handler, emit_queue), name="receive_loop()"
            )
            tg.create_task(
                emit_loop(websocket, handler, emit_queue), name="emit_loop()"
            )
            tg.create_task(handler.quest_manager.wait(), name="quest_manager.wait()")
    finally:
        await handler.cleanup()
        logger.info("websocket_route() finished")


async def receive_loop(
    websocket: WebSocket,
    handler: UnmuteHandler,
    emit_queue: asyncio.Queue[ora.ServerEvent],
):
    """Receive messages from the WebSocket.

    Can decide to send messages via `emit_queue`.
    """
    opus_reader = sphn.OpusStreamReader(SAMPLE_RATE)
    wait_for_first_opus = True
    while True:
        try:
            message_raw = await websocket.receive_text()
        except WebSocketDisconnect as e:
            logger.info(
                "receive_loop() stopped because WebSocket disconnected: "
                f"{e.code=} {e.reason=}"
            )
            raise WebSocketClosedError() from e
        except RuntimeError as e:
            # This is expected when the client disconnects
            if "WebSocket is not connected" not in str(e):
                raise  # re-raise unexpected errors

            logger.info("receive_loop() stopped because WebSocket disconnected.")
            raise WebSocketClosedError() from e

        try:
            message: ora.ClientEvent = ClientEventAdapter.validate_json(message_raw)
        except json.JSONDecodeError as e:
            await emit_queue.put(
                ora.Error(
                    error=ora.ErrorDetails(
                        type="invalid_request_error",
                        message=f"Invalid JSON: {e}",
                    )
                )
            )
            continue
        except ValidationError as e:
            await emit_queue.put(
                ora.Error(
                    error=ora.ErrorDetails(
                        type="invalid_request_error",
                        message="Invalid message",
                        details=json.loads(e.json()),
                    )
                )
            )
            continue

        message_to_record = message

        if isinstance(message, ora.InputAudioBufferAppend):
            opus_bytes = base64.b64decode(message.audio)
            if wait_for_first_opus:
                # Somehow the UI is sending us potentially old messages from a previous
                # connection on reconnect, so that we might get some old OGG packets,
                # waiting for the bit set for first packet to feed to the decoder.
                if opus_bytes[5] & 2:
                    wait_for_first_opus = False
                else:
                    continue
            pcm = await asyncio.to_thread(opus_reader.append_bytes, opus_bytes)

            message_to_record = ora.UnmuteInputAudioBufferAppendAnonymized(
                number_of_samples=pcm.size,
            )

            if pcm.size:
                await handler.receive((SAMPLE_RATE, pcm[np.newaxis, :]))
        elif isinstance(message, ora.SessionUpdate):
            await handler.update_session(message.session)
            await emit_queue.put(ora.SessionUpdated(session=message.session))

        elif isinstance(message, ora.UnmuteAdditionalOutputs):
            # Don't record this: it's a debugging message and can be verbose. Anything
            # important to store should be in the other event types.
            message_to_record = None

        else:
            logger.info("Ignoring message:", str(message)[:100])

        if message_to_record is not None and handler.recorder is not None:
            await handler.recorder.add_event("client", message_to_record)


class EmitDebugLogger:
    def __init__(self):
        self.last_emitted_n = 0
        self.last_emitted_type = ""

    def on_emit(self, to_emit: ora.ServerEvent):
        if self.last_emitted_type == to_emit.type:
            self.last_emitted_n += 1
        else:
            self.last_emitted_n = 1
            self.last_emitted_type = to_emit.type

        if self.last_emitted_n == 1:
            logger.debug(f"Emitting: {to_emit.type}")
        else:
            logger.debug(f"Emitting ({self.last_emitted_n}): {self.last_emitted_type}")


async def emit_loop(
    websocket: WebSocket,
    handler: UnmuteHandler,
    emit_queue: asyncio.Queue[ora.ServerEvent],
):
    """Send messages to the WebSocket."""
    emit_debug_logger = EmitDebugLogger()

    opus_writer = sphn.OpusStreamWriter(SAMPLE_RATE)

    while True:
        if (
            websocket.application_state == WebSocketState.DISCONNECTED
            or websocket.client_state == WebSocketState.DISCONNECTED
        ):
            logger.info("emit_loop() stopped because WebSocket disconnected")
            raise WebSocketClosedError()

        try:
            to_emit = emit_queue.get_nowait()
        except asyncio.QueueEmpty:
            emitted_by_handler = await handler.emit()

            if emitted_by_handler is None:
                continue
            elif isinstance(emitted_by_handler, AdditionalOutputs):
                assert len(emitted_by_handler.args) == 1
                to_emit = ora.UnmuteAdditionalOutputs(
                    args=emitted_by_handler.args[0],
                )
            elif isinstance(emitted_by_handler, CloseStream):
                # Close here explicitly so that the receive loop stops too
                await websocket.close()
                break
            elif isinstance(emitted_by_handler, ora.ServerEvent):
                to_emit = emitted_by_handler
            else:
                _sr, audio = emitted_by_handler
                audio = audio_to_float32(audio)
                opus_bytes = await asyncio.to_thread(opus_writer.append_pcm, audio)
                # Due to buffering/chunking, Opus doesn't necessarily output something on every PCM added
                if opus_bytes:
                    to_emit = ora.ResponseAudioDelta(
                        delta=base64.b64encode(opus_bytes).decode("utf-8"),
                    )
                else:
                    continue

        emit_debug_logger.on_emit(to_emit)

        if handler.recorder is not None:
            await handler.recorder.add_event("server", to_emit)

        try:
            await websocket.send_text(to_emit.model_dump_json())
        except (WebSocketDisconnect, RuntimeError) as e:
            if isinstance(e, RuntimeError):
                if "Unexpected ASGI message 'websocket.send'" in str(e):
                    # This is expected when the client disconnects
                    message = f"emit_loop() stopped because WebSocket disconnected: {e}"
                else:
                    raise
            else:
                message = (
                    "emit_loop() stopped because WebSocket disconnected: "
                    f"{e.code=} {e.reason=}"
                )

            logger.info(message)
            raise WebSocketClosedError() from e


def _cors_headers_for_error(request: Request):
    origin = request.headers.get("origin")
    allow_origin = origin if origin in CORS_ALLOW_ORIGINS else None
    headers = {"Access-Control-Allow-Credentials": "true"}
    if allow_origin:
        headers["Access-Control-Allow-Origin"] = allow_origin

    return headers


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # We need this so that CORS header are added even when the route raises an
    # exception. Otherwise you get a confusing CORS error even if the issue is totally
    # unrelated.
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=_cors_headers_for_error(request),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # We need this so that CORS header are added even when the route raises an
    # exception. Otherwise you get a confusing CORS error even if the issue is totally
    # unrelated.
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=_cors_headers_for_error(request),
    )


# ---------------------------------------------------------------------------
# SQORA API endpoints – auth, chat, contests, exams, admin config
# These endpoints serve the SQORA React frontend.
# ---------------------------------------------------------------------------

# Gemini AI client (OpenAI-compatible)



_gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
_gemini_client: OpenAI | None = None
if _gemini_api_key:
    _gemini_client = OpenAI(
        api_key=_gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
else:
    logger.warning("GEMINI_API_KEY is not set. /api/chat will return fallback responses.")



CHAT_HISTORY_FILE = "chat_history.json"
VIDEO_CACHE_FILE = "video_cache.json"
AI_RESPONSE_CACHE_FILE = "ai_response_cache.json"

def _load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading chat history: {e}")
            return []
    return []

def _load_video_cache():
    """Load the video cache that maps normalized prompts to video IDs."""
    if os.path.exists(VIDEO_CACHE_FILE):
        try:
            with open(VIDEO_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading video cache: {e}")
            return {}
    return {}

def _save_video_cache(cache: dict):
    """Save the video cache to disk."""
    try:
        with open(VIDEO_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving video cache: {e}")

def _load_ai_response_cache():
    """Load the AI response cache that maps normalized prompts to AI responses."""
    if os.path.exists(AI_RESPONSE_CACHE_FILE):
        try:
            with open(AI_RESPONSE_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading AI response cache: {e}")
            return {}
    return {}

def _save_ai_response_cache(cache: dict):
    """Save the AI response cache to disk."""
    try:
        with open(AI_RESPONSE_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving AI response cache: {e}")

def _normalize_prompt(text: str) -> str:
    """Normalize a prompt for cache lookup by removing punctuation, symbols, extra whitespace, and lowercasing."""
    import re
    # Remove all non-alphanumeric characters except spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Lowercase and collapse multiple spaces
    return " ".join(text.lower().strip().split())

chat_history = _load_chat_history()
video_cache = _load_video_cache()
ai_response_cache = _load_ai_response_cache()

def _extract_topic(text: str) -> str:
    """
    Simple dynamic topic detection.
    Can later upgrade to NLP/LLM classification.
    """

    lower_text = text.lower()

    if "ohm" in lower_text:
        return "Ohm's Law"
    if "maxwell" in lower_text:
        return "Maxwell's Equations"
    if "integration" in lower_text:
        return "Integration"
    if "chemical" in lower_text:
        return "Chemical Reaction"
    if "photosynthesis" in lower_text:
        return "Photosynthesis"

    # Default fallback
    return "JEE/NEET Lesson"


def _create_animation_job(response_text: str, topic: str = "Lesson"):
    """Create a manim animation job, or return cached video ID if prompt was seen before."""
    global video_cache
    
    # Check cache first
    normalized_prompt = _normalize_prompt(response_text)
    if normalized_prompt in video_cache:
        cached_video_id = video_cache[normalized_prompt]
        logger.info(f"Cache hit! Reusing video {cached_video_id} for prompt: {response_text[:50]}...")
        return cached_video_id
    
    # Cache miss - create new job
    job_data = {
        "topic": topic,
        "response_text": response_text,
    }

    lesson_id = str(uuid.uuid4())

    # Navigate to sqora root
    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    manim_jobs_path = os.path.join(BASE_DIR, "manim", "jobs", "incoming")
    os.makedirs(manim_jobs_path, exist_ok=True)

    file_path = os.path.join(manim_jobs_path, f"{lesson_id}.json")

    with open(file_path, "w") as f:
        json.dump(job_data, f)
    
    # Add to cache
    video_cache[normalized_prompt] = lesson_id
    _save_video_cache(video_cache)
    
    logger.info(f"Cache miss. Created new job {lesson_id} for prompt: {response_text[:50]}...")
    return lesson_id

def _append_to_chat_history(role: str, text: str, video_id: str | None = None):
    """Append a message to chat history.
    
    Args:
        role: Either "user" or "assistant"
        text: The message text
        video_id: Optional video ID to attach (for user messages that trigger manim)
    """
    global chat_history

    entry = {
        "role": role,
        "text": text
    }

    if video_id:
        entry["video_id"] = video_id

    chat_history.append(entry)

    try:
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(chat_history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")


# In-memory stores (demo – no database required)
_users_db: dict[str, dict] = {
    # Matches Frontend/src/authConfig.js defaults
    "admin@sqora.com": {
        "name": "Admin",
        "email": "admin@sqora.com",
        "password": "Admin@5410",
        "role": "admin",
    },
}

_admin_config: dict[str, object] = {
    # Matches Frontend/src/store/useAppConfig.js defaults
    "mentorGreeting": (
        "Hi! I am your AI mentor. Tap the mic or open chat to ask anything about your prep."
    ),
    "voiceEnabled": True,
    "highlightedExam": "",
    "showContestsOnHome": True,
    "aiOnlyAnswers": True,
    "flagSensitive": False,
}

# Matches the shape used in Frontend/src/pages/Contests.jsx
_contests_upcoming = [
    {
        "code": "NEET-M1",
        "name": "NEET Mock 1 \u2013 Physics, Chemistry, Biology",
        "start": "Jan/29/2026 20:05 UTC+5.5",
        "length": "03:00",
        "beforeStart": "2 days",
        "beforeReg": "1 day",
    },
    {
        "code": "JEE-M2",
        "name": "JEE Main Mock 2 \u2013 PCM",
        "start": "Feb/02/2026 17:30 UTC+5.5",
        "length": "03:00",
        "beforeStart": "6 days",
        "beforeReg": "5 days",
    },
    {
        "code": "NEET-M2",
        "name": "NEET Mock 2 \u2013 Full syllabus",
        "start": "Feb/05/2026 21:00 UTC+5.5",
        "length": "03:00",
        "beforeStart": "9 days",
        "beforeReg": "8 days",
    },
]

_contests_past = [
    {
        "code": "JEE-M1",
        "name": "JEE Main Mock 1 \u2013 PCM",
        "start": "Jan/26/2026 20:05 UTC+5.5",
        "length": "03:00",
        "participants": "43326",
        "unrated": True,
    },
    {
        "code": "NEET-P1",
        "name": "NEET Previous Year 1",
        "start": "Jan/22/2026 19:30 UTC+5.5",
        "length": "03:00",
        "participants": "28104",
        "unrated": False,
    },
    {
        "code": "JEE-A1",
        "name": "JEE Advanced Mock 1",
        "start": "Jan/18/2026 21:00 UTC+5.5",
        "length": "03:00",
        "participants": "8912",
        "unrated": False,
    },
]


def _make_demo_questions(subjects: list[str], per_subject: int) -> list[dict]:
    """Generate placeholder questions for an exam."""
    questions: list[dict] = []
    for si, subj in enumerate(subjects):
        for qi in range(per_subject):
            q_num = si * per_subject + qi + 1
            questions.append(
                {
                    "number": q_num,
                    "subject": subj,
                    "text": f"[{subj} Q{qi + 1}] Which of the following best describes the concept?",
                    "options": {
                        "A": f"Option A for {subj} question {qi + 1}",
                        "B": f"Option B for {subj} question {qi + 1}",
                        "C": f"Option C for {subj} question {qi + 1}",
                        "D": f"Option D for {subj} question {qi + 1}",
                    },
                    "correct": "A",
                    "scoring": "+4 / -1",
                }
            )
    return questions


_exam_store: dict[str, dict] = {}


def _get_exam(code: str) -> dict:
    """Return (and lazily create) exam data for a given contest code.

    Args:
        code: The contest code, e.g. "NEET-M1" or "JEE-M2".
    """
    if code in _exam_store:
        return _exam_store[code]

    # Matches Frontend/src/pages/Exam.jsx EXAM_CONFIGS
    is_neet = code.upper().startswith("NEET")
    if is_neet:
        config = {
            "subjects": ["Physics", "Chemistry", "Botany", "Zoology"],
            "qPerSubject": 45,
            "totalQ": 180,
        }
    else:
        config = {
            "subjects": ["Physics", "Chemistry", "Mathematics"],
            "qPerSubject": 25,
            "totalQ": 75,
        }

    exam = {
        "code": code,
        "config": config,
        "questions": _make_demo_questions(config["subjects"], config["qPerSubject"]),
    }
    _exam_store[code] = exam
    return exam


# --- Pydantic models for SQORA endpoints ---


class AuthSignup(BaseModel):
    """Signup request body."""

    name: str
    email: str
    password: str


class AuthLogin(BaseModel):
    """Login request body."""

    email: str
    password: str


class ChatRequest(BaseModel):
    """AI chat request body."""

    message: str


class AdminConfigUpdate(BaseModel):
    """Partial update for admin configuration."""

    mentorGreeting: str | None = None
    voiceEnabled: bool | None = None
    highlightedExam: str | None = None
    showContestsOnHome: bool | None = None
    aiOnlyAnswers: bool | None = None
    flagSensitive: bool | None = None


# --- Auth ---


@app.post("/api/auth/signup")
async def api_signup(body: AuthSignup):
    """Register a new user."""
    if body.email in _users_db:
        raise HTTPException(status_code=400, detail="Email already registered.")
    _users_db[body.email] = {
        "name": body.name,
        "email": body.email,
        "password": body.password,
        "role": "user",
    }
    return {"token": "demo-token", "role": "user"}


@app.post("/api/auth/login")
async def api_login(body: AuthLogin):
    """Authenticate a user and return their role."""
    user = _users_db.get(body.email)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"token": "demo-token", "role": user["role"]}


# --- AI Chat ---


@app.post("/api/chat")
async def api_chat(body: ChatRequest):
    """Return an AI mentor response powered by Gemini."""
    global ai_response_cache
    
    if not _gemini_client:
        return {"reply": "AI is not configured. Please set the GEMINI_API_KEY environment variable."}

    # Normalize the user's question for cache lookup
    normalized_question = _normalize_prompt(body.message)
    
    # Check AI response cache first
    if normalized_question in ai_response_cache:
        cached_reply = ai_response_cache[normalized_question]
        logger.info(f"AI response cache hit for: {body.message[:50]}...")
        
        # Still need to create manim job and log to history
        topic = _extract_topic(body.message)
        lesson_id = _create_animation_job(
            response_text=body.message,
            topic=topic
        )
        
        _append_to_chat_history("user", body.message, video_id=lesson_id)
        _append_to_chat_history("assistant", cached_reply)
        
        return {"reply": cached_reply, "video_id": lesson_id}
    
    # Cache miss - generate new response
    logger.info(f"AI response cache miss for: {body.message[:50]}...")
    
    # Extract topic from user's question for manim generation
    topic = _extract_topic(body.message)
    
    # Create manim job based on user's question (parallel with AI response)
    lesson_id = _create_animation_job(
        response_text=body.message,
        topic=topic
    )
    
    # Log user message with video_id attached
    _append_to_chat_history("user", body.message, video_id=lesson_id)

    try:
        response = await asyncio.to_thread(
            _gemini_client.chat.completions.create,
            model="gemini-2.5-flash",
            reasoning_effort="low",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly and knowledgeable JEE/NEET tutor"
                        "Give clear, concise explanations with examples. "
                        "Use simple language suitable for Indian high-school students preparing for competitive exams."
                    ),
                },
                *[
                    {"role": "assistant" if m["role"] == "ai" else m["role"], "content": m["text"]}
                    for m in chat_history[-10:]
                ],
            ],
            temperature=0,
        )
        reply = response.choices[0].message.content
        
        # Save to AI response cache
        ai_response_cache[normalized_question] = reply
        _save_ai_response_cache(ai_response_cache)
        
        # Log AI response (no video_id needed for assistant messages)
        _append_to_chat_history("assistant", reply)
    except Exception as e:
        logger.error("Gemini chat error: %s", e)
        reply = "Sorry, I couldn't process your question right now. Please try again."

    return {"reply": reply, "video_id": lesson_id}


@app.get("/api/chat")
async def api_chat_history():
    """Return the stored chat history."""
    return {"history": chat_history}


# --- Videos (manim rendered) ---

_RENDERED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "manim", "media", "rendered",
)


@app.get("/api/videos/{video_id}/status")
async def api_video_status(video_id: str):
    """Check if a rendered video is ready."""
    path = os.path.join(_RENDERED_DIR, f"{video_id}.mp4")
    ready = os.path.exists(path)
    return {"ready": ready}


@app.get("/api/videos/{video_id}")
async def api_video(video_id: str):
    """Serve a rendered manim video."""
    path = os.path.join(_RENDERED_DIR, f"{video_id}.mp4")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video not found or still rendering.")
    return FileResponse(path, media_type="video/mp4")



# --- Contests ---


@app.get("/api/contests")
async def api_contests():
    """Return upcoming and past contest lists."""
    return {"upcoming": _contests_upcoming, "past": _contests_past}


# --- Exam questions ---


@app.get("/api/exams/{code}")
async def api_exam(code: str):
    """Return exam config and questions for a given contest code.

    Args:
        code: The contest code, e.g. "NEET-M1".
    """
    return _get_exam(code)


# --- Admin config ---


@app.get("/api/admin/config")
async def api_admin_config_get():
    """Return current admin configuration."""
    return _admin_config


@app.put("/api/admin/config")
async def api_admin_config_put(body: AdminConfigUpdate):
    """Update admin configuration (partial update)."""
    for key, value in body.model_dump(exclude_none=True).items():
        _admin_config[key] = value
    return _admin_config


if __name__ == "__main__":
    import sys

    print(f"Run this via:\nfastapi dev {sys.argv[0]}")
    exit(1)
