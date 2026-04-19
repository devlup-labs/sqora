import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _resolve_state_path() -> Path:
    raw = os.getenv("RAG_GUARD_STATE_FILE", "rag_guard_state.json")
    p = Path(raw)
    if p.is_absolute():
        return p
    # Keep the guard state near config.json by default.
    return Path(__file__).parents[2] / raw


def _resolve_alert_path() -> Path:
    raw = os.getenv("RAG_GUARD_ALERT_FILE", "rag_guard_alert.json")
    p = Path(raw)
    if p.is_absolute():
        return p
    return Path(__file__).parents[2] / raw


def _load_state(state_path: Path) -> Optional[Dict[str, Any]]:
    if not state_path.exists():
        return None
    try:
        with open(state_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception as exc:
        logger.warning("RAG guard: failed loading state file %s: %s", state_path, exc)
    return None


def _save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def run_rag_startup_guard() -> Dict[str, Any]:
    """Checks Qdrant collection count and records alerts for suspicious drops."""
    qdrant_url = os.getenv("QDRANT_URL", "http://10.36.16.15:6333")
    qdrant_collection = os.getenv("QDRANT_COLLECTION", "pyqs")
    min_points = _int_env("RAG_GUARD_MIN_POINTS", 50)
    drop_ratio = _float_env("RAG_GUARD_DROP_RATIO", 0.5)

    state_path = _resolve_state_path()
    alert_path = _resolve_alert_path()

    result: Dict[str, Any] = {
        "checked_at": _utc_now_iso(),
        "qdrant_url": qdrant_url,
        "collection": qdrant_collection,
        "status": "ok",
    }

    try:
        client = QdrantClient(url=qdrant_url)
        info = client.get_collection(qdrant_collection)
        current_count = int(getattr(info, "points_count", 0) or 0)
        result["points_count"] = current_count
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)
        logger.error("RAG guard: unable to inspect Qdrant collection '%s': %s", qdrant_collection, exc)
        _save_json(alert_path, result)
        return result

    previous = _load_state(state_path) or {}
    previous_count = previous.get("points_count")
    if isinstance(previous_count, str) and previous_count.isdigit():
        previous_count = int(previous_count)

    alerts = []

    if current_count < min_points:
        alerts.append(
            f"Collection '{qdrant_collection}' is below minimum expected points: "
            f"{current_count} < {min_points}"
        )

    if isinstance(previous_count, int) and previous_count > 0:
        floor = int(previous_count * (1.0 - max(0.0, min(1.0, drop_ratio))))
        if current_count <= floor:
            alerts.append(
                f"Collection '{qdrant_collection}' dropped unexpectedly: "
                f"{previous_count} -> {current_count}"
            )

    if alerts:
        result["status"] = "alert"
        result["alerts"] = alerts
        logger.error("RAG guard alert: %s", " | ".join(alerts))
        _save_json(alert_path, result)
    else:
        logger.info(
            "RAG guard: collection '%s' healthy with %s points",
            qdrant_collection,
            current_count,
        )

    _save_json(
        state_path,
        {
            "checked_at": result["checked_at"],
            "qdrant_url": qdrant_url,
            "collection": qdrant_collection,
            "points_count": current_count,
        },
    )

    return result
