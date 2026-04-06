import os
import json
import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator, List, Dict

import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.5-flash"
        self.client = None

        self.load_config()

        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not set")

        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            logger.info("✅ Gemini initialized")
        except Exception as e:
            raise RuntimeError(f"❌ Gemini init failed: {e}")

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                config = json.load(f)
                llm_config = config.get("llm", {})
                self.model_name = llm_config.get("model", self.model_name)

    # --------------------------
    # Message formatting
    # --------------------------
    def _build_prompt(self, message: str, chat_history: List[Dict]) -> str:
        system_prompt = (
            "You are a friendly and knowledgeable JEE/NEET tutor. "
            "Give clear, concise explanations with examples. "
            "Use simple language for Indian students."
        )

        history_text = []
        for m in chat_history[-10:]:
            role = "Assistant" if m["role"] == "assistant" else "User"
            history_text.append(f"{role}: {m['text']}")

        history_text.append(f"User: {message}")

        return system_prompt + "\n\n" + "\n".join(history_text)

    # --------------------------
    # Non-streaming response
    # --------------------------
    async def get_response(self, message: str, chat_history: List[Dict]) -> str:
        if not self.client:
            return "AI not configured."

        prompt = self._build_prompt(message, chat_history)

        try:
            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt
            )

            return response.text or "No response generated."

        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "Something went wrong."

    # --------------------------
    # Streaming response (SYNC generator)
    # --------------------------
    def stream_response(self, message: str, chat_history: List[Dict]):
        if not self.client:
            yield "AI not configured."
            return

        prompt = self._build_prompt(message, chat_history)

        try:
            response = self.client.generate_content(
                prompt,
                stream=True
            )

            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Stream Error: {e}")
            yield "Error occurred."

    # --------------------------
    # Async streaming wrapper (IMPORTANT)
    # --------------------------
    async def async_stream_response(
        self, message: str, chat_history: List[Dict]
    ) -> AsyncIterator[str]:
        loop = asyncio.get_event_loop()

        def generator():
            for chunk in self.stream_response(message, chat_history):
                yield chunk

        for chunk in await loop.run_in_executor(None, lambda: list(generator())):
            yield chunk


# --------------------------
# Singleton instance
# --------------------------
_BASE_DIR = Path(__file__).parents[2]
llm_service = LLMService(str(_BASE_DIR / "config.json"))