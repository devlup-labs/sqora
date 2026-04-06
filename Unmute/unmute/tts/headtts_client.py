import asyncio
import heapq
import json
import numpy as np
import re
from dataclasses import dataclass, field
from logging import getLogger
from typing import Annotated, Any, AsyncIterator, Callable, Literal, Union, cast

import websockets
from pydantic import BaseModel, Field, TypeAdapter

from unmute import metrics as mt
from unmute.kyutai_constants import (
    FRAME_TIME_SEC,
    SAMPLE_RATE,
)
from unmute.service_discovery import ServiceWithStartup
from unmute.timer import Stopwatch
from unmute.websocket_utils import WebsocketState

from unmute.tts.text_to_speech import (
    TTSClientMessage,
    TTSClientTextMessage,
    TTSClientVoiceMessage,
    TTSClientEosMessage,
    TTSTextMessage,
    TTSAudioMessage,
    TTSErrorMessage,
    TTSReadyMessage,
    TTSMessage,
    TTSMessageAdapter,
    prepare_text_for_tts,
    RealtimeQueue,
    AUDIO_BUFFER_SEC,
)

logger = getLogger(__name__)

# Default HeadTTS configuration
HEADTTS_SERVER = "ws://127.0.0.1:8882"

class HeadTTSClient(ServiceWithStartup):
    def __init__(
        self,
        tts_instance: str = HEADTTS_SERVER,
        get_time: Callable[[], float] | None = None,
        voice: str | None = None,
    ):
        self.tts_instance = tts_instance
        self.websocket: websockets.ClientConnection | None = None

        self.time_since_first_text_sent = Stopwatch(autostart=False)
        self.waiting_first_audio: bool = True
        
        self.received_samples = 0
        self.received_samples_yielded = 0

        self.voice = voice or "af_bella"
        
        self.text_output_queue = RealtimeQueue(get_time=get_time)
        self.shutdown_lock = asyncio.Lock()
        self.shutdown_complete = asyncio.Event()
        
        self.msg_id_counter = 0
        
        # Buffer for forming complete sentences
        self.text_buffer = ""
        # Punctuation to split sentences
        self.sentence_end_pattern = re.compile(r'([.!?])\s+')

    def state(self) -> WebsocketState:
        if not self.websocket:
            return "not_created"
        else:
            d: dict[websockets.protocol.State, WebsocketState] = {
                websockets.protocol.State.CONNECTING: "connecting",
                websockets.protocol.State.OPEN: "connected",
                websockets.protocol.State.CLOSING: "closing",
                websockets.protocol.State.CLOSED: "closed",
            }
            return d[self.websocket.state]

    async def _send_json(self, payload: dict):
        if self.websocket:
            await self.websocket.send(json.dumps(payload))

    async def send(self, message: str | TTSClientMessage) -> None:
        """Send a message to the TTS server."""
        if isinstance(message, str):
            message = TTSClientTextMessage(
                type="Text", text=prepare_text_for_tts(message)
            )

        if self.shutdown_lock.locked():
            logger.warning("Can't send - TTS shutting down")
            return
        if not self.websocket:
            logger.warning("Can't send - TTS websocket not connected")
            return

        if isinstance(message, TTSClientTextMessage):
            if not message.text:
                return
            
            # Add to buffer and check for complete sentences
            self.text_buffer += message.text + " "
            
            match = self.sentence_end_pattern.search(self.text_buffer)
            if match:
                end_idx = match.end()
                sentence = self.text_buffer[:end_idx].strip()
                self.text_buffer = self.text_buffer[end_idx:]
                
                await self._synthesize_text(sentence)

        elif isinstance(message, TTSClientEosMessage):
            # Flush whatever is left in the buffer
            remaining = self.text_buffer.strip()
            if remaining:
                await self._synthesize_text(remaining)
                self.text_buffer = ""

    async def _synthesize_text(self, text: str):
        mt.TTS_SENT_FRAMES.inc()
        self.time_since_first_text_sent.start_if_not_started()
        
        self.msg_id_counter += 1
        req = {
            "type": "synthesize",
            "id": self.msg_id_counter,
            "data": {"input": text}
        }
        await self._send_json(req)

    async def start_up(self):
        logger.info(f"Connecting to HeadTTS: {self.tts_instance}")
        self.websocket = await websockets.connect(self.tts_instance)
        logger.debug("Connected to HeadTTS")

        try:
            # Send setup configuration
            self.msg_id_counter += 1
            setup_req = {
                "type": "setup",
                "id": self.msg_id_counter,
                "data": {
                    "voice": self.voice,
                    "language": "en-us",
                    "speed": 1,
                    "audioEncoding": "pcm" # Request raw PCM data
                }
            }
            await self._send_json(setup_req)
        except Exception as e:
            logger.error(f"Error during HeadTTS startup: {repr(e)}")
            await self.websocket.close()
            self.websocket = None
            raise

    async def shutdown(self):
        async with self.shutdown_lock:
            if self.shutdown_complete.is_set():
                return
            mt.TTS_ACTIVE_SESSIONS.dec()
            mt.TTS_AUDIO_DURATION.observe(self.received_samples / SAMPLE_RATE)
            if self.time_since_first_text_sent.started:
                mt.TTS_GEN_DURATION.observe(self.time_since_first_text_sent.time())

            self.shutdown_complete.set()

            if self.websocket:
                await self.websocket.close()
                self.websocket = None

            logger.info("HeadTTS shutdown() finished")

    def _convert_pcm16_to_float32(self, pcm_bytes: bytes) -> list[float]:
        # HeadTTS returns 24kHz PCM 16bit LE
        # But we need to make sure the stream output sample rate matches Unmute (typically 24k)
        int16_array = np.frombuffer(pcm_bytes, dtype=np.int16)
        float32_array = int16_array.astype(np.float32) / 32768.0
        return float32_array.tolist()

    async def __aiter__(self) -> AsyncIterator[TTSMessage]:
        if self.websocket is None:
            raise RuntimeError("TTS websocket not connected")
        mt.TTS_SESSIONS.inc()
        mt.TTS_ACTIVE_SESSIONS.inc()

        output_queue: RealtimeQueue[TTSMessage] = RealtimeQueue()
        current_audio_metadata = None

        try:
            async for message_data in self.websocket:
                if isinstance(message_data, bytes):
                    # It's an ArrayBuffer of PCM audio matching the last 'audio' metadata message
                    if current_audio_metadata:
                        pcm_floats = self._convert_pcm16_to_float32(message_data)
                        audio_msg = TTSAudioMessage(type="Audio", pcm=pcm_floats)
                        
                        mt.TTS_RECV_FRAMES.inc()
                        if self.waiting_first_audio and self.time_since_first_text_sent.started:
                            self.waiting_first_audio = False
                            ttft = self.time_since_first_text_sent.time()
                            mt.TTS_TTFT.observe(ttft)
                            logger.info("Time to first token is %.1f ms", ttft * 1000)
                            
                        # Queue audio
                        output_queue.start_if_not_started()
                        output_queue.put(audio_msg, self.received_samples / SAMPLE_RATE - AUDIO_BUFFER_SEC)
                        self.received_samples += len(pcm_floats)
                        
                        # We also queue the text words based on wtimes we got in metadata
                        words = current_audio_metadata.get("words", [])
                        wtimes = current_audio_metadata.get("wtimes", [])
                        wdurations = current_audio_metadata.get("wdurations", [])
                        
                        for i in range(len(words)):
                            w_start_s = wtimes[i] / 1000.0
                            w_dur_s = wdurations[i] / 1000.0
                            word_msg = TTSTextMessage(
                                type="Text",
                                text=words[i],
                                start_s=w_start_s,
                                stop_s=w_start_s + w_dur_s
                            )
                            output_queue.put(word_msg, w_start_s)
                            mt.TTS_RECV_WORDS.inc()

                        current_audio_metadata = None
                else:
                    # It's a JSON string
                    msg_obj = json.loads(message_data)
                    msg_type = msg_obj.get("type")
                    
                    if msg_type == "audio":
                        # Contains metadata for text/visemes, and indicates binary chunk is coming next
                        current_audio_metadata = msg_obj.get("data", {})
                    elif msg_type == "error":
                        err_str = msg_obj.get("data", {}).get("error", "Unknown error")
                        logger.error(f"HeadTTS Error: {err_str}")
                        raise RuntimeError(f"HeadTTS returned error: {err_str}")

                for _, message in output_queue.get_nowait():
                    if isinstance(message, TTSAudioMessage):
                        self.received_samples_yielded += len(message.pcm)
                    yield message

        except websockets.ConnectionClosedOK:
            pass
        except websockets.ConnectionClosedError:
            if not self.shutdown_complete.is_set():
                raise

        async for _, message in output_queue:
            if self.shutdown_complete.is_set():
                break
            if isinstance(message, TTSAudioMessage):
                self.received_samples_yielded += len(message.pcm)
            yield message

        logger.debug("HeadTTS __aiter__() finished")
        await self.shutdown()
