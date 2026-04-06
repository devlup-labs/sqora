import os
import json
import logging
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load .env
_ENV_FILE = Path(__file__).parents[4] / ".env"
load_dotenv(dotenv_path=_ENV_FILE)

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.provider = "gemini"
        self.url = None
        self.api_key = os.getenv("GEMINI_API_KEY")

        print("INIT API KEY:", self.api_key)

        self.client = None
        self.load_config()

        if not self.api_key:
            print("❌ API KEY MISSING")

        try:
            # ✅ NEW SDK CLIENT
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini initialized (new SDK)")
        except Exception as e:
            print("❌ Gemini init error:", e)
            self.client = None

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    llm_config = config.get("llm", {})
                    self.provider = llm_config.get("provider", self.provider)
                    self.url = llm_config.get("url", self.url)
            except Exception as e:
                logger.warning(f"Config load failed: {e}")
    def retrive_context(self, query: str) -> str:
        import subprocess
        logger.info(f"Retrieving context from Qdrant for query: {query!r}")
        rag_proxy_path = os.path.join(os.path.dirname(__file__), "rag_proxy.py")
        try:
            process = subprocess.run(
                ["python", rag_proxy_path, query],
                capture_output=True,
                text=True,
                check=False
            )
            if process.returncode == 0:
                context = process.stdout.strip()
                logger.info("Successfully retrieved context by executing rag_proxy.py")
            else:
                logger.error(f"Error executing rag_proxy.py: {process.stderr}")
                context = ""
        except Exception as e:
            logger.error(f"Exception executing rag_proxy.py: {e}")
            context = ""
        return context
    def _build_prompt(self, message: str, chat_history: list) -> str:
        prompt = (
            "You are a friendly JEE/NEET tutor.\n"
            "Explain clearly with simple examples.\n\n"
        )

        for m in chat_history[-10:]:
            role = "User" if m["role"] == "user" else "Assistant"
            prompt += f"{role}: {m['text']}\n"

        prompt += f"User: {message}\nAssistant:"
        context = self.retrive_context(message)
        prompt += f"\n\nContext: {context}"
        return prompt

    async def get_response(self, message: str, chat_history: list) -> str:
        print("🔥 USING GEMINI (NEW SDK)")

        if not self.client:
            return "AI not configured"

        try:
            prompt = await asyncio.to_thread(self._build_prompt, message, chat_history)

            # ✅ NEW SDK CALL
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            print("RAW RESPONSE:", response)

            # ✅ Safe extraction
            if hasattr(response, "text") and response.text:
                return response.text

            return "No response generated."

        except Exception as e:
            import traceback
            print("🔥 GEMINI ERROR:")
            traceback.print_exc()
            return f"Gemini error: {str(e)}"

    async def stream_response(self, message: str, chat_history: list):
        if not self.client:
            yield "AI is not configured."
            return

        try:
            prompt = await self._build_prompt(message, chat_history)

            # ✅ NEW SDK streaming
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                stream=True
            )

            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"LLM Stream Error: {e}")
            yield "Error streaming response"


_BASE_DIR = Path(__file__).parents[2]
llm_service = LLMService(str(_BASE_DIR / "config.json"))