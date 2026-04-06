"""
Firebase Admin SDK - Server-side token verification.
Verifies Firebase ID tokens sent by the frontend via Authorization: Bearer <token>.
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_firebase_admin = None
_firebase_auth_module = None

# Path to service account key (never commit this file to git!)
_SERVICE_ACCOUNT_PATH = Path(__file__).parents[1] / "firebase-service-account.json"


def _init_firebase():
    """Lazily initialize Firebase Admin SDK if service account is available."""
    global _firebase_admin, _firebase_auth_module
    if _firebase_admin is not None:
        return True  # already initialized

    if not _SERVICE_ACCOUNT_PATH.exists():
        logger.warning(
            "⚠️  firebase-service-account.json not found. "
            "Token verification is DISABLED (dev mode). "
            "Place the file at %s to enable secure multi-user auth.",
            _SERVICE_ACCOUNT_PATH,
        )
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials, auth

        if not firebase_admin._apps:
            cred = credentials.Certificate(str(_SERVICE_ACCOUNT_PATH))
            firebase_admin.initialize_app(cred)

        _firebase_admin = firebase_admin
        _firebase_auth_module = auth
        logger.info("✅ Firebase Admin SDK initialized — token verification is ACTIVE")
        return True
    except ImportError:
        logger.error(
            "❌ firebase-admin package not installed. "
            "Run: pip install firebase-admin"
        )
        return False
    except Exception as e:
        logger.error(f"❌ Firebase Admin init error: {e}")
        return False


def verify_token(token: str) -> str | None:
    """
    Verify a Firebase ID token and return the uid.
    Returns the unverified uid if SDK is not configured (dev mode).
    """
    if not _init_firebase():
        return _unverified_decode(token)

    try:
        decoded = _firebase_auth_module.verify_id_token(token)
        return decoded.get("uid")
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def _unverified_decode(token: str) -> str | None:
    import base64
    import json
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1]
        padded = payload + "=" * ((4 - len(payload) % 4) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        data = json.loads(decoded)
        return data.get("user_id") or data.get("uid")
    except Exception as e:
        logger.warning(f"Dev fallback token decode failed: {e}")
        return None
