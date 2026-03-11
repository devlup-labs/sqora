#!/bin/bash
# Colors for easy identification
COLOR="\e[1;33m"
RESET="\e[0m"

echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}         🎬 MANIM VIDEO WORKER (ANIMATION)        ${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo -e "${COLOR}Purpose: Generates Mathematical Animations locally${RESET}"
echo -e "${COLOR}=================================================${RESET}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the manim directory relative to the script
cd "$SCRIPT_DIR/manim" || exit 1

# Activate the main venv which should have manim/requirements.txt installed
source "$SCRIPT_DIR/.venv/bin/activate"
python worker.py
