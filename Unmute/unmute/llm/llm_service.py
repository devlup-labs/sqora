import os
import json
import logging
import asyncio
from pathlib import Path

from typing import Any, List, Tuple, Union, Dict, cast
from dotenv import load_dotenv
from google import genai

# Load .env
_ENV_FILE = Path(__file__).parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=True)

logger = logging.getLogger(__name__)


class LLMService:
    _DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.provider = "gemini"
        self.url = None
        self.model = self._DEFAULT_MODEL
        self.api_key = os.getenv("GEMINI_API_KEY")

        # Context compaction settings.
        self.compaction_enabled = True
        self.compaction_max_context_tokens = 7000
        self.compaction_trigger_tokens = 5800
        self.compaction_target_summary_tokens = 1200
        self.compaction_keep_recent_messages = 8
        self.compaction_model = self._DEFAULT_MODEL
        self.compaction_state_path = Path(config_path).with_name("chat_compaction_state.json")

        # Rolling compaction state.
        self._compacted_context = ""
        self._compacted_upto = 0

        self.client = None
        self.load_config()
        self._load_compaction_state()

        if not self.api_key:
            logger.warning("❌ GEMINI_API_KEY not set. LLM will not function.")

        try:
            # ✅ NEW SDK CLIENT
            self.client = genai.Client(api_key=self.api_key)
            logger.info("✅ Gemini initialized (new SDK)")
        except Exception as e:
            logger.error(f"❌ Gemini init error: {e}")
            self.client = None

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    llm_config = config.get("llm", {})
                    self.provider = llm_config.get("provider", self.provider)
                    self.url = llm_config.get("url", self.url)
                    self.model = llm_config.get("model", self.model)

                    compaction = llm_config.get("context_compaction", {})
                    if isinstance(compaction, dict):
                        self.compaction_enabled = bool(
                            compaction.get("enabled", self.compaction_enabled)
                        )
                        self.compaction_max_context_tokens = self._to_int(
                            compaction.get("max_context_tokens"),
                            self.compaction_max_context_tokens,
                            minimum=512,
                        )
                        self.compaction_trigger_tokens = self._to_int(
                            compaction.get("trigger_tokens"),
                            self.compaction_trigger_tokens,
                            minimum=256,
                        )
                        self.compaction_target_summary_tokens = self._to_int(
                            compaction.get("target_summary_tokens"),
                            self.compaction_target_summary_tokens,
                            minimum=64,
                        )
                        self.compaction_keep_recent_messages = self._to_int(
                            compaction.get("keep_recent_messages"),
                            self.compaction_keep_recent_messages,
                            minimum=0,
                        )
                        self.compaction_model = compaction.get(
                            "model", self.compaction_model
                        )

                        state_file = compaction.get("state_file")
                        if isinstance(state_file, str) and state_file.strip():
                            state_path = Path(state_file)
                            if not state_path.is_absolute():
                                state_path = Path(self.config_path).parent / state_path
                            self.compaction_state_path = state_path

                    self.compaction_trigger_tokens = min(
                        self.compaction_trigger_tokens,
                        self.compaction_max_context_tokens,
                    )
            except Exception as e:
                logger.warning(f"Config load failed: {e}")
    def retrieve_context(self, query: str) -> str:
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

    @staticmethod
    def _to_int(value, default: int, minimum: int = 0) -> int:
        try:
            result = int(value)
            return max(result, minimum)
        except (TypeError, ValueError):
            return max(default, minimum)

    @staticmethod
    def _role_for_llm(role: str) -> str:
        # For new SDK: user or model
        return "model" if role == "assistant" else "user"

    @staticmethod
    def _estimate_text_tokens(text: str) -> int:
        # Rough estimate: 1 token ~= 4 chars for English-heavy text.
        return max(1, (len(text) + 3) // 4)

    # pyre-ignore[11]
    def _estimate_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        total = 2
        for message in messages:
            total += 4
            parts = cast(List[Dict[str, Any]], message.get("parts", []))
            if parts and isinstance(parts, list) and len(parts) > 0:
                text = str(parts[0].get("text", ""))
                # pyre-ignore[16]
                total += self._estimate_text_tokens(text)
        return total

    def _load_compaction_state(self):
        if not self.compaction_state_path.exists():
            return

        try:
            with open(self.compaction_state_path, "r") as f:
                data = json.load(f)
            self._compacted_context = str(data.get("summary", ""))
            self._compacted_upto = self._to_int(data.get("compacted_upto"), 0, 0)
        except Exception as e:
            logger.error(f"Failed to load context compaction state: {e}")
            self._compacted_context = ""
            self._compacted_upto = 0

    def _save_compaction_state(self):
        try:
            self.compaction_state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.compaction_state_path, "w") as f:
                json.dump(
                    {
                        "summary": self._compacted_context,
                        "compacted_upto": self._compacted_upto,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"Failed to save context compaction state: {e}")

    def _sync_state_with_history(self, chat_history: List[Any]):
        if self._compacted_upto > len(chat_history):
            logger.info("Chat history appears reset. Clearing compaction state.")
            self._compacted_context = ""
            self._compacted_upto = 0
            self._save_compaction_state()

    def _pending_entries(self, chat_history: List[Any]) -> List[Tuple[int, str, str]]:
        history_len = len(chat_history)
        start = min(max(self._compacted_upto, 0), history_len)
        pending: List[Tuple[int, str, str]] = []

        for idx in range(start, history_len):
            msg = chat_history[idx]
            role = self._role_for_llm(str(msg.get("role", "user")))
            text = str(msg.get("text", "")).strip()
            if not text:
                continue
            pending.append((idx, role, text))

        return pending

    def _context_token_estimate(
        self, pending: list[tuple[int, str, str]], current_user_message: str
    ) -> int:
        messages = [
            {
                "role": "user",
                "parts": [{"text": (
                    "SYSTEM INSTRUCTION: You are a friendly and knowledgeable JEE/NEET tutor. "
                    "Give clear, concise explanations with examples. "
                    "Use simple language suitable for Indian high-school students preparing for competitive exams."
                )}]
            }
        ]
        if self._compacted_context:
            messages.append(
                {
                    "role": "user",
                    "parts": [{"text": (
                        "Compacted conversation memory. Use this as trusted background context:\n"
                        f"{self._compacted_context}"
                    )}]
                }
            )
            messages.append({"role": "model", "parts": [{"text": "Understood. I will use the compacted memory for context."}]})

        for _, role, text in pending:
            messages.append({"role": role, "parts": [{"text": text}]})
        if current_user_message:
            messages.append({"role": "user", "parts": [{"text": current_user_message}]})
        return self._estimate_messages_tokens(messages)

    def _build_compaction_source(self, to_compact: list[tuple[int, str, str]]) -> str:
        lines: list[str] = []
        if self._compacted_context:
            lines.append("Existing compacted context:")
            lines.append(self._compacted_context.strip())
            lines.append("")
        lines.append("Conversation turns to fold into compacted context:")

        for _, role, text in to_compact:
            speaker = "Assistant" if role == "model" else "User"
            lines.append(f"{speaker}: {text}")

        return "\n".join(lines)

    def _fallback_compaction(self, source: str) -> str:
        # Fallback if compaction LLM call fails: keep a bounded tail.
        max_chars = max(256, self.compaction_target_summary_tokens * 4)
        lines = [ln.strip() for ln in source.splitlines() if ln.strip()]
        joined = " | ".join(lines[-80:])
        if len(joined) > max_chars:
            joined = joined[-max_chars:]
        return joined

    def _compact_context_with_llm(self, source: str) -> str:
        if not self.client:
            return self._fallback_compaction(source)

        try:
            if self.client is None:
                 return self._fallback_compaction(source)
                 
            # Use the new SDK for compaction too
            response: Any = self.client.models.generate_content(
                model=self.compaction_model or self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": (
                            "You compress conversation history for another LLM call. "
                            "Return a compact memory that preserves user goals, constraints, decisions, unresolved questions, and key facts. "
                            "Keep it dense and factual. Avoid filler and avoid markdown.\n\n"
                            "Summarize this conversation context into compact memory for future turns. "
                            "Keep important details that matter for continuity and instruction following.\n\n"
                            f"{source}"
                        )}]
                    }
                ],
                config={"temperature": 0, "max_output_tokens": self.compaction_target_summary_tokens}
            )
            summary = str(getattr(response, "text", "")).strip()
            if summary:
                return summary
        except Exception as e:
            logger.warning(f"Context compaction LLM call failed, using fallback: {e}")

        return self._fallback_compaction(source)

    def _compact_pending_entries(
        self,
        pending: list[tuple[int, str, str]],
        keep_recent_messages: int,
    ):
        if not pending:
            return

        keep_recent_messages = max(0, keep_recent_messages)
        if len(pending) <= keep_recent_messages:
            return

        cut = len(pending) - keep_recent_messages
        to_compact = pending[:cut]
        source = self._build_compaction_source(to_compact)
        new_summary = self._compact_context_with_llm(source)
        if not new_summary:
            return

        self._compacted_context = new_summary
        self._compacted_upto = to_compact[-1][0] + 1
        self._save_compaction_state()

    def _maybe_roll_compaction(self, chat_history: list, current_user_message: str):
        if not self.compaction_enabled:
            return

        pending = self._pending_entries(chat_history)
        estimate = self._context_token_estimate(pending, current_user_message)
        if estimate <= self.compaction_trigger_tokens:
            return

        logger.info(
            "Context estimate %s exceeded trigger %s, running compaction.",
            estimate,
            self.compaction_trigger_tokens,
        )
        self._compact_pending_entries(
            pending,
            keep_recent_messages=self.compaction_keep_recent_messages,
        )

        pending_after = self._pending_entries(chat_history)
        estimate_after = self._context_token_estimate(pending_after, current_user_message)
        if estimate_after > self.compaction_max_context_tokens and pending_after:
            logger.info(
                "Context still estimated at %s after first pass, compacting remaining pending context.",
                estimate_after,
            )
            self._compact_pending_entries(pending_after, keep_recent_messages=0)

    def _build_messages(self, message: str, chat_history: list) -> list:
        # Base system instruction
        system_content = (
            "You are a friendly and knowledgeable JEE/NEET tutor. "
            "Give clear, concise explanations with examples. "
            "Use simple language suitable for Indian high-school students preparing for competitive exams."
        )

        if not self.compaction_enabled:
            messages = [
                {"role": "user", "parts": [{"text": system_content}]},
                {"role": "model", "parts": [{"text": "Understood. I will act as your tutor."}]}
            ]
            recent = chat_history[-10:] if len(chat_history) >= 10 else chat_history
            for m in recent:
                role = self._role_for_llm(str(m.get("role", "user")))
                messages.append({"role": role, "parts": [{"text": str(m.get("text", ""))}]})
            context_data = self.retrieve_context(message)
            final_text = message
            if context_data:
                final_text += f"\n\nContext:\n{context_data}"
                
            messages.append({"role": "user", "parts": [{"text": final_text}]})
            return messages

        self._sync_state_with_history(chat_history)
        self._maybe_roll_compaction(chat_history, message)

        messages = [
            {"role": "user", "parts": [{"text": system_content}]},
            {"role": "model", "parts": [{"text": "Understood. I will act as your tutor."}]}
        ]

        if self._compacted_context:
            messages.append(
                {
                    "role": "user",
                    "parts": [{"text": (
                        "Compacted conversation memory. Use this as trusted background context:\n"
                        f"{self._compacted_context}"
                    )}]
                }
            )
            messages.append({"role": "model", "parts": [{"text": "Understood. Memory loaded."}]})

        for _, role, text in self._pending_entries(chat_history):
            messages.append({"role": role, "parts": [{"text": text}]})

        context_data = self.retrieve_context(message)
        final_text = message
        if context_data:
            final_text += f"\n\nContext:\n{context_data}"
            
        messages.append({"role": "user", "parts": [{"text": final_text}]})
        return messages

    async def get_response(self, message: str, chat_history: List[Any]) -> str:
        if self.client is None:
            return "AI is not configured. Please check your API key."
        try:
            # Fix: calling _build_messages which is a method, not a static function
            messages = await asyncio.to_thread(self._build_messages, message, chat_history)
            
            # Using the new SDK
            response: Any = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=messages,
                # config is a dict in the new SDK generate_content
                config={"temperature": 0}
            )
            
            res_text = str(getattr(response, "text", ""))
            if res_text:
                return res_text
            return "No response generated."
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "Sorry, I am having trouble thinking right now. Please try again."

    def stream_response(self, message: str, chat_history: list):
        if not self.client:
            yield "AI is not configured. Please check your API key."
            return
        try:
            messages = self._build_messages(message, chat_history)
            
            # Using the new SDK for streaming
            stream = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config={"temperature": 0},
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"LLM Stream Error: {e}")
            yield "Sorry, I ran into a problem. Please try again."

# Singleton instance
_BASE_DIR = Path(__file__).parents[2]
llm_service = LLMService(str(_BASE_DIR / "config.json"))