# BrowserPilot — Autonomous Browser Agent: Implementation Plan

> **Goal**: Build a production-grade, fully autonomous browser agent that
> accepts plain-English instructions and executes multi-step web tasks
> using GPT-4o vision, Playwright, LangChain, and FastAPI.

---

## User Review Required

> [!IMPORTANT]
> **OpenAI API Key**: The project requires an `OPENAI_API_KEY` with
> GPT-4o (vision) access. Confirm you have one before proceeding.

> [!IMPORTANT]
> **Python Version**: Targeting Python 3.12+. Confirm your local
> Python version meets this requirement.

> [!WARNING]
> **Cost Implications**: GPT-4o vision calls are billed per image
> token. Each screenshot-based step will incur API costs. Consider
> adding budget caps and rate limiting.

> [!CAUTION]
> **Security**: The agent will control a real browser. Implement
> sandboxing, URL allowlists, and action guardrails to prevent
> misuse. Never run in production without proper isolation.

---

## 1. Project Overview

BrowserPilot is an AI agent that autonomously controls a web browser
to complete tasks described in natural language. It combines:

- **GPT-4o Vision** — Multimodal LLM for screenshot interpretation
  and DOM-grounded action decisions
- **Playwright** — Cross-browser automation (Chromium/Firefox/WebKit)
- **LangChain** — Agent orchestration, tool management, memory
- **FastAPI** — REST/WebSocket API server for external integrations
- **browser-use** — Open-source agentic browser framework as the
  core engine

```mermaid
graph TB
    subgraph User["👤 User Layer"]
        CLI["CLI Interface"]
        API["REST API Client"]
        WS["WebSocket Client"]
        WEB["Web Dashboard"]
    end

    subgraph Server["🖥️ FastAPI Server"]
        REST["REST Endpoints"]
        WSS["WebSocket Handler"]
        SSE["SSE Stream"]
        AUTH["Auth Middleware"]
        RATE["Rate Limiter"]
    end

    subgraph Core["🧠 Agent Core"]
        PLANNER["Task Planner"]
        DECOMP["Task Decomposer"]
        LOOP["Action Loop"]
        CRITIC["Critic Sub-Agent"]
        MEMORY["Agent Memory"]
    end

    subgraph Vision["👁️ Vision Pipeline"]
        SCREEN["Screenshot Capture"]
        ANNOTATE["DOM Annotator"]
        VLM["GPT-4o Vision"]
        PARSE["Action Parser"]
    end

    subgraph Browser["🌐 Browser Layer"]
        PW["Playwright Controller"]
        DOM["DOM Inspector"]
        ACTIONS["Action Executor"]
        ANTI["Anti-Detection"]
    end

    subgraph Data["💾 Data Layer"]
        STATE["State Manager"]
        HISTORY["Execution History"]
        EXPORT["Data Exporter"]
        ARTIFACTS["Artifact Store"]
    end

    CLI --> REST
    API --> REST
    WS --> WSS
    WEB --> REST
    WEB --> WSS

    REST --> AUTH --> RATE --> PLANNER
    WSS --> AUTH
    SSE --> AUTH

    PLANNER --> DECOMP --> LOOP
    LOOP --> CRITIC
    CRITIC --> LOOP
    LOOP --> MEMORY

    LOOP --> SCREEN --> ANNOTATE --> VLM --> PARSE --> LOOP

    PARSE --> PW
    PW --> DOM
    PW --> ACTIONS
    PW --> ANTI

    LOOP --> STATE
    STATE --> HISTORY
    STATE --> EXPORT
    STATE --> ARTIFACTS

    style User fill:#1a1a2e,stroke:#e94560,color:#fff
    style Server fill:#16213e,stroke:#0f3460,color:#fff
    style Core fill:#0f3460,stroke:#533483,color:#fff
    style Vision fill:#533483,stroke:#e94560,color:#fff
    style Browser fill:#1a1a2e,stroke:#0f3460,color:#fff
    style Data fill:#16213e,stroke:#533483,color:#fff
```

---

## 2. Technology Stack & Versions

| Technology      | Version  | Purpose                              |
|-----------------|----------|--------------------------------------|
| Python          | 3.12+    | Runtime                              |
| browser-use     | ^1.0     | Core agentic browser framework       |
| Playwright      | ^1.51    | Browser automation engine            |
| LangChain       | ^0.3     | LLM orchestration & agent tools      |
| langchain-openai| ^0.3     | OpenAI GPT-4o integration            |
| FastAPI         | ^0.128   | REST/WebSocket API server            |
| Uvicorn         | ^0.34    | ASGI server                          |
| Pydantic        | ^2.10    | Data validation & settings           |
| openai          | ^1.60    | Direct OpenAI API (fallback)         |
| Pillow          | ^11.1    | Image processing for screenshots     |
| aiohttp         | ^3.11    | Async HTTP client                    |
| structlog       | ^24.4    | Structured logging                   |
| python-dotenv   | ^1.0     | Environment variable management      |
| pytest          | ^8.3     | Unit & integration testing           |
| pytest-asyncio  | ^0.24    | Async test support                   |
| pytest-playwright| ^0.6    | Playwright test fixtures             |
| ruff            | ^0.9     | Linter & formatter                   |
| uv              | latest   | Package manager                      |

---

## 3. Repository Structure

```
BrowserPilot/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI pipeline
│       └── release.yml             # Release workflow
├── src/
│   └── browser_pilot/
│       ├── __init__.py
│       ├── __main__.py             # CLI entry point
│       ├── config.py               # Pydantic settings
│       ├── logging.py              # Structured logging setup
│       │
│       ├── agent/                  # Core agent logic
│       │   ├── __init__.py
│       │   ├── action_loop.py      # Main observe-decide-act loop
│       │   ├── planner.py          # Task decomposition planner
│       │   ├── critic.py           # Critic sub-agent
│       │   ├── memory.py           # Agent memory / context
│       │   ├── prompts.py          # System prompts & templates
│       │   └── state.py            # Agent state machine
│       │
│       ├── vision/                 # Vision pipeline
│       │   ├── __init__.py
│       │   ├── screenshot.py       # Screenshot capture & crop
│       │   ├── annotator.py        # DOM element annotation
│       │   ├── interpreter.py      # GPT-4o vision analysis
│       │   └── grounding.py        # DOM grounding & verify
│       │
│       ├── browser/                # Browser automation
│       │   ├── __init__.py
│       │   ├── controller.py       # Playwright lifecycle
│       │   ├── dom_inspector.py    # DOM tree extraction
│       │   ├── actions.py          # Click, type, scroll, nav
│       │   ├── anti_detection.py   # Stealth & anti-bot
│       │   └── profiles.py         # Browser profile manager
│       │
│       ├── server/                 # FastAPI server
│       │   ├── __init__.py
│       │   ├── app.py              # FastAPI application
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── tasks.py        # Task CRUD endpoints
│       │   │   ├── health.py       # Health check
│       │   │   ├── stream.py       # SSE streaming
│       │   │   └── websocket.py    # WebSocket handler
│       │   ├── middleware.py       # Auth, CORS, rate limit
│       │   ├── schemas.py          # Request/response models
│       │   └── dependencies.py     # FastAPI dependencies
│       │
│       ├── tools/                  # LangChain tools
│       │   ├── __init__.py
│       │   ├── browser_tools.py    # Browser action tools
│       │   ├── extraction_tools.py # Data extraction tools
│       │   ├── navigation_tools.py # Navigation tools
│       │   └── form_tools.py       # Form interaction tools
│       │
│       ├── models/                 # Data models
│       │   ├── __init__.py
│       │   ├── task.py             # Task & sub-task models
│       │   ├── action.py           # Action models
│       │   ├── result.py           # Execution result models
│       │   └── dom.py              # DOM element models
│       │
│       └── utils/                  # Utilities
│           ├── __init__.py
│           ├── image.py            # Image processing utils
│           ├── retry.py            # Retry logic
│           ├── rate_limiter.py     # API rate limiter
│           └── sanitizer.py        # Input sanitization
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_planner.py
│   │   ├── test_critic.py
│   │   ├── test_action_loop.py
│   │   ├── test_screenshot.py
│   │   ├── test_annotator.py
│   │   ├── test_dom_inspector.py
│   │   ├── test_actions.py
│   │   ├── test_grounding.py
│   │   ├── test_state.py
│   │   ├── test_memory.py
│   │   └── test_sanitizer.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_vision_pipeline.py
│   │   ├── test_agent_e2e.py
│   │   ├── test_browser_actions.py
│   │   └── test_api_server.py
│   └── e2e/
│       ├── __init__.py
│       ├── test_form_filling.py
│       ├── test_navigation.py
│       ├── test_data_extraction.py
│       └── test_complex_tasks.py
│
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   ├── development.md
│   └── examples.md
│
├── examples/
│   ├── search_and_extract.py
│   ├── fill_form.py
│   ├── multi_step_research.py
│   └── screenshot_analysis.py
│
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
├── LICENSE
└── README.md
```

---

## 4. Proposed Changes — Phase-by-Phase

### Phase 1: Project Foundation

#### [NEW] pyproject.toml
- Project metadata, dependencies, dev dependencies
- Ruff configuration (line-length=80, Python 3.12)
- pytest configuration
- Build system (hatchling)

#### [NEW] .env.example
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
BROWSER_HEADLESS=true
BROWSER_TYPE=chromium
MAX_STEPS=50
STEP_TIMEOUT=120
MAX_FAILURES=5
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-api-key-here
LOG_LEVEL=INFO
SCREENSHOT_DIR=./screenshots
RECORDING_DIR=./recordings
```

#### [NEW] .gitignore
- Standard Python ignores + .env, screenshots/,
  recordings/, *.pyc, __pycache__, .venv/

#### [NEW] .python-version
```
3.12
```

---

### Phase 2: Configuration & Logging

```mermaid
classDiagram
    class Settings {
        +str openai_api_key
        +str openai_model
        +bool browser_headless
        +str browser_type
        +int max_steps
        +int step_timeout
        +int max_failures
        +str api_host
        +int api_port
        +str api_key
        +str log_level
        +Path screenshot_dir
        +Path recording_dir
        +get_llm() ChatOpenAI
        +get_browser_config() BrowserConfig
    }

    class LogConfig {
        +str level
        +bool json_output
        +bool colorize
        +configure() void
    }

    Settings --> LogConfig
```

#### [NEW] src/browser_pilot/config.py
- Pydantic `BaseSettings` with `.env` file support
- Validated fields for all environment variables
- Factory methods: `get_llm()`, `get_browser_config()`
- Singleton pattern via `@lru_cache`

#### [NEW] src/browser_pilot/logging.py
- Structlog configuration with JSON & console renderers
- Correlation ID injection for request tracing
- Performance timing context manager

---

### Phase 3: Data Models

```mermaid
classDiagram
    class Task {
        +str id
        +str instruction
        +TaskStatus status
        +list~SubTask~ sub_tasks
        +datetime created_at
        +datetime updated_at
        +TaskResult result
    }

    class SubTask {
        +str id
        +str description
        +int order
        +SubTaskStatus status
        +list~Action~ actions
        +str parent_task_id
    }

    class Action {
        +str id
        +ActionType action_type
        +dict params
        +ActionStatus status
        +str screenshot_before
        +str screenshot_after
        +str dom_state_before
        +str dom_state_after
        +float confidence
        +str reasoning
    }

    class DOMElement {
        +int index
        +str tag
        +str text
        +dict attributes
        +BoundingBox bbox
        +bool is_interactive
        +bool is_visible
    }

    class BoundingBox {
        +float x
        +float y
        +float width
        +float height
    }

    class TaskResult {
        +bool success
        +str summary
        +dict extracted_data
        +list~str~ screenshots
        +float total_time
        +int total_steps
        +list~str~ errors
    }

    class ActionType {
        <<enumeration>>
        CLICK
        TYPE
        SCROLL
        NAVIGATE
        SELECT
        HOVER
        WAIT
        SCREENSHOT
        EXTRACT
        GO_BACK
    }

    class TaskStatus {
        <<enumeration>>
        PENDING
        PLANNING
        EXECUTING
        VALIDATING
        COMPLETED
        FAILED
        CANCELLED
    }

    Task "1" --> "*" SubTask
    SubTask "1" --> "*" Action
    Action --> ActionType
    Action --> DOMElement
    Task --> TaskStatus
    Task --> TaskResult
    DOMElement --> BoundingBox
```

#### [NEW] src/browser_pilot/models/task.py
- `Task`, `SubTask` Pydantic models with status tracking
- `TaskResult` for completion data

#### [NEW] src/browser_pilot/models/action.py
- `Action` model with before/after state
- `ActionType` enum (click, type, scroll, navigate, etc.)

#### [NEW] src/browser_pilot/models/result.py
- `ExecutionResult`, `StepResult` models
- Serialization for API responses

#### [NEW] src/browser_pilot/models/dom.py
- `DOMElement`, `BoundingBox` models
- DOM tree representation for grounding

---

### Phase 4: Browser Automation Layer

```mermaid
sequenceDiagram
    participant Agent as Agent Core
    participant Ctrl as BrowserController
    participant PW as Playwright
    participant Page as Browser Page
    participant DOM as DOM Inspector

    Agent->>Ctrl: initialize(config)
    Ctrl->>PW: launch(browser_type)
    PW->>Page: new_page()
    Ctrl-->>Agent: ready

    Agent->>Ctrl: navigate(url)
    Ctrl->>Page: goto(url)
    Page-->>Ctrl: loaded

    Agent->>DOM: inspect()
    DOM->>Page: evaluate(js_script)
    Page-->>DOM: dom_tree
    DOM-->>Agent: DOMElement[]

    Agent->>Ctrl: click(element)
    Ctrl->>Page: click(selector)
    Ctrl->>Page: wait_for_load()
    Ctrl-->>Agent: success

    Agent->>Ctrl: screenshot()
    Ctrl->>Page: screenshot(full_page)
    Ctrl-->>Agent: image_bytes
```

#### [NEW] src/browser_pilot/browser/controller.py
- `BrowserController` class wrapping Playwright
- Async lifecycle: `start()`, `stop()`, `restart()`
- Page management: `navigate()`, `go_back()`, `refresh()`
- Context manager support (`async with`)
- Video recording toggle
- Multiple browser type support (chromium, firefox, webkit)

#### [NEW] src/browser_pilot/browser/dom_inspector.py
- JavaScript injection for DOM tree extraction
- Filters: interactive-only, visible-only, within viewport
- Serialization to `DOMElement[]`
- Accessibility tree extraction
- Element indexing for vision annotation

#### [NEW] src/browser_pilot/browser/actions.py
- `click(element)` — Click with retry & verification
- `type_text(element, text)` — Type with human-like delay
- `scroll(direction, amount)` — Viewport scrolling
- `select_option(element, value)` — Dropdown selection
- `hover(element)` — Hover for tooltips/menus
- `press_key(key)` — Keyboard shortcuts
- `drag_and_drop(source, target)` — Drag operations
- `upload_file(element, path)` — File upload handling
- Each action returns `ActionResult` with success/failure

#### [NEW] src/browser_pilot/browser/anti_detection.py
- User-agent rotation
- Viewport randomization
- WebDriver flag masking
- Human-like mouse movement curves
- Randomized typing delays
- Cookie/fingerprint management

#### [NEW] src/browser_pilot/browser/profiles.py
- Browser profile creation & management
- Cookie persistence across sessions
- Proxy configuration
- Extension loading

---

### Phase 5: Vision Pipeline

```mermaid
flowchart LR
    subgraph Capture["📸 Capture"]
        SS["Take Screenshot"]
        CROP["Smart Crop"]
        RESIZE["Optimize Size"]
    end

    subgraph Annotate["🏷️ Annotate"]
        DOM_EX["Extract DOM"]
        BBOX["Bounding Boxes"]
        LABEL["Index Labels"]
        OVERLAY["Draw Overlays"]
    end

    subgraph Interpret["🧠 Interpret"]
        ENCODE["Base64 Encode"]
        PROMPT["Build Prompt"]
        VLM2["GPT-4o Vision"]
        PARSE2["Parse Response"]
    end

    subgraph Ground["✅ Ground"]
        VERIFY["Verify Element"]
        MATCH["DOM Matching"]
        CONF["Confidence Score"]
        DECIDE["Go / No-Go"]
    end

    SS --> CROP --> RESIZE
    RESIZE --> ENCODE
    SS --> DOM_EX --> BBOX --> LABEL --> OVERLAY
    OVERLAY --> ENCODE

    ENCODE --> PROMPT --> VLM2 --> PARSE2

    PARSE2 --> VERIFY --> MATCH --> CONF --> DECIDE

    style Capture fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style Annotate fill:#2d1b4e,stroke:#8b5cf6,color:#fff
    style Interpret fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style Ground fill:#1b4332,stroke:#40c057,color:#fff
```

#### [NEW] src/browser_pilot/vision/screenshot.py
- Full-page and viewport screenshot capture
- Smart cropping to region of interest
- Resolution optimization for API token efficiency
- Screenshot diffing between steps
- Artifact storage with naming convention

#### [NEW] src/browser_pilot/vision/annotator.py
- Overlay numbered bounding boxes on screenshots
- Color-coded by element type (input, button, link, etc.)
- Clickable region highlighting
- Set-of-Marks (SoM) prompting technique
- Clean image vs annotated image variants

#### [NEW] src/browser_pilot/vision/interpreter.py
- GPT-4o vision API integration
- Structured prompt engineering:
  - Current screenshot (annotated)
  - Current DOM state
  - Task context & history
  - Available actions
- Response parsing into `Action` objects
- Token usage tracking & budgeting
- Retry with exponential backoff on API errors

#### [NEW] src/browser_pilot/vision/grounding.py
- Verify proposed action against live DOM state
- Element existence check before execution
- Bounding box overlap verification
- Staleness detection (page changed since screenshot)
- Confidence scoring (0–1) for action validity
- Rejection threshold configuration

---

### Phase 6: Agent Core — The Brain

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Planning: receive_task()

    Planning --> Decomposing: plan_created
    Decomposing --> Executing: sub_tasks_ready

    Executing --> Observing: start_step
    Observing --> Deciding: screenshot_taken
    Deciding --> Grounding: action_proposed
    Grounding --> Acting: action_verified
    Grounding --> Deciding: action_rejected

    Acting --> Observing: action_complete
    Acting --> Recovering: action_failed

    Recovering --> Observing: retry
    Recovering --> Validating: max_retries

    Observing --> Validating: sub_task_done
    Validating --> Executing: more_sub_tasks
    Validating --> Completed: all_done

    Executing --> Failed: max_steps_reached
    Recovering --> Failed: unrecoverable

    Completed --> [*]
    Failed --> [*]

    note right of Planning
        Task Planner breaks
        instruction into
        atomic sub-tasks
    end note

    note right of Grounding
        Anti-hallucination:
        verify action against
        live DOM before commit
    end note

    note right of Validating
        Critic sub-agent
        validates completion
        criteria
    end note
```

#### [NEW] src/browser_pilot/agent/action_loop.py
```python
# Pseudocode for the core loop
class ActionLoop:
    async def run(self, task: Task) -> TaskResult:
        """Main observe-decide-act loop."""
        plan = await self.planner.plan(task)
        for sub_task in plan.sub_tasks:
            for step in range(self.max_steps):
                # 1. OBSERVE — screenshot + DOM state
                screenshot = await self.vision.capture()
                dom_state = await self.browser.inspect_dom()
                annotated = await self.vision.annotate(
                    screenshot, dom_state
                )

                # 2. DECIDE — ask GPT-4o what to do
                action = await self.vision.interpret(
                    annotated, dom_state, sub_task, history
                )

                # 3. GROUND — verify before executing
                is_valid = await self.grounding.verify(
                    action, dom_state
                )
                if not is_valid:
                    continue  # re-observe

                # 4. ACT — execute the action
                result = await self.browser.execute(action)
                history.append(result)

                # 5. VALIDATE — check if sub-task done
                if await self.critic.is_done(sub_task):
                    break

        return self.compile_result(task, history)
```

- Step counter with configurable maximum
- Action history for context window
- Error recovery with configurable retry policy
- Timeout per step and per task
- Cancellation support via asyncio

#### [NEW] src/browser_pilot/agent/planner.py

```mermaid
flowchart TB
    INPUT["📝 User Instruction"]
    LLM["🧠 GPT-4o Planner"]
    PARSE3["📋 Parse Sub-Tasks"]
    VALIDATE2["✅ Validate Plan"]
    DEPS["🔗 Dependency Graph"]
    EXEC["⚡ Execution Order"]

    INPUT --> LLM
    LLM --> PARSE3
    PARSE3 --> VALIDATE2
    VALIDATE2 --> DEPS
    DEPS --> EXEC

    subgraph Example["Example Decomposition"]
        T1["1. Open Google"]
        T2["2. Search 'AI startups 2025'"]
        T3["3. Open first result"]
        T4["4. Extract company names"]
        T5["5. Navigate to spreadsheet"]
        T6["6. Fill in extracted data"]
    end

    EXEC --> Example

    style INPUT fill:#e94560,stroke:#fff,color:#fff
    style LLM fill:#533483,stroke:#fff,color:#fff
    style Example fill:#0f3460,stroke:#fff,color:#fff
```

- Instruction → sub-task decomposition via LLM
- Dependency resolution between sub-tasks
- Dynamic re-planning when page changes unexpectedly
- Sub-task prioritization & ordering
- Plan serialization for resume capability
- Max sub-task limit to prevent infinite loops

#### [NEW] src/browser_pilot/agent/critic.py

```mermaid
flowchart LR
    subgraph Input["Critic Input"]
        ST["Sub-Task Description"]
        BEFORE["Before State"]
        AFTER["After State"]
        ACTIONS2["Action History"]
    end

    subgraph Analysis["Critic Analysis"]
        COMPARE["State Comparison"]
        CRITERIA["Check Criteria"]
        EVIDENCE["Gather Evidence"]
    end

    subgraph Output["Critic Output"]
        PASS["✅ PASS - Task Complete"]
        FAIL["❌ FAIL - Continue"]
        PARTIAL["⚠️ PARTIAL - Adjust"]
    end

    ST --> COMPARE
    BEFORE --> COMPARE
    AFTER --> COMPARE
    ACTIONS2 --> CRITERIA

    COMPARE --> CRITERIA --> EVIDENCE

    EVIDENCE --> PASS
    EVIDENCE --> FAIL
    EVIDENCE --> PARTIAL

    style Input fill:#1a1a2e,stroke:#e94560,color:#fff
    style Analysis fill:#16213e,stroke:#0f3460,color:#fff
    style Output fill:#0f3460,stroke:#533483,color:#fff
```

- Separate LLM call to evaluate task completion
- Compares before/after DOM states
- Checks explicit success criteria from sub-task
- Returns: PASS / FAIL / PARTIAL with reasoning
- Prevents premature "done" declarations
- Configurable strictness level

#### [NEW] src/browser_pilot/agent/memory.py
- Sliding window context management
- Summarization of old steps to save tokens
- Key observation extraction & persistence
- Cross-sub-task knowledge transfer
- Token budget tracking

#### [NEW] src/browser_pilot/agent/prompts.py
- System prompts for each LLM role:
  - **Planner**: Task decomposition instructions
  - **Actor**: Action decision instructions
  - **Critic**: Completion validation instructions
  - **Summarizer**: Context compression instructions
- Few-shot examples for each prompt
- Dynamic prompt construction with context injection

#### [NEW] src/browser_pilot/agent/state.py
- Finite state machine for agent lifecycle
- State transitions with validation
- Serializable state for persistence/resume
- Event hooks for state changes

---

### Phase 7: LangChain Tool Integration

```mermaid
flowchart TB
    subgraph Tools["🛠️ LangChain Tools"]
        BT["Browser Tools"]
        NT["Navigation Tools"]
        FT["Form Tools"]
        ET["Extraction Tools"]
    end

    subgraph BrowserTools["Browser Tools"]
        BT1["click_element"]
        BT2["type_text"]
        BT3["scroll_page"]
        BT4["take_screenshot"]
        BT5["press_key"]
    end

    subgraph NavTools["Navigation Tools"]
        NT1["navigate_to_url"]
        NT2["go_back"]
        NT3["go_forward"]
        NT4["refresh_page"]
        NT5["switch_tab"]
    end

    subgraph FormTools["Form Tools"]
        FT1["fill_input"]
        FT2["select_dropdown"]
        FT3["check_checkbox"]
        FT4["submit_form"]
        FT5["upload_file"]
    end

    subgraph ExtTools["Extraction Tools"]
        ET1["extract_text"]
        ET2["extract_table"]
        ET3["extract_links"]
        ET4["extract_structured"]
        ET5["get_page_title"]
    end

    BT --> BrowserTools
    NT --> NavTools
    FT --> FormTools
    ET --> ExtTools

    style Tools fill:#1a1a2e,stroke:#e94560,color:#fff
    style BrowserTools fill:#16213e,stroke:#0f3460,color:#fff
    style NavTools fill:#0f3460,stroke:#533483,color:#fff
    style FormTools fill:#533483,stroke:#e94560,color:#fff
    style ExtTools fill:#1a1a2e,stroke:#0f3460,color:#fff
```

#### [NEW] src/browser_pilot/tools/browser_tools.py
- `@tool` decorated functions for browser actions
- Input validation via Pydantic schemas
- Return structured results with success/failure
- Error messages useful for LLM self-correction

#### [NEW] src/browser_pilot/tools/navigation_tools.py
- URL navigation with wait-for-load
- Tab management tools
- History navigation (back/forward)
- URL validation and sanitization

#### [NEW] src/browser_pilot/tools/form_tools.py
- Form field detection and filling
- Dropdown/select handling
- Checkbox/radio button toggling
- File upload via file chooser
- Form submission with confirmation

#### [NEW] src/browser_pilot/tools/extraction_tools.py
- Text extraction from selectors
- Table extraction to structured data
- Link harvesting with metadata
- Structured data extraction via schemas
- Screenshot-to-text (OCR fallback)

---

### Phase 8: FastAPI Server

```mermaid
flowchart TB
    subgraph Endpoints["API Endpoints"]
        direction TB
        POST_TASK["POST /api/v1/tasks"]
        GET_TASK["GET /api/v1/tasks/{id}"]
        LIST_TASKS["GET /api/v1/tasks"]
        CANCEL["DELETE /api/v1/tasks/{id}"]
        STREAM["GET /api/v1/tasks/{id}/stream"]
        WS_EP["WS /api/v1/ws"]
        HEALTH["GET /api/v1/health"]
        SCREENSHOTS["GET /api/v1/tasks/{id}/screenshots"]
    end

    subgraph Middleware["Middleware Stack"]
        CORS2["CORS"]
        AUTH2["API Key Auth"]
        RATE2["Rate Limiting"]
        LOG2["Request Logging"]
        ERR["Error Handler"]
    end

    subgraph TaskEngine["Task Engine"]
        QUEUE["Task Queue"]
        WORKER["Background Worker"]
        AGENT2["Agent Instance"]
        EVENTS["Event Emitter"]
    end

    Endpoints --> Middleware --> TaskEngine

    EVENTS --> STREAM
    EVENTS --> WS_EP

    style Endpoints fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style Middleware fill:#2d1b4e,stroke:#8b5cf6,color:#fff
    style TaskEngine fill:#1b4332,stroke:#40c057,color:#fff
```

#### [NEW] src/browser_pilot/server/app.py
- FastAPI application factory
- CORS, docs configuration
- Lifespan events (startup/shutdown)
- Browser pool initialization

#### [NEW] src/browser_pilot/server/routes/tasks.py
- `POST /api/v1/tasks` — Create & enqueue task
- `GET /api/v1/tasks/{id}` — Get task status
- `GET /api/v1/tasks` — List all tasks (paginated)
- `DELETE /api/v1/tasks/{id}` — Cancel task
- `GET /api/v1/tasks/{id}/screenshots` — Get screenshots

#### [NEW] src/browser_pilot/server/routes/stream.py
- `GET /api/v1/tasks/{id}/stream` — SSE endpoint
- Real-time action updates
- Screenshot URLs in events
- Step completion notifications
- Error event streaming

#### [NEW] src/browser_pilot/server/routes/websocket.py
- `WS /api/v1/ws` — Bidirectional WebSocket
- Live screenshot streaming
- Interactive task control (pause/resume/cancel)
- Action-by-action progress reporting

#### [NEW] src/browser_pilot/server/routes/health.py
- `GET /api/v1/health` — Server health check
- Browser pool status
- Memory usage
- Active task count

#### [NEW] src/browser_pilot/server/middleware.py
- API key authentication
- Rate limiting (per-IP and per-key)
- CORS configuration
- Request/response logging

#### [NEW] src/browser_pilot/server/schemas.py
- `CreateTaskRequest` / `CreateTaskResponse`
- `TaskStatusResponse`
- `TaskListResponse` with pagination
- `StreamEvent` for SSE
- `WebSocketMessage` for WS
- `ErrorResponse`

#### [NEW] src/browser_pilot/server/dependencies.py
- Settings dependency injection
- Browser pool dependency
- Agent factory dependency
- Auth dependency

---

### Phase 9: CLI Interface

```mermaid
flowchart LR
    CLI2["browserpilot CLI"]

    CLI2 --> RUN["run 'instruction'"]
    CLI2 --> SERVE["serve --port 8000"]
    CLI2 --> STATUS["status --task-id abc"]
    CLI2 --> LIST2["list --limit 10"]
    CLI2 --> SCREENSHOT2["screenshot --url ..."]
    CLI2 --> CONFIG2["config --show"]

    RUN --> |"Execute task"| AGENT3["Agent"]
    SERVE --> |"Start API"| SERVER2["FastAPI"]
    STATUS --> |"Query"| SERVER2
    LIST2 --> |"Query"| SERVER2

    style CLI2 fill:#e94560,stroke:#fff,color:#fff
    style AGENT3 fill:#533483,stroke:#fff,color:#fff
    style SERVER2 fill:#0f3460,stroke:#fff,color:#fff
```

#### [NEW] src/browser_pilot/__main__.py
- `browserpilot run "instruction"` — Execute a task
- `browserpilot serve` — Start API server
- `browserpilot status <task_id>` — Check task status
- `browserpilot list` — List recent tasks
- `browserpilot config` — Show current configuration
- Rich terminal output with progress bars
- Argument parsing via `argparse` or `click`

---

### Phase 10: Utilities

#### [NEW] src/browser_pilot/utils/image.py
- Screenshot compression & optimization
- Base64 encoding/decoding
- Image diffing between steps
- Thumbnail generation
- Token-count estimation for images

#### [NEW] src/browser_pilot/utils/retry.py
- Configurable retry decorator
- Exponential backoff with jitter
- Exception type filtering
- Max attempts & timeout

#### [NEW] src/browser_pilot/utils/rate_limiter.py
- Token bucket rate limiter for OpenAI API
- Concurrent request limiter
- Per-minute and per-day budgets
- Cost estimation & alerts

#### [NEW] src/browser_pilot/utils/sanitizer.py
- URL sanitization & validation
- Input text sanitization
- JavaScript injection prevention
- File path sanitization

---

### Phase 11: Testing Infrastructure

```mermaid
flowchart TB
    subgraph UnitTests["Unit Tests"]
        UT1["test_planner.py"]
        UT2["test_critic.py"]
        UT3["test_action_loop.py"]
        UT4["test_screenshot.py"]
        UT5["test_annotator.py"]
        UT6["test_dom_inspector.py"]
        UT7["test_actions.py"]
        UT8["test_grounding.py"]
        UT9["test_state.py"]
        UT10["test_memory.py"]
        UT11["test_sanitizer.py"]
    end

    subgraph IntegTests["Integration Tests"]
        IT1["test_vision_pipeline.py"]
        IT2["test_agent_e2e.py"]
        IT3["test_browser_actions.py"]
        IT4["test_api_server.py"]
    end

    subgraph E2ETests["E2E Tests"]
        E1["test_form_filling.py"]
        E2["test_navigation.py"]
        E3["test_data_extraction.py"]
        E4["test_complex_tasks.py"]
    end

    subgraph Infra["Test Infrastructure"]
        MOCK["Mock LLM Responses"]
        FIX["Pytest Fixtures"]
        PAGES["Test HTML Pages"]
        SNAP["Snapshot Testing"]
    end

    Infra --> UnitTests
    Infra --> IntegTests
    Infra --> E2ETests

    style UnitTests fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style IntegTests fill:#2d1b4e,stroke:#8b5cf6,color:#fff
    style E2ETests fill:#1b4332,stroke:#40c057,color:#fff
    style Infra fill:#1a1a2e,stroke:#e94560,color:#fff
```

#### [NEW] tests/conftest.py
- Shared fixtures: mock LLM, test browser, test pages
- Async event loop configuration
- Temporary directory management
- Environment variable mocking

#### Unit Tests (11 files)
- Mock all external dependencies (LLM, browser)
- Test pure logic: planning, grounding, state machine
- Edge cases: empty DOM, timeout, invalid actions
- Minimum 90% code coverage target

#### Integration Tests (4 files)
- Test component interactions with real browser
- Vision pipeline end-to-end (screenshot → action)
- API server with test client
- Database operations if applicable

#### E2E Tests (4 files)
- Full task execution on test websites
- Form filling on a local HTML fixture
- Multi-page navigation scenarios
- Data extraction accuracy validation

---

### Phase 12: CI/CD & Deployment

```mermaid
flowchart LR
    subgraph CI["GitHub Actions CI"]
        LINT["Ruff Lint"]
        TYPE["Type Check"]
        UNIT2["Unit Tests"]
        INT2["Integration Tests"]
        E2E2["E2E Tests"]
        BUILD["Build Package"]
        COV["Coverage Report"]
    end

    PUSH["Git Push"] --> LINT
    LINT --> TYPE --> UNIT2 --> INT2 --> E2E2
    E2E2 --> BUILD --> COV

    subgraph Deploy["Deployment"]
        DOCKER["Docker Image"]
        PYPI["PyPI Release"]
        DOCS2["Deploy Docs"]
    end

    BUILD --> DOCKER
    BUILD --> PYPI
    BUILD --> DOCS2

    style CI fill:#1e3a5f,stroke:#4a90d9,color:#fff
    style Deploy fill:#1b4332,stroke:#40c057,color:#fff
```

#### [NEW] .github/workflows/ci.yml
```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  test:
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --all-extras
      - run: npx playwright install chromium
      - run: uv run pytest tests/unit/ -v
        continue-on-error: true
      - run: uv run pytest tests/integration/ -v
        continue-on-error: true
      - run: uv run pytest tests/e2e/ -v
        continue-on-error: true

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
```

#### [NEW] .github/workflows/release.yml
- Triggered on tag push (v*)
- Build & publish to PyPI
- Create GitHub release
- Build & push Docker image

#### [NEW] Dockerfile
- Multi-stage build
- Python 3.12 slim base
- Playwright dependencies
- Non-root user
- Health check endpoint

---

## 5. Data Flow Diagrams

### Complete Task Execution Flow

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant Q as Task Queue
    participant P as Planner
    participant L as Action Loop
    participant V as Vision
    participant B as Browser
    participant G as Grounding
    participant C as Critic
    participant LLM as GPT-4o

    User->>API: POST /tasks {instruction}
    API->>Q: enqueue(task)
    API-->>User: 202 {task_id}

    Q->>P: process(task)
    P->>LLM: decompose(instruction)
    LLM-->>P: sub_tasks[]
    P->>L: execute(sub_tasks)

    loop For each sub-task
        loop Action Loop (max N steps)
            L->>B: screenshot()
            B-->>L: image_bytes
            L->>B: inspect_dom()
            B-->>L: dom_elements[]

            L->>V: annotate(image, elements)
            V-->>L: annotated_image

            L->>LLM: decide(annotated, dom, context)
            LLM-->>L: proposed_action

            L->>G: verify(action, dom)
            alt Action Valid
                G-->>L: ✅ verified
                L->>B: execute(action)
                B-->>L: result
            else Action Invalid
                G-->>L: ❌ rejected
                Note over L: Re-observe
            end
        end

        L->>C: validate(sub_task, state)
        C->>LLM: check_completion()
        alt Done
            LLM-->>C: ✅ complete
            C-->>L: PASS
        else Not Done
            LLM-->>C: ❌ incomplete
            C-->>L: FAIL
            Note over L: Adjust & retry
        end
    end

    L-->>API: TaskResult
    API-->>User: GET /tasks/{id} → result
```

### Vision Pipeline Detail

```mermaid
flowchart TB
    subgraph Input2["Input"]
        RAW["Raw Screenshot (1920×1080)"]
        DOM2["DOM Elements (JSON)"]
    end

    subgraph Process["Processing"]
        RESIZE2["Resize to 1280×720"]
        EXTRACT2["Filter Interactive"]
        BBOX2["Calculate BBoxes"]
        NUMBER["Number Elements"]
        DRAW["Draw Overlays"]
        COMPOSE["Compose Prompt"]
    end

    subgraph LLMCall["GPT-4o Vision Call"]
        IMG["Image (base64)"]
        SYSP["System Prompt"]
        USRP["User Prompt"]
        HIST["Action History"]
    end

    subgraph Output2["Parsed Output"]
        ACT["Action Type"]
        TGT["Target Element #"]
        PARAMS2["Parameters"]
        REASON2["Reasoning"]
        CONFID["Confidence"]
    end

    RAW --> RESIZE2
    DOM2 --> EXTRACT2 --> BBOX2 --> NUMBER
    RESIZE2 --> DRAW
    NUMBER --> DRAW
    DRAW --> IMG
    COMPOSE --> SYSP
    COMPOSE --> USRP
    COMPOSE --> HIST

    IMG --> LLMCall
    SYSP --> LLMCall
    USRP --> LLMCall
    HIST --> LLMCall

    LLMCall --> ACT
    LLMCall --> TGT
    LLMCall --> PARAMS2
    LLMCall --> REASON2
    LLMCall --> CONFID

    style Input2 fill:#1a1a2e,stroke:#e94560,color:#fff
    style Process fill:#16213e,stroke:#0f3460,color:#fff
    style LLMCall fill:#533483,stroke:#e94560,color:#fff
    style Output2 fill:#0f3460,stroke:#533483,color:#fff
```

---

## 6. Anti-Hallucination Grounding Strategy

```mermaid
flowchart TB
    PROPOSED["Proposed Action from LLM"]

    CHECK1{"Element exists
    in DOM?"}
    CHECK2{"Element is
    visible?"}
    CHECK3{"Element is
    interactive?"}
    CHECK4{"BBox matches
    screenshot?"}
    CHECK5{"Page hasn't
    changed?"}

    EXECUTE["✅ Execute Action"]
    REJECT["❌ Reject & Re-observe"]

    PROPOSED --> CHECK1
    CHECK1 -->|Yes| CHECK2
    CHECK1 -->|No| REJECT

    CHECK2 -->|Yes| CHECK3
    CHECK2 -->|No| REJECT

    CHECK3 -->|Yes| CHECK4
    CHECK3 -->|No| REJECT

    CHECK4 -->|Yes| CHECK5
    CHECK4 -->|No| REJECT

    CHECK5 -->|Yes| EXECUTE
    CHECK5 -->|No| REJECT

    REJECT -->|"Take new screenshot"| PROPOSED

    style PROPOSED fill:#e94560,stroke:#fff,color:#fff
    style EXECUTE fill:#40c057,stroke:#fff,color:#fff
    style REJECT fill:#ff6b6b,stroke:#fff,color:#fff
```

The grounding system performs 5 verification checks before any
action is committed:

1. **Element Existence** — Is the target element in the current DOM?
2. **Element Visibility** — Is the element visible in the viewport?
3. **Interactivity** — Is the element actually interactive
   (button, input, link)?
4. **Bounding Box Match** — Does the element's position match
   what the LLM saw in the screenshot?
5. **Page Freshness** — Has the page changed since the screenshot
   was taken?

If any check fails, the action is rejected and the agent
re-observes the page before deciding again.

---

## 7. Error Recovery Strategy

```mermaid
flowchart TB
    ERROR["Action Failed"]

    R1{"Retry
    count < max?"}
    R2{"Is it a
    network error?"}
    R3{"Is it a
    DOM change?"}
    R4{"Is it an
    LLM error?"}

    RETRY["Retry Same Action"]
    REOBS["Re-observe Page"]
    BACKOFF["Exponential Backoff"]
    REPLAN["Re-plan Sub-task"]
    FAIL2["Mark Task Failed"]

    ERROR --> R1
    R1 -->|Yes| R2
    R1 -->|No| FAIL2

    R2 -->|Yes| BACKOFF --> RETRY
    R2 -->|No| R3

    R3 -->|Yes| REOBS
    R3 -->|No| R4

    R4 -->|Yes| BACKOFF --> RETRY
    R4 -->|No| REPLAN

    RETRY --> ERROR
    REOBS --> ERROR

    style ERROR fill:#ff6b6b,stroke:#fff,color:#fff
    style FAIL2 fill:#c92a2a,stroke:#fff,color:#fff
    style RETRY fill:#ffd43b,stroke:#333,color:#333
    style REOBS fill:#4263eb,stroke:#fff,color:#fff
    style REPLAN fill:#7950f2,stroke:#fff,color:#fff
```

---

## 8. Performance & Cost Optimization

```mermaid
pie title Token Budget Distribution (per step)
    "Screenshot Image" : 40
    "DOM Context" : 25
    "System Prompt" : 15
    "Action History" : 15
    "Response" : 5
```

| Optimization                    | Impact                        |
|---------------------------------|-------------------------------|
| Screenshot downscaling          | –60% image tokens             |
| DOM filtering (interactive only)| –70% context tokens           |
| History summarization           | –50% history tokens           |
| Prompt caching (Anthropic)      | –50% on repeated prompts      |
| Batch grounding checks          | –30% DOM queries              |
| Step-level caching              | Skip unchanged pages          |

---

## Open Questions

> [!IMPORTANT]
> **LLM Provider**: Should we support multiple LLM providers
> (Anthropic Claude, Google Gemini) in addition to GPT-4o, or
> focus exclusively on GPT-4o for v1?

> [!IMPORTANT]
> **Persistence**: Should task state be persisted to a database
> (SQLite? PostgreSQL?) for crash recovery, or is in-memory
> sufficient for v1?

> [!IMPORTANT]
> **Concurrency**: How many simultaneous browser sessions should
> the server support? Each session requires ~200MB RAM for the
> browser process.

> [!WARNING]
> **browser-use Integration**: Should we build directly on top
> of the `browser-use` library (which provides the agent loop),
> or implement our own agent loop from scratch using raw
> Playwright + LangChain? The former is faster but less flexible.

---

## Verification Plan

### Automated Tests

| Test Suite       | Command                              | Coverage     |
|------------------|--------------------------------------|--------------|
| Unit Tests       | `uv run pytest tests/unit/ -v`       | 90%+ target  |
| Integration      | `uv run pytest tests/integration/ -v`| Core flows   |
| E2E              | `uv run pytest tests/e2e/ -v`        | Happy paths  |
| Lint             | `uv run ruff check .`                | Zero errors  |
| Format           | `uv run ruff format --check .`       | Zero diffs   |

### Manual Verification
1. Run a simple navigation task via CLI
2. Run a form-filling task via CLI
3. Run a data extraction task via CLI
4. Start the API server and test via curl/Postman
5. Verify WebSocket streaming in a browser client
6. Check screenshot artifacts are saved correctly
7. Verify the critic correctly rejects incomplete tasks
8. Test anti-hallucination by removing an element mid-task

### Performance Benchmarks
- Task: "Search Google for 'BrowserPilot' and extract the top 5 results"
  - Target: < 60 seconds, < 15 steps
  - Token budget: < 50,000 tokens total
