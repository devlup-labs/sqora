#!/bin/bash
# Colors for easy identification
COLOR="\e[1;36m"
RESET="\e[0m"

echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}          🗣️ POCKET-TTS (TEXT-TO-SPEECH)          ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}Port:     8089${RESET}"
echo -e "${COLOR}Purpose:  Generates AI Audio Voices locally      ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${TTS_PORT:-8089}"

port_is_listening() {
	python - "$1" <<'PY'
import socket
import sys

port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.5)
try:
	sys.exit(0 if sock.connect_ex(("127.0.0.1", port)) == 0 else 1)
finally:
	sock.close()
PY
}

# Change to the project directory relative to the script
cd "$SCRIPT_DIR/Unmute" || exit 1

# Use the shared project virtual environment so the command works on a fresh machine.
source "$SCRIPT_DIR/.venv/bin/activate"

if port_is_listening "$PORT"; then
	echo "Pocket-TTS is already running on port $PORT. Reusing the existing server."
	exit 0
fi

TTS_PORT="$PORT" python unmute/tts/tts_server.py

