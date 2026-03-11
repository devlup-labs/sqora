import os
import subprocess

def start_tts():
    print("Starting Kyutai Pocket-TTS server on port 8089...")
    
    # We use the pocket-tts-env we created earlier to run pocket-tts
    venv_python = os.path.expanduser("~/pocket-tts-env/bin/pocket-tts")
    
    if os.path.exists(venv_python):
        subprocess.run([venv_python, "serve", "--port", "8089"])
    else:
        # Fallback to uvx
        subprocess.run(["uvx", "pocket-tts", "serve", "--port", "8089"])

if __name__ == "__main__":
    start_tts()
