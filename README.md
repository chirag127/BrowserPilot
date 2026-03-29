<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini-Vision-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-Agent-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Server-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/100%25-FREE-success?style=for-the-badge" />
</p>

<h1 align="center">BrowserPilot</h1>

<p align="center">
  <strong>Fully autonomous browser agent — 100% free, zero API costs.<br/>
  Powered by Google Gemini (free vision), Playwright, LangChain, and FastAPI.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-configuration">Config</a> •
  <a href="#-testing">Testing</a>
</p>

---

## What is BrowserPilot?

BrowserPilot is an AI-powered autonomous browser agent that
interprets natural language instructions and executes complex
web tasks. It runs **entirely on free infrastructure**:

- **Primary LLM**: Google Gemini (`gemini-2.0-flash`, free vision, no credit card)
- **Fallback LLM**: OpenRouter free vision models (no credit card)
- **Browser**: Playwright (open-source)
- **Orchestration**: LangChain (open-source)
- **Server**: FastAPI (open-source)

---

## Technology Stack (100% Free)

| Component | Technology | Cost | Notes |
|-----------|-----------|------|-------|
| **Vision LLM (primary)** | Google Gemini (`gemini-2.0-flash`) | **FREE** | Get free API key at aistudio.google.com, no credit card |
| **Fallback LLM** | OpenRouter (`gemma-3-27b-it:free`) | **FREE** | 20 RPM, 200 RPD, no credit card |
| **Browser** | Playwright v1.58+ | **FREE** | Chromium/Firefox/WebKit |
| **Agent** | LangChain v1.2+ | **FREE** | Tool orchestration |
| **Server** | FastAPI v0.135+ | **FREE** | REST/WebSocket API |
| **Package Mgr** | uv (latest) | **FREE** | Fast Python package manager |

---

## Complete Setup Guide

### Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| **Python** | 3.12+ | [python.org](https://www.python.org/downloads/) |
| **uv** | latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| **Git** | any | [git-scm.com](https://git-scm.com/) |

### Step 1 — Clone the Repository

```bash
git clone https://github.com/chirag127/BrowserPilot.git
cd BrowserPilot
```

### Step 2 — Install Dependencies

```bash
# Install Python packages (creates .venv automatically)
uv sync

# Install Playwright browser binaries
uv run playwright install chromium

# On Linux, also install system deps:
# uv run playwright install-deps
```

### Step 3 — Get API Keys

**Google Gemini (primary, free):**

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **Create API Key** → copy it
4. No credit card required

**OpenRouter (fallback, free, optional):**

1. Go to https://openrouter.ai
2. Sign up → go to **Keys** → create a key
3. Free tier: 20 requests/min, 200 requests/day

### Step 4 — Configure Environment

```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` and set your keys:

```env
# Required — paste your Gemini key here
GOOGLE_API_KEY=AIzaSy...your-key-here

# Optional — OpenRouter fallback
OPENROUTER_API_KEY=sk-or-v1-...your-key-here

# Defaults work fine for local dev
GEMINI_MODEL=gemini-2.0-flash
OPENROUTER_MODEL=google/gemma-3-27b-it:free
BROWSER_HEADLESS=true
BROWSER_TYPE=chromium
MAX_STEPS=50
STEP_TIMEOUT=120
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### Step 5 — Verify Installation

```bash
# Check config is loaded correctly
uv run browserpilot config

# Run a simple test task
uv run browserpilot run "Go to example.com and tell me the page title"
```

### Step 6 — Start Using

```bash
# CLI mode
uv run browserpilot run "Go to github.com and find trending repos"

# API server mode
uv run browserpilot serve --port 8000

# Non-headless (see the browser)
uv run browserpilot run "Take a screenshot of google.com" --no-headless
```

### Docker Setup (Alternative)

```bash
# Build
docker build -t browserpilot .

# Run
docker run -p 8000:8000 --env-file .env browserpilot
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: browser_pilot` | Run `uv sync` again |
| Playwright browser not found | Run `uv run playwright install chromium` |
| `GOOGLE_API_KEY not set` | Check `.env` file exists and key is set |
| Port 8000 in use | Change `API_PORT` in `.env` or use `--port` flag |
| Permission errors on Linux | Run `uv run playwright install-deps` |

---

## Usage

### CLI Mode

```bash
# Simple navigation
uv run browserpilot run "Go to github.com and find trending repos"

# Form filling
uv run browserpilot run "Go to example.com/contact, fill name: John"

# Data extraction
uv run browserpilot run "Get top 10 posts from news.ycombinator.com"

# Use Gemini (default)
uv run browserpilot run "Search for AI news" --provider gemini

# Use OpenRouter fallback
uv run browserpilot run "Search for AI news" --provider openrouter

# Show browser (not headless)
uv run browserpilot run "Take a screenshot of google.com" --no-headless
```

### API Mode

```bash
# Start server
uv run browserpilot serve --host 0.0.0.0 --port 8000

# Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Go to example.com"}'

# Check task status
curl http://localhost:8000/api/v1/tasks/{task_id}

# Health check
curl http://localhost:8000/api/v1/health
```

### Python SDK

```python
import asyncio
from browser_pilot.agent.action_loop import ActionLoop
from browser_pilot.models.task import Task

async def main():
    task = Task(instruction="Go to example.com and get the title")
    loop = ActionLoop(provider="gemini")
    result = await loop.run(task)

    print(f"Success: {result.success}")
    print(f"Steps: {result.total_steps}")
    print(f"Time: {result.total_time:.1f}s")

asyncio.run(main())
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/tasks` | Create a new task |
| `GET` | `/api/v1/tasks/{id}` | Get task status & result |
| `GET` | `/api/v1/tasks` | List all tasks (paginated) |
| `DELETE` | `/api/v1/tasks/{id}` | Cancel a running task |
| `GET` | `/api/v1/health` | Health check |

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | _(empty)_ | Free Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Vision model name |
| `OPENROUTER_API_KEY` | _(empty)_ | OpenRouter key (free) |
| `OPENROUTER_MODEL` | `google/gemma-3-27b-it:free` | Fallback model |
| `BROWSER_HEADLESS` | `true` | Run browser headlessly |
| `BROWSER_TYPE` | `chromium` | Browser engine |
| `MAX_STEPS` | `50` | Max steps per sub-task |
| `STEP_TIMEOUT` | `120` | Seconds per step |
| `API_HOST` | `0.0.0.0` | Server host |
| `API_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## How It Works

### The Observe-Decide-Act Loop

1. **OBSERVE** — Take screenshot + extract interactive DOM elements
2. **ANNOTATE** — Overlay numbered bounding boxes (Set-of-Marks)
3. **DECIDE** — Send annotated image to vision LLM for action decision
4. **GROUND** — Verify proposed action against live DOM (anti-hallucination)
5. **ACT** — Execute the action via Playwright
6. **VALIDATE** — Critic sub-agent checks if sub-task is complete

### Anti-Hallucination Grounding

Every proposed action is verified against 5 checks:
1. Element exists in DOM
2. Element is visible
3. Element is interactive
4. Bounding box position matches
5. Page state hasn't changed

If any check fails, the action is rejected and the agent re-observes.

---

## Testing

```bash
# All tests
uv run pytest -v

# Unit tests
uv run pytest tests/unit/ -v

# Integration tests
uv run pytest tests/integration/ -v

# With coverage
uv run pytest --cov=browser_pilot --cov-report=html

# Lint
uv run ruff check .
uv run ruff format --check .
```

---

## Project Structure

```
BrowserPilot/
├── src/browser_pilot/
│   ├── agent/              # Core agent logic
│   │   ├── action_loop.py  # Observe-decide-act loop
│   │   ├── planner.py      # Task decomposition
│   │   ├── critic.py       # Completion validation
│   │   ├── memory.py       # Context management
│   │   └── state.py        # State machine
│   ├── vision/             # Vision pipeline
│   │   ├── screenshot.py   # Screenshot capture
│   │   ├── annotator.py    # DOM overlay (SoM)
│   │   ├── interpreter.py  # LLM vision analysis
│   │   └── grounding.py    # Anti-hallucination
│   ├── browser/            # Playwright automation
│   │   ├── controller.py   # Browser lifecycle
│   │   ├── dom_inspector.py# DOM extraction
│   │   ├── actions.py      # Click/type/scroll
│   │   └── anti_detection.py
│   ├── server/             # FastAPI server
│   ├── tools/              # LangChain tools
│   ├── models/             # Data models
│   └── utils/              # Utilities
├── tests/                  # Test suites
├── pyproject.toml          # Dependencies
└── README.md
```

---

## CI/CD

GitHub Actions runs on every push:
- **Lint**: `ruff check` + `ruff format --check`
- **Unit Tests**: `pytest tests/unit/`
- **Integration Tests**: `pytest tests/integration/`
- **E2E Tests**: `pytest tests/e2e/`
- **Build**: `uv build`

All test jobs use `continue-on-error: true`.

---

## License

MIT License. See [LICENSE](LICENSE).

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/chirag127">Chirag Singhal</a>
</p>
