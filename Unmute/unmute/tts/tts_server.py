import os
import subprocess

def start_tts():
    port = os.environ.get("TTS_PORT", "8089")
    print(f"Starting Kyutai Pocket-TTS server on port {port}...")
    
    # We use the pocket-tts-env we created earlier to run pocket-tts
    venv_python = os.path.expanduser("~/pocket-tts-env/bin/pocket-tts")
    
    if os.path.exists(venv_python):
        subprocess.run([venv_python, "serve", "--port", port])
    else:
        # Fallback to uvx
        subprocess.run(["uvx", "pocket-tts", "serve", "--port", port])

if __name__ == "__main__":
    start_tts()
