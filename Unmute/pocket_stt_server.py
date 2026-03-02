import os
import io
import json
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.expanduser("~/voice_commander/model")
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Vosk STT Model not found at {MODEL_PATH}")

print("Loading Vosk Model... this may take a few seconds.")
# Model is preloaded for ultra-fast text recognition
model = Model(MODEL_PATH)
print("Model loaded successfully!")

@app.post("/stt")
async def process_stt(audio: UploadFile = File(...)):
    try:
        content = await audio.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(content))
        
        # Vosk strictly requires mono, 16kHz, 16-bit PCM configuration
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_frame_rate(16000)
        
        pcm_data = audio_segment.raw_data
        recognizer = KaldiRecognizer(model, 16000)
        
        # Send raw chunks into the recognizer
        chunk_size = 4000
        for i in range(0, len(pcm_data), chunk_size):
            recognizer.AcceptWaveform(pcm_data[i:i+chunk_size])
            
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "")
        print(f"[STT API] Transcribed text: {text}")
        
        return JSONResponse(content={"text": text})
    except Exception as e:
        print(f"Error processing audio: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
