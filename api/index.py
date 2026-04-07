"""
Vercel serverless entry point for the SQORA FastAPI backend.
Vercel calls this file as a Python WSGI/ASGI handler.
"""
import sys
import os
from pathlib import Path

# Make Unmute package importable from the project root
_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT / "Unmute"))

# Load .env so GEMINI_API_KEY etc. are available
from dotenv import load_dotenv
load_dotenv(_ROOT / ".env", override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from unmute.sqora_routes import router

app = FastAPI(title="SQORA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this to your Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Vercel expects a module-level ASGI app named `app`
