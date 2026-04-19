import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from unmute.sqora_routes import router as sqora_router
from unmute.llm.rag_guard import run_rag_startup_guard
from dotenv import load_dotenv
import os

# .env lives two levels up: /home/raid/sqora/.env
_ENV_FILE = Path(__file__).parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_FILE)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")




logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Initialize the main API Backend
app = FastAPI(title="SQORA Backend Interface")

# Allow CORS for local development and Vercel production
CORS_ALLOW_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://sqora.vercel.app",
    "https://sqora-devlups.web.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main AI chat, auth, and database routing logic
app.include_router(sqora_router)


@app.on_event("startup")
async def startup_rag_guard_check():
    # Run a lightweight safety check and write alert file if vector count drops.
    try:
        guard_result = run_rag_startup_guard()
        if guard_result.get("status") == "alert":
            logger.error("RAG startup guard alert: %s", guard_result)
        elif guard_result.get("status") == "error":
            logger.error("RAG startup guard error: %s", guard_result)
        else:
            logger.info("RAG startup guard ok: %s", guard_result)
    except Exception as exc:
        logger.error("RAG startup guard crashed: %s", exc)

@app.get("/")
def root():
    return {"message": "You've reached the Unmute backend server."}

if __name__ == "__main__":
    import sys
    print(f"Run this via:\nfastapi dev {sys.argv[0]}")
    exit(1)
