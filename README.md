<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-Vision-000000?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-Agent-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Server-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/100%25-FREE-success?style=for-the-badge" />
</p>

<h1 align="center">BrowserPilot</h1>

<p align="center">
  <strong>Fully autonomous browser agent — 100% free, zero API costs.<br/>
  Powered by Ollama (local vision), Playwright, LangChain, and FastAPI.</strong>
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

- **Primary LLM**: Ollama (local, unlimited, no API key)
- **Fallback LLM**: OpenRouter free vision models (no credit card)
- **Browser**: Playwright (open-source)
- **Orchestration**: LangChain (open-source)
- **Server**: FastAPI (open-source)

---

## Technology Stack (100% Free)

| Component | Technology | Cost | Notes |
|-----------|-----------|------|-------|
| **Vision LLM** | Ollama (`gemma3:4b`) | **FREE** | Local, unlimited, ~4GB RAM |
| **Fallback LLM** | OpenRouter (`gemma-3-27b-it:free`) | **FREE** | 20 RPM, 200 RPD, no credit card |
| **Browser** | Playwright v1.58+ | **FREE** | Chromium/Firefox/WebKit |
| **Agent** | LangChain v1.2+ | **FREE** | Tool orchestration |
| **Server** | FastAPI v0.135+ | **FREE** | REST/WebSocket API |
| **Package Mgr** | uv (latest) | **FREE** | Fast Python package manager |

---

## Quick Start

### Prerequisites

1. **Python 3.12+**
2. **[uv](https://docs.astral.sh/uv/)** package manager
3. **[Ollama](https://ollama.ai)** installed and running

### Setup

```bash
# Clone
git clone https://github.com/chirag127/BrowserPilot.git
cd BrowserPilot

# Install Python dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Pull the vision model in Ollama
ollama pull gemma3:4b

# Create .env from template
cp .env.example .env
# No API keys needed for Ollama!
```

### First Run

```bash
# CLI — run a task
uv run browserpilot run "Go to example.com and tell me the page title"

# Start the API server
uv run browserpilot serve --port 8000

# Show config
uv run browserpilot config
```

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
    loop = ActionLoop(provider="ollama")
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
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3:4b` | Vision model name |
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
