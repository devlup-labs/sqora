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

# Change to the project directory relative to the script
cd "$SCRIPT_DIR/Unmute" || exit 1
python unmute/tts/tts_server.py

