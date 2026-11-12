# AI Media Factory OS

Autonomous multi-brand, multi-studio, multilingual media production platform built on Google Antigravity, FastAPI, React/Vite, LangGraph state machine, Maya3 Indic TTS, and HyperFrames.

## Architecture

* **Backend (`backend/`):**
  * **FastAPI REST API** with SQLite / PostgreSQL persistence.
  * **Maya3 TTS Adapter (`backend/app/adapters/voice/`):** Supports 12 Indic languages natively (Odia `or`, Hindi `hi`, Bengali `bn`, Telugu `te`, Tamil `ta`, etc.).
  * **HyperFrames & Motion Pack (`backend/app/adapters/render/`):** Pure-function-of-time deterministic DOM/canvas scene rendering.
  * **FFmpeg Skill (`backend/app/adapters/render/`):** `probe -> edit -> check -> verify` contract with automated EBU R128 (-14 LUFS) loudness normalization and 9:16 vertical social reframing.
  * **Production Orchestrator (`backend/app/orchestration/`):** Autonomous multi-agent pipeline executing research, scriptwriting, voice synthesis, scene rendering, master assembly, and QA auditing.
  * **Production Economics Engine (`backend/app/services/cost_service.py`):** Real-time tracking of LLM tokens, Maya3 GPU seconds, and rendering compute, keeping total episode production costs under **$0.10 / finished minute**.

* **Frontend (`frontend/`):**
  * Modern React 18 + Vite + TypeScript + Tailwind CSS production studio dashboard.
  * Real-time Studio Switcher (Entertainment, Kids, Education, Podcast, News, Marketing).
  * Recurring Character & Voice Registry.
  * 1-Click Autonomous Episode Production Wizard.
  * Live Agent Execution Monitor & Media Deliverable Inspector (16:9 Landscape & 9:16 Vertical Reel).
  * Itemized Cost Ledger.

* **Agent Skills (`.agents/skills/`):**
  * `odia-comedy-specialist`: Rules for authentic Odia village comedy, cultural nuances, and Maya3 phoneme handling.
  * `kids-content-director`: Pedagogical structure, rhyming metrics, and child safety gates.
  * `media-qa-auditor`: FFprobe container inspection and loudness normalization specs.

## Quickstart

### 1. Run Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Run Tests
```bash
backend\venv\Scripts\pytest backend\tests -v
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
