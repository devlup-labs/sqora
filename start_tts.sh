#!/bin/bash
# Colors for easy identification
COLOR="\e[1;36m"
RESET="\e[0m"

echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}          🗣️ HEADTTS (TEXT-TO-SPEECH)            ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}Port:     8882${RESET}"
echo -e "${COLOR}Purpose:  Generates AI Audio Voices locally      ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${HEADTTS_PORT:-8882}"
NODE_BIN="${NODE_BIN:-node}"
CONFIG_FILE="${HEADTTS_CONFIG:-$SCRIPT_DIR/headtts-node.json}"

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
cd "$SCRIPT_DIR" || exit 1


if ! command -v "$NODE_BIN" >/dev/null 2>&1; then
	echo "HeadTTS requires Node.js, but '$NODE_BIN' was not found."
	exit 1
fi

if port_is_listening "$PORT"; then
	echo "HeadTTS is already running on port $PORT. Reusing the existing server."
	exit 0
fi

exec "$NODE_BIN" "$SCRIPT_DIR/modules/headtts-node.mjs" --config "$CONFIG_FILE"

