import os
import json
import logging
from pathlib import Path
from openai import OpenAI
import asyncio

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.provider = "gemini"
        self.url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        self.load_config()
        self.init_client()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                config = json.load(f)
                llm_config = config.get("llm", {})
                self.provider = llm_config.get("provider", self.provider)
                self.url = llm_config.get("url", self.url)

    def init_client(self):
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.url,
            )
        else:
            logger.warning("GEMINI_API_KEY not set. LLM will not function.")

    def _build_messages(self, message: str, chat_history: list) -> list:
        messages = [
            {"role": "system", "content": (
                "You are a friendly and knowledgeable JEE/NEET tutor. "
                "Give clear, concise explanations with examples. "
                "Use simple language suitable for Indian high-school students preparing for competitive exams."
            )}
        ]
        for m in chat_history[-10:]:
            role = "assistant" if m["role"] == "assistant" else "user"
            messages.append({"role": role, "content": m["text"]})
        messages.append({"role": "user", "content": message})
        return messages

    async def get_response(self, message: str, chat_history: list) -> str:
        """Non-streaming: returns the full reply as a string."""
        if not self.client:
            return "AI is not configured. Please check your API key."
        try:
            messages = self._build_messages(message, chat_history)
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gemini-2.5-flash",
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "Sorry, I am having trouble thinking right now. Please try again."

    def stream_response(self, message: str, chat_history: list):
        """Streaming: yields text delta strings as they arrive from the model."""
        if not self.client:
            yield "AI is not configured. Please check your API key."
            return
        try:
            messages = self._build_messages(message, chat_history)
            stream = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=messages,
                temperature=0,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"LLM Stream Error: {e}")
            yield "Sorry, I ran into a problem. Please try again."

# Singleton instance
_BASE_DIR = Path(__file__).parents[2]
llm_service = LLMService(str(_BASE_DIR / "config.json"))
