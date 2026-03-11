#!/bin/bash
# Colors for easy identification
COLOR="\e[1;35m"
RESET="\e[0m"

echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}             🚀 SQORA BACKEND (API)               ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}Port:     8000${RESET}"
echo -e "${COLOR}Purpose:  Handles Chat Interface, Gemini API, DB ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the Unmute backend directory relative to the script
cd "$SCRIPT_DIR/Unmute" || exit 1
fastapi dev unmute/main_websocket.py --port 8000
