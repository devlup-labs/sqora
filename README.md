# SQORA Platform

Welcome to the SQORA project repository. This application bridges an interactive React frontend with a real-time conversational AI backend, along with a dynamic Manim video generation service for creating educational math and science visualizations on the fly.

## System Architecture

The project consists of three separate interconnected services:

1. **Frontend (React + Vite)**
   - Located at the root of the project (and partially in `/Frontend/`).
   - Uses React, `@react-three/fiber` for 3D elements, `react-markdown` and `katex` for rendering math.
   - Connects to the backend using WebSockets to facilitate an interactive audio-chat interface with AI mentors.

2. **Backend Server (FastAPI - `Unmute/`)**
   - Located in the `/Unmute` directory.
   - Built on FastAPI and handles WebSocket connections for real-time AI conversation (`main_websocket.py`).
   - Receives audio chunks, performs Speech-to-Text (STT), fetches an LLM text response (such as Gemini or general OpenAI-like), applies Text-to-Speech (TTS), and streams the audio back.

3. **Manim Worker (`manim/`)**
   - Located in the `/manim` directory.
   - A standalone Python worker that polls a job queue (e.g., `jobs/incoming/`).
   - Translates AI text responses into Manim Python code using Gemini, dynamically renders `.mp4` video files, and sends them back to the user context.

## Setup & Installation

Both the Backend and Manim worker share a single, unified Python virtual environment. 

### 1. Install Node Dependencies (Frontend)
From the project root (`/home/yash/SQ`):
```bash
npm install
```

### 2. Setup Python Environment (Backend & Manim)
From the project root (`/home/yash/SQ`):
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install all unified dependencies
pip install -r requirements.txt
```

## Running the Application Locally

You will need to open **three separate terminals** to run all services simultaneously.

### Terminal 1: Frontend Server
```bash
cd /home/yash/SQ
npm run dev
```
*(Available at `http://localhost:5173`)*

### Terminal 2: Backend (Websocket AI Engine)
```bash
cd /home/yash/SQ/Unmute
source ../.venv/bin/activate
fastapi dev unmute/main_websocket.py
```
*(Runs the FastAPI app reloading on `127.0.0.1:8000`)*

### Terminal 3: Manim Worker
```bash
cd /home/yash/SQ/manim
source ../.venv/bin/activate
python worker.py
```
*(Starts the renderer worker polling for new scenes to generate)*

## Directory Overview

- `requirements.txt` - Unified Python package requirements for backend and manim.
- `package.json` / `vite.config.js` - Configuration for the React frontend web interface.
- `/Unmute` - Core backend orchestrating STT -> LLM -> TTS pipelines.
- `/manim` - Scripts, caches, and jobs for generating videos programmatically.
- `/src` - The source code of the web page features, components, and pages.
