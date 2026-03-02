import json
import os
from pathlib import Path

from unmute.websocket_utils import http_to_ws

HEADERS = {"kyutai-api-key": "public_token"}

repo_root = Path(__file__).parents[1]
config_path = repo_root / "config.json"

try:
    with open(config_path, "r") as f:
        _cfg = json.load(f)
except Exception:
    _cfg = {}

def _get_service_url(svc_name, default_protocol, default_ip, default_port):
    svc = _cfg.get(svc_name, {})
    return f"{svc.get('protocol', default_protocol)}://{svc.get('ip', default_ip)}:{svc.get('port', default_port)}"

# The defaults are already ws://, but make the env vars support http:// and https://
STT_SERVER = http_to_ws(os.environ.get("KYUTAI_STT_URL", _get_service_url("stt", "ws", "localhost", 8090)))
TTS_SERVER = http_to_ws(os.environ.get("KYUTAI_TTS_URL", _get_service_url("tts", "ws", "localhost", 8089)))
LLM_SERVER = os.environ.get("KYUTAI_LLM_URL", _get_service_url("llm", "http", "localhost", 8091))
KYUTAI_LLM_MODEL = os.environ.get("KYUTAI_LLM_MODEL")
KYUTAI_LLM_API_KEY = os.environ.get("KYUTAI_LLM_API_KEY")

# If None, a dict-based cache will be used instead of Redis
REDIS_SERVER = os.environ.get("KYUTAI_REDIS_URL")

SPEECH_TO_TEXT_PATH = _cfg.get("stt", {}).get("endpoint", "/api/asr-streaming")
TEXT_TO_SPEECH_PATH = _cfg.get("tts", {}).get("endpoint", "/api/tts_streaming")
LLM_PATH = _cfg.get("llm", {}).get("endpoint", "/v1")



# If None, recordings will not be saved
_recordings_dir = os.environ.get("KYUTAI_RECORDINGS_DIR")
RECORDINGS_DIR = Path(_recordings_dir) if _recordings_dir else None



SAMPLE_RATE = 24000
SAMPLES_PER_FRAME = 1920
FRAME_TIME_SEC = SAMPLES_PER_FRAME / SAMPLE_RATE  # 0.08
# TODO: make it so that we can read this from the ASR server?
STT_DELAY_SEC = 0.5
