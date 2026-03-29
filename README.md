<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GPT--4o-Vision-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-Agent-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Server-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
</p>

<h1 align="center">🤖 BrowserPilot</h1>

<p align="center">
  <strong>A fully autonomous browser agent that navigates the web,<br/>
  fills forms, extracts data, and completes multi-step tasks<br/>
  from plain English instructions.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-configuration">Config</a> •
  <a href="#-testing">Testing</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🎯 What is BrowserPilot?

BrowserPilot is an AI-powered autonomous browser agent that
interprets natural language instructions and executes complex
web tasks without human intervention. It combines **GPT-4o's
multimodal vision** with **Playwright's browser automation** to
create an agent that can _see_, _think_, and _act_ on any website.

```
"Research the top 5 AI startups of 2025 and fill this spreadsheet"
                              ↓
                     🤖 BrowserPilot
                              ↓
         ✅ Opens Google → Searches → Reads articles
         ✅ Extracts company names, funding, descriptions
         ✅ Navigates to spreadsheet → Fills in data
         ✅ Verifies completion → Reports results
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Vision-Grounded Actions** | Screenshots → GPT-4o → Intelligent decisions |
| 📋 **Task Decomposition** | Breaks complex instructions into atomic steps |
| ✅ **Anti-Hallucination** | Verifies every action against live DOM state |
| 🔍 **Critic Validation** | Sub-agent validates task completion criteria |
| 🌐 **Multi-Browser** | Chromium, Firefox, and WebKit support |
| 🔌 **REST & WebSocket API** | FastAPI server for external integrations |
| 📡 **Real-Time Streaming** | SSE/WebSocket for live progress updates |
| 🛡️ **Stealth Mode** | Anti-detection for bot-resistant sites |
| 📸 **Screenshot Artifacts** | Before/after screenshots for every action |
| 🔄 **Error Recovery** | Automatic retry with intelligent re-planning |
| ⚡ **CLI & API Modes** | Run from terminal or integrate via REST |
| 📊 **Structured Extraction** | Extract tables, text, and structured data |

---

## 🏗️ Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph UserLayer["👤 User Interfaces"]
        CLI["🖥️ CLI<br/><code>browserpilot run</code>"]
        REST["🌐 REST API<br/><code>POST /tasks</code>"]
        WS["🔌 WebSocket<br/>Live Streaming"]
        DASH["📊 Dashboard<br/>Web UI"]
    end

    subgraph APILayer["🖥️ FastAPI Server"]
        ROUTER["Router"]
        AUTH["🔒 Auth"]
        RATE["⏱️ Rate Limiter"]
        SSE["📡 SSE Stream"]
        QUEUE["📋 Task Queue"]
    end

    subgraph AgentLayer["🧠 Agent Core"]
        PLANNER["📋 Task Planner<br/>Decomposes instructions"]
        LOOP["🔄 Action Loop<br/>Observe → Decide → Act"]
        CRITIC["🔍 Critic Agent<br/>Validates completion"]
        MEMORY["💾 Memory<br/>Context management"]
        STATE["📊 State Machine<br/>Lifecycle tracking"]
    end

    subgraph VisionLayer["👁️ Vision Pipeline"]
        CAPTURE["📸 Screenshot"]
        ANNOTATE["🏷️ Annotator<br/>Set-of-Marks"]
        GPT4O["🧠 GPT-4o Vision<br/>Action decisions"]
        GROUND["✅ DOM Grounding<br/>Anti-hallucination"]
    end

    subgraph BrowserLayer["🌐 Browser Engine"]
        PW["🎭 Playwright"]
        DOM["🌳 DOM Inspector"]
        ACTIONS["⚡ Action Executor"]
        STEALTH["🛡️ Anti-Detection"]
    end

    subgraph DataLayer["💾 Data & Storage"]
        ARTIFACTS["📁 Artifacts"]
        HISTORY["📜 History"]
        EXPORT["📊 Exporter"]
        SCREENSHOTS["📸 Screenshots"]
    end

    CLI --> ROUTER
    REST --> ROUTER
    WS --> ROUTER
    DASH --> ROUTER

    ROUTER --> AUTH --> RATE --> QUEUE

    QUEUE --> PLANNER
    PLANNER --> LOOP
    LOOP <--> CRITIC
    LOOP <--> MEMORY
    LOOP --> STATE

    LOOP --> CAPTURE --> ANNOTATE --> GPT4O --> GROUND
    GROUND --> LOOP

    GROUND --> PW
    PW --> DOM
    PW --> ACTIONS
    PW --> STEALTH

    LOOP --> ARTIFACTS
    LOOP --> HISTORY
    HISTORY --> EXPORT
    CAPTURE --> SCREENSHOTS

    QUEUE --> SSE
    SSE --> WS

    style UserLayer fill:#0d1117,stroke:#58a6ff,color:#c9d1d9
    style APILayer fill:#161b22,stroke:#1f6feb,color:#c9d1d9
    style AgentLayer fill:#0d1117,stroke:#8b5cf6,color:#c9d1d9
    style VisionLayer fill:#161b22,stroke:#f97316,color:#c9d1d9
    style BrowserLayer fill:#0d1117,stroke:#10b981,color:#c9d1d9
    style DataLayer fill:#161b22,stroke:#6366f1,color:#c9d1d9
```

---

### Agent Decision Flow

```mermaid
flowchart TB
    START(["🚀 Receive Instruction"])
    PLAN["📋 Plan<br/>Decompose into sub-tasks"]
    SUBTASK["📎 Select Next Sub-Task"]

    subgraph ActionLoop["🔄 Observe → Decide → Act Loop"]
        OBSERVE["📸 OBSERVE<br/>Take screenshot + inspect DOM"]
        DECIDE["🧠 DECIDE<br/>GPT-4o analyzes & proposes action"]
        VERIFY["✅ VERIFY<br/>Ground action against live DOM"]
        ACT["⚡ ACT<br/>Execute via Playwright"]
        RECORD["📝 RECORD<br/>Save action + screenshot"]
    end

    VALIDATE["🔍 VALIDATE<br/>Critic checks completion"]
    MORE{"More<br/>sub-tasks?"}
    DONE(["✅ Task Complete"])
    FAIL(["❌ Task Failed"])

    START --> PLAN --> SUBTASK
    SUBTASK --> OBSERVE
    OBSERVE --> DECIDE
    DECIDE --> VERIFY
    VERIFY -->|"✅ Valid"| ACT
    VERIFY -->|"❌ Invalid"| OBSERVE
    ACT --> RECORD
    RECORD --> VALIDATE
    VALIDATE -->|"❌ Not done"| OBSERVE
    VALIDATE -->|"✅ Done"| MORE
    MORE -->|"Yes"| SUBTASK
    MORE -->|"No"| DONE

    ACT -->|"Max retries exceeded"| FAIL

    style START fill:#10b981,stroke:#fff,color:#fff
    style DONE fill:#10b981,stroke:#fff,color:#fff
    style FAIL fill:#ef4444,stroke:#fff,color:#fff
    style ActionLoop fill:#1e1b4b,stroke:#8b5cf6,color:#c9d1d9
```

---

### Component Interaction Sequence

```mermaid
sequenceDiagram
    actor User
    participant CLI as 🖥️ CLI
    participant API as 🌐 FastAPI
    participant Planner as 📋 Planner
    participant Loop as 🔄 Action Loop
    participant Vision as 👁️ Vision
    participant Browser as 🌐 Browser
    participant Ground as ✅ Grounder
    participant Critic as 🔍 Critic
    participant LLM as 🧠 GPT-4o

    User->>CLI: browserpilot run "Search for..."
    CLI->>API: POST /api/v1/tasks

    rect rgb(30, 27, 75)
        Note over Planner,LLM: Phase 1: Task Planning
        API->>Planner: plan(instruction)
        Planner->>LLM: Decompose into sub-tasks
        LLM-->>Planner: [sub_task_1, sub_task_2, ...]
    end

    rect rgb(20, 83, 45)
        Note over Loop,Browser: Phase 2: Execution Loop
        loop For each sub-task
            loop Until sub-task complete
                Loop->>Browser: screenshot()
                Browser-->>Loop: 📸 image
                Loop->>Browser: inspect_dom()
                Browser-->>Loop: 🌳 DOM tree

                Loop->>Vision: annotate(image, DOM)
                Vision-->>Loop: 🏷️ annotated image

                Loop->>LLM: What action should I take?
                LLM-->>Loop: click(element #7)

                Loop->>Ground: verify(action, DOM)
                alt Action is grounded
                    Ground-->>Loop: ✅ verified
                    Loop->>Browser: execute(click #7)
                    Browser-->>Loop: ✅ success
                else Action hallucinated
                    Ground-->>Loop: ❌ rejected
                    Note over Loop: Re-observe page
                end
            end

            Loop->>Critic: Is sub-task done?
            Critic->>LLM: Evaluate completion
            LLM-->>Critic: ✅ / ❌
        end
    end

    Loop-->>API: TaskResult
    API-->>CLI: ✅ Task completed
    CLI-->>User: Results displayed
```

---

### Vision Pipeline Architecture

```mermaid
flowchart LR
    subgraph Capture["📸 Capture Stage"]
        RAW["Raw Screenshot<br/>1920 × 1080"]
        RESIZE["Resize & Optimize<br/>1280 × 720"]
        ENCODE["Base64 Encode"]
    end

    subgraph DOM_Stage["🌳 DOM Analysis"]
        EXTRACT["Extract DOM Tree"]
        FILTER["Filter Interactive<br/>Elements Only"]
        BBOX["Calculate<br/>Bounding Boxes"]
        INDEX["Assign Index<br/>Numbers"]
    end

    subgraph Annotate_Stage["🏷️ Annotation"]
        OVERLAY["Draw Numbered<br/>Bounding Boxes"]
        COLOR["Color-Code by<br/>Element Type"]
        COMPOSE["Compose Final<br/>Annotated Image"]
    end

    subgraph LLM_Stage["🧠 GPT-4o Vision"]
        PROMPT["Build Multimodal<br/>Prompt"]
        CALL["API Call with<br/>Image + Context"]
        PARSE["Parse Structured<br/>Response"]
    end

    subgraph Output_Stage["📤 Output"]
        ACTION["Action Type<br/>click / type / scroll"]
        TARGET["Target Element<br/>Index #N"]
        PARAMS["Parameters<br/>text, url, etc."]
        CONF["Confidence<br/>Score 0-1"]
    end

    RAW --> RESIZE --> ENCODE
    EXTRACT --> FILTER --> BBOX --> INDEX
    ENCODE --> OVERLAY
    INDEX --> OVERLAY
    OVERLAY --> COLOR --> COMPOSE
    COMPOSE --> PROMPT
    PROMPT --> CALL --> PARSE
    PARSE --> ACTION
    PARSE --> TARGET
    PARSE --> PARAMS
    PARSE --> CONF

    style Capture fill:#0c4a6e,stroke:#38bdf8,color:#fff
    style DOM_Stage fill:#312e81,stroke:#818cf8,color:#fff
    style Annotate_Stage fill:#4c1d95,stroke:#a78bfa,color:#fff
    style LLM_Stage fill:#7c2d12,stroke:#fb923c,color:#fff
    style Output_Stage fill:#064e3b,stroke:#34d399,color:#fff
```

---

### Anti-Hallucination Grounding System

```mermaid
flowchart TB
    PROPOSED["🧠 LLM Proposed Action<br/><i>click element #7</i>"]

    C1{"1️⃣ Does element #7<br/>exist in DOM?"}
    C2{"2️⃣ Is element #7<br/>visible on page?"}
    C3{"3️⃣ Is element #7<br/>interactive?"}
    C4{"4️⃣ Does BBox match<br/>screenshot position?"}
    C5{"5️⃣ Is the page still<br/>in the same state?"}

    EXECUTE["✅ EXECUTE ACTION<br/>Safe to proceed"]
    REJECT["❌ REJECT & RE-OBSERVE<br/>Take fresh screenshot"]

    PROPOSED --> C1
    C1 -->|"✅ Yes"| C2
    C1 -->|"❌ No"| REJECT

    C2 -->|"✅ Yes"| C3
    C2 -->|"❌ No"| REJECT

    C3 -->|"✅ Yes"| C4
    C3 -->|"❌ No"| REJECT

    C4 -->|"✅ Yes"| C5
    C4 -->|"❌ No"| REJECT

    C5 -->|"✅ Yes"| EXECUTE
    C5 -->|"❌ No"| REJECT

    REJECT --> |"New screenshot"| PROPOSED

    style PROPOSED fill:#6366f1,stroke:#fff,color:#fff
    style EXECUTE fill:#10b981,stroke:#fff,color:#fff
    style REJECT fill:#ef4444,stroke:#fff,color:#fff
    style C1 fill:#1e293b,stroke:#94a3b8,color:#e2e8f0
    style C2 fill:#1e293b,stroke:#94a3b8,color:#e2e8f0
    style C3 fill:#1e293b,stroke:#94a3b8,color:#e2e8f0
    style C4 fill:#1e293b,stroke:#94a3b8,color:#e2e8f0
    style C5 fill:#1e293b,stroke:#94a3b8,color:#e2e8f0
```

---

### Task Decomposition Example

```mermaid
flowchart TB
    TASK["📝 User Instruction<br/><i>'Research the top 5 AI startups<br/>of 2025 and fill this spreadsheet'</i>"]

    subgraph Plan["📋 Decomposed Plan"]
        S1["1️⃣ Open Google.com"]
        S2["2️⃣ Search for<br/>'top AI startups 2025'"]
        S3["3️⃣ Open the first<br/>relevant article"]
        S4["4️⃣ Extract startup names,<br/>funding, and descriptions"]
        S5["5️⃣ Navigate to the<br/>target spreadsheet URL"]
        S6["6️⃣ Fill Row 1 with<br/>Startup #1 data"]
        S7["7️⃣ Fill Row 2 with<br/>Startup #2 data"]
        S8["8️⃣ Repeat for remaining<br/>startups"]
        S9["9️⃣ Verify all 5 rows<br/>are filled correctly"]
    end

    TASK --> S1
    S1 --> S2 --> S3 --> S4
    S4 --> S5 --> S6 --> S7 --> S8 --> S9

    subgraph Dependencies["🔗 Dependency Graph"]
        D1["S1 → S2: Need Google open"]
        D2["S3 → S4: Need article loaded"]
        D3["S4 → S6: Need extracted data"]
        D4["S6…S8: Sequential filling"]
    end

    style TASK fill:#7c3aed,stroke:#fff,color:#fff
    style Plan fill:#0f172a,stroke:#6366f1,color:#e2e8f0
    style Dependencies fill:#1e1b4b,stroke:#8b5cf6,color:#c9d1d9
```

---

### State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: Agent initialized

    Idle --> Planning: receive_task()
    Planning --> Decomposing: plan_generated
    Decomposing --> Executing: sub_tasks_ready

    state Executing {
        [*] --> Observing
        Observing --> Deciding: screenshot_captured
        Deciding --> Grounding: action_proposed
        Grounding --> Acting: action_verified
        Grounding --> Observing: action_rejected
        Acting --> Observing: step_complete
        Acting --> Recovering: action_failed
        Recovering --> Observing: retry
        Recovering --> [*]: max_retries
    }

    Executing --> Validating: sub_task_boundary
    Validating --> Executing: more_sub_tasks
    Validating --> Completed: all_sub_tasks_done

    Executing --> Failed: max_steps_reached
    Planning --> Failed: planning_error
    Recovering --> Failed: unrecoverable

    Completed --> Idle: reset()
    Failed --> Idle: reset()

    Completed --> [*]
    Failed --> [*]

    note right of Grounding
        ✅ Anti-hallucination
        checks happen HERE
    end note

    note right of Validating
        🔍 Critic sub-agent
        evaluates HERE
    end note
```

---

### Error Recovery Strategy

```mermaid
flowchart TB
    ERROR["⚠️ Action Failed"]

    CHECK1{"Retry count<br/>< max?"}
    CHECK2{"Network<br/>error?"}
    CHECK3{"Page/DOM<br/>changed?"}
    CHECK4{"LLM API<br/>error?"}
    CHECK5{"Element<br/>stale?"}

    RETRY["🔄 Retry<br/>Same Action"]
    REOBSERVE["📸 Re-observe<br/>Take new screenshot"]
    BACKOFF["⏳ Exponential<br/>Backoff + Retry"]
    REPLAN["📋 Re-plan<br/>Adjust sub-task"]
    MARKFAIL["❌ Mark Task<br/>as Failed"]

    ERROR --> CHECK1
    CHECK1 -->|"No"| MARKFAIL
    CHECK1 -->|"Yes"| CHECK2

    CHECK2 -->|"Yes"| BACKOFF
    CHECK2 -->|"No"| CHECK3

    CHECK3 -->|"Yes"| REOBSERVE
    CHECK3 -->|"No"| CHECK4

    CHECK4 -->|"Yes"| BACKOFF
    CHECK4 -->|"No"| CHECK5

    CHECK5 -->|"Yes"| REOBSERVE
    CHECK5 -->|"No"| REPLAN

    BACKOFF --> RETRY
    RETRY -.-> ERROR
    REOBSERVE -.-> ERROR
    REPLAN -.-> ERROR

    style ERROR fill:#dc2626,stroke:#fff,color:#fff
    style MARKFAIL fill:#991b1b,stroke:#fff,color:#fff
    style RETRY fill:#d97706,stroke:#fff,color:#fff
    style REOBSERVE fill:#2563eb,stroke:#fff,color:#fff
    style BACKOFF fill:#7c3aed,stroke:#fff,color:#fff
    style REPLAN fill:#059669,stroke:#fff,color:#fff
```

---

### API Request/Response Flow

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI Server
    participant Auth as Auth Middleware
    participant Rate as Rate Limiter
    participant Queue as Task Queue
    participant Worker as Background Worker
    participant Agent as BrowserPilot Agent

    Client->>API: POST /api/v1/tasks
    Note right of Client: {"instruction": "..."}
    API->>Auth: Validate API Key
    Auth-->>API: ✅ Authenticated

    API->>Rate: Check rate limit
    Rate-->>API: ✅ Within limits

    API->>Queue: Enqueue task
    Queue-->>API: task_id = "abc-123"
    API-->>Client: 202 Accepted
    Note left of API: {"task_id": "abc-123",<br/>"status": "pending"}

    Queue->>Worker: Dequeue task
    Worker->>Agent: Execute task
    Note over Agent: Running autonomously...

    par Real-time Updates
        Client->>API: GET /api/v1/tasks/abc-123/stream
        loop SSE Events
            Agent-->>API: Step completed
            API-->>Client: event: step_complete
            Note left of API: {"step": 3,<br/>"action": "click",<br/>"screenshot": "url"}
        end
    end

    Agent-->>Worker: TaskResult
    Worker-->>Queue: Mark complete

    Client->>API: GET /api/v1/tasks/abc-123
    API-->>Client: 200 OK
    Note left of API: {"status": "completed",<br/>"result": {...},<br/>"screenshots": [...]}
```

---

### Data Model Relationships

```mermaid
erDiagram
    TASK ||--o{ SUB_TASK : contains
    SUB_TASK ||--o{ ACTION : executes
    ACTION ||--o| DOM_ELEMENT : targets
    ACTION ||--o{ SCREENSHOT : captures
    TASK ||--|| TASK_RESULT : produces

    TASK {
        uuid id PK
        string instruction
        enum status
        datetime created_at
        datetime updated_at
        json config
    }

    SUB_TASK {
        uuid id PK
        uuid task_id FK
        string description
        int order
        enum status
        string completion_criteria
    }

    ACTION {
        uuid id PK
        uuid sub_task_id FK
        enum action_type
        json params
        enum status
        float confidence
        string reasoning
        datetime executed_at
    }

    DOM_ELEMENT {
        int index PK
        string tag
        string text
        json attributes
        float x
        float y
        float width
        float height
        bool is_interactive
        bool is_visible
    }

    SCREENSHOT {
        uuid id PK
        uuid action_id FK
        string file_path
        enum timing
        int width
        int height
        datetime captured_at
    }

    TASK_RESULT {
        uuid id PK
        uuid task_id FK
        bool success
        string summary
        json extracted_data
        float total_time_seconds
        int total_steps
        json errors
    }
```

---

### Token Budget Distribution

```mermaid
pie title Token Budget Per Step (~4,000 tokens)
    "Screenshot Image Tokens" : 1600
    "DOM Context" : 1000
    "System Prompt" : 600
    "Action History" : 600
    "Response" : 200
```

---

### Module Dependency Graph

```mermaid
graph TD
    MAIN["__main__.py<br/>CLI Entry Point"]
    CONFIG["config.py<br/>Settings"]
    LOG["logging.py<br/>Structured Logs"]

    subgraph Agent["agent/"]
        ALOOP["action_loop.py"]
        PLAN["planner.py"]
        CRIT["critic.py"]
        MEM["memory.py"]
        PROM["prompts.py"]
        ST["state.py"]
    end

    subgraph Vision["vision/"]
        SS["screenshot.py"]
        ANN["annotator.py"]
        INTERP["interpreter.py"]
        GRD["grounding.py"]
    end

    subgraph Browser2["browser/"]
        CTRL["controller.py"]
        DOMI["dom_inspector.py"]
        ACT["actions.py"]
        ANTI["anti_detection.py"]
        PROF["profiles.py"]
    end

    subgraph Server["server/"]
        APP["app.py"]
        ROUTES["routes/"]
        MID["middleware.py"]
        SCH["schemas.py"]
        DEP["dependencies.py"]
    end

    subgraph Tools["tools/"]
        BT["browser_tools.py"]
        NT["navigation_tools.py"]
        FT["form_tools.py"]
        ET["extraction_tools.py"]
    end

    subgraph Models["models/"]
        MT["task.py"]
        MA["action.py"]
        MR["result.py"]
        MD["dom.py"]
    end

    subgraph Utils["utils/"]
        UI["image.py"]
        UR["retry.py"]
        URL2["rate_limiter.py"]
        US["sanitizer.py"]
    end

    MAIN --> CONFIG
    MAIN --> LOG
    MAIN --> APP
    MAIN --> ALOOP

    ALOOP --> PLAN
    ALOOP --> CRIT
    ALOOP --> MEM
    ALOOP --> ST
    ALOOP --> PROM

    ALOOP --> SS
    ALOOP --> ANN
    ALOOP --> INTERP
    ALOOP --> GRD

    ALOOP --> CTRL
    CTRL --> DOMI
    CTRL --> ACT
    CTRL --> ANTI
    CTRL --> PROF

    APP --> ROUTES
    APP --> MID
    APP --> DEP

    ROUTES --> SCH
    DEP --> CONFIG

    BT --> ACT
    NT --> CTRL
    FT --> ACT
    ET --> DOMI

    INTERP --> UI
    INTERP --> UR
    INTERP --> URL2
    GRD --> DOMI

    style Agent fill:#1e1b4b,stroke:#8b5cf6,color:#c9d1d9
    style Vision fill:#4c1d95,stroke:#a78bfa,color:#c9d1d9
    style Browser2 fill:#064e3b,stroke:#34d399,color:#c9d1d9
    style Server fill:#0c4a6e,stroke:#38bdf8,color:#c9d1d9
    style Tools fill:#713f12,stroke:#fbbf24,color:#c9d1d9
    style Models fill:#1e3a5f,stroke:#60a5fa,color:#c9d1d9
    style Utils fill:#44403c,stroke:#a8a29e,color:#c9d1d9
```

---

### Browser Automation Layer

```mermaid
flowchart TB
    subgraph BrowserEngine["🎭 Playwright Browser Engine"]
        direction TB
        LAUNCH["Launch Browser<br/>Chromium / Firefox / WebKit"]
        CONTEXT["Create Context<br/>Viewport, UA, Proxy"]
        PAGE["New Page<br/>Navigation ready"]

        LAUNCH --> CONTEXT --> PAGE
    end

    subgraph Actions2["⚡ Available Actions"]
        direction LR
        CLICK2["🖱️ Click"]
        TYPE2["⌨️ Type"]
        SCROLL2["📜 Scroll"]
        NAV["🔗 Navigate"]
        SELECT["📋 Select"]
        HOVER2["👆 Hover"]
        WAIT2["⏳ Wait"]
        UPLOAD["📁 Upload"]
    end

    subgraph DOM3["🌳 DOM Inspector"]
        TREE["Parse DOM Tree"]
        FILTER2["Filter Elements"]
        SERIALIZE["Serialize to JSON"]
        A11Y["Accessibility Tree"]
    end

    subgraph Stealth["🛡️ Anti-Detection"]
        UA["User-Agent Rotation"]
        VP["Viewport Randomization"]
        MOUSE["Human-like Mouse"]
        TYPING["Random Type Delays"]
        FLAGS["WebDriver Flag Mask"]
    end

    PAGE --> Actions2
    PAGE --> DOM3
    CONTEXT --> Stealth

    style BrowserEngine fill:#0f172a,stroke:#10b981,color:#e2e8f0
    style Actions2 fill:#1e293b,stroke:#38bdf8,color:#e2e8f0
    style DOM3 fill:#1e293b,stroke:#8b5cf6,color:#e2e8f0
    style Stealth fill:#1e293b,stroke:#f97316,color:#e2e8f0
```

---

### Critic Validation Workflow

```mermaid
flowchart LR
    subgraph CriticInput["📥 Critic Receives"]
        ST_DESC["Sub-Task<br/>Description"]
        BEFORE_STATE["Before<br/>State"]
        AFTER_STATE["After<br/>State"]
        ACTION_LOG["Action<br/>History"]
    end

    subgraph CriticAnalysis["🔍 Analysis"]
        COMPARE_DOM["Compare DOM<br/>Before vs After"]
        CHECK_URL["Check URL<br/>Changed?"]
        CHECK_CONTENT["Check Content<br/>Matches criteria?"]
        CHECK_ERRORS["Check for<br/>Error messages?"]
    end

    subgraph CriticLLM["🧠 LLM Evaluation"]
        BUILD_PROMPT2["Build Evidence<br/>Prompt"]
        ASK_LLM["Ask GPT-4o:<br/>'Is the task done?'"]
    end

    subgraph CriticOutput["📤 Verdict"]
        PASS_V["✅ PASS<br/>Task complete"]
        FAIL_V["❌ FAIL<br/>Continue execution"]
        PARTIAL_V["⚠️ PARTIAL<br/>Adjust approach"]
    end

    ST_DESC --> COMPARE_DOM
    BEFORE_STATE --> COMPARE_DOM
    AFTER_STATE --> COMPARE_DOM
    ACTION_LOG --> CHECK_ERRORS

    COMPARE_DOM --> BUILD_PROMPT2
    CHECK_URL --> BUILD_PROMPT2
    CHECK_CONTENT --> BUILD_PROMPT2
    CHECK_ERRORS --> BUILD_PROMPT2

    BUILD_PROMPT2 --> ASK_LLM

    ASK_LLM --> PASS_V
    ASK_LLM --> FAIL_V
    ASK_LLM --> PARTIAL_V

    style CriticInput fill:#1e1b4b,stroke:#8b5cf6,color:#c9d1d9
    style CriticAnalysis fill:#0f172a,stroke:#38bdf8,color:#c9d1d9
    style CriticLLM fill:#4c1d95,stroke:#f97316,color:#c9d1d9
    style CriticOutput fill:#064e3b,stroke:#10b981,color:#c9d1d9
```

---

### Memory & Context Management

```mermaid
flowchart TB
    subgraph ContextWindow["🧠 LLM Context Window (128K tokens)"]
        SYS["System Prompt<br/>~600 tokens"]
        CURR_SS["Current Screenshot<br/>~1,600 tokens"]
        CURR_DOM["Current DOM State<br/>~1,000 tokens"]

        subgraph SlidingWindow["📜 Sliding Window History"]
            H1["Step N-4: click #3 → success"]
            H2["Step N-3: type 'query' → success"]
            H3["Step N-2: click #12 → success"]
            H4["Step N-1: scroll down → success"]
        end

        subgraph Summarized["📋 Summarized History"]
            SUM["Steps 1 to N-5:<br/>'Navigated to Google,<br/>searched for AI startups,<br/>opened first result'"]
        end

        TASK_CTX["Task Context<br/>Current sub-task + plan"]
    end

    FULL["Full History<br/>(stored, not sent)"]

    FULL -->|"Summarize old steps"| Summarized
    FULL -->|"Keep recent steps"| SlidingWindow

    style ContextWindow fill:#0f172a,stroke:#8b5cf6,color:#c9d1d9
    style SlidingWindow fill:#1e1b4b,stroke:#a78bfa,color:#c9d1d9
    style Summarized fill:#312e81,stroke:#c4b5fd,color:#c9d1d9
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (GPT-4o access)

### Installation

```bash
# Clone the repository
git clone https://github.com/chirag127/BrowserPilot.git
cd BrowserPilot

# Install dependencies with uv
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Create your .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### First Run

```bash
# Run a simple task
uv run browserpilot run "Go to google.com and search for 'BrowserPilot'"

# Start the API server
uv run browserpilot serve --port 8000

# Check task status
uv run browserpilot status <task_id>
```

---

## 📖 Usage

### CLI Mode

```bash
# Simple navigation
uv run browserpilot run "Navigate to github.com and find the trending repositories"

# Form filling
uv run browserpilot run "Go to example.com/contact and fill the form with name: John, email: john@example.com"

# Data extraction
uv run browserpilot run "Go to news.ycombinator.com and extract the top 10 post titles"

# Complex multi-step task
uv run browserpilot run "Research the top 5 AI startups of 2025, find their funding amounts, and save the data as a JSON file"

# With options
uv run browserpilot run "Search Google for 'Python tutorials'" \
  --max-steps 30 \
  --headless false \
  --screenshot-dir ./my-screenshots
```

### API Mode

```bash
# Start the server
uv run browserpilot serve --host 0.0.0.0 --port 8000

# Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"instruction": "Search Google for BrowserPilot"}'

# Get task status
curl http://localhost:8000/api/v1/tasks/<task_id> \
  -H "X-API-Key: your-api-key"

# Stream live updates (SSE)
curl http://localhost:8000/api/v1/tasks/<task_id>/stream \
  -H "X-API-Key: your-api-key"
```

### Python SDK

```python
import asyncio
from browser_pilot import BrowserPilot

async def main():
    pilot = BrowserPilot(
        model="gpt-4o",
        headless=True,
        max_steps=30,
    )

    result = await pilot.run(
        "Go to github.com/trending and extract "
        "the top 5 repository names and descriptions"
    )

    print(f"Success: {result.success}")
    print(f"Steps taken: {result.total_steps}")
    print(f"Extracted data: {result.extracted_data}")

    for screenshot in result.screenshots:
        print(f"Screenshot: {screenshot}")

asyncio.run(main())
```

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/tasks` | Create a new task |
| `GET` | `/api/v1/tasks/{id}` | Get task status & result |
| `GET` | `/api/v1/tasks` | List all tasks (paginated) |
| `DELETE` | `/api/v1/tasks/{id}` | Cancel a running task |
| `GET` | `/api/v1/tasks/{id}/stream` | SSE live updates |
| `WS` | `/api/v1/ws` | WebSocket connection |
| `GET` | `/api/v1/tasks/{id}/screenshots` | Get screenshots |
| `GET` | `/api/v1/health` | Health check |

### Create Task Request

```json
{
  "instruction": "Search Google for 'AI news' and extract the top 5 results",
  "config": {
    "max_steps": 30,
    "headless": true,
    "browser_type": "chromium",
    "screenshot_on_action": true
  }
}
```

### Task Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "instruction": "Search Google for 'AI news'...",
  "status": "completed",
  "result": {
    "success": true,
    "summary": "Successfully extracted top 5 AI news results",
    "extracted_data": {
      "results": [
        {"title": "...", "url": "...", "snippet": "..."},
      ]
    },
    "total_time_seconds": 45.2,
    "total_steps": 8,
    "errors": []
  },
  "screenshots": [
    "/api/v1/tasks/550e.../screenshots/step_1.png",
    "/api/v1/tasks/550e.../screenshots/step_2.png"
  ],
  "created_at": "2026-03-29T12:00:00Z",
  "updated_at": "2026-03-29T12:00:45Z"
}
```

---

## 🔧 How It Works

### The Core Loop: Observe → Decide → Act

BrowserPilot operates on a continuous loop that mirrors how a
human would interact with a web browser:

```mermaid
graph LR
    O["👁️ OBSERVE<br/>Screenshot + DOM"]
    D["🧠 DECIDE<br/>GPT-4o Vision"]
    V["✅ VERIFY<br/>Ground in DOM"]
    A["⚡ ACT<br/>Playwright"]

    O --> D --> V --> A --> O

    style O fill:#0ea5e9,stroke:#fff,color:#fff
    style D fill:#8b5cf6,stroke:#fff,color:#fff
    style V fill:#10b981,stroke:#fff,color:#fff
    style A fill:#f97316,stroke:#fff,color:#fff
```

1. **OBSERVE**: Take a screenshot of the current page and extract
   the DOM tree. Interactive elements are numbered and overlaid on
   the screenshot (Set-of-Marks technique).

2. **DECIDE**: Send the annotated screenshot + DOM context + task
   history to GPT-4o Vision. The LLM analyzes the page and proposes
   the next action (e.g., "click element #7" or "type 'hello'
   into element #3").

3. **VERIFY**: Before executing, the Grounding module verifies
   the proposed action against the live DOM state. This prevents
   the LLM from "hallucinating" actions on elements that don't
   exist, aren't visible, or have changed since the screenshot.

4. **ACT**: Execute the verified action using Playwright. Record
   the before/after state. Update the action history.

5. **VALIDATE**: After each sub-task boundary, the Critic sub-agent
   evaluates whether the sub-task has been completed by comparing
   the before/after states and checking explicit completion criteria.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | _required_ | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Model to use for vision |
| `BROWSER_HEADLESS` | `true` | Run browser headlessly |
| `BROWSER_TYPE` | `chromium` | Browser engine |
| `MAX_STEPS` | `50` | Max steps per task |
| `STEP_TIMEOUT` | `120` | Seconds per step timeout |
| `MAX_FAILURES` | `5` | Max consecutive failures |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `API_KEY` | _none_ | API authentication key |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `SCREENSHOT_DIR` | `./screenshots` | Screenshot save path |
| `RECORDING_DIR` | `./recordings` | Video recording path |

### Configuration File

```python
# Custom configuration via Python
from browser_pilot.config import Settings

settings = Settings(
    openai_model="gpt-4o",
    browser_headless=False,
    max_steps=30,
    step_timeout=60,
    max_failures=3,
)
```

---

## 🧪 Testing

### Test Architecture

```mermaid
flowchart TB
    subgraph Unit_Tests["🔬 Unit Tests"]
        UT1["Planner Logic"]
        UT2["Critic Logic"]
        UT3["State Machine"]
        UT4["DOM Inspector"]
        UT5["Grounding Checks"]
        UT6["Memory Manager"]
        UT7["Input Sanitizer"]
    end

    subgraph Integration_Tests["🔗 Integration Tests"]
        IT1["Vision Pipeline<br/>Screenshot → Action"]
        IT2["Browser Actions<br/>Click, Type, Scroll"]
        IT3["API Server<br/>Request/Response"]
        IT4["Agent E2E<br/>Component interactions"]
    end

    subgraph E2E_Tests2["🌐 E2E Tests"]
        ET1["Form Filling<br/>on test pages"]
        ET2["Multi-page<br/>Navigation"]
        ET3["Data Extraction<br/>Accuracy"]
        ET4["Complex Multi-step<br/>Tasks"]
    end

    subgraph Infra2["🛠️ Test Infrastructure"]
        MOCK_LLM["Mock LLM<br/>Responses"]
        TEST_PAGES["Local HTML<br/>Test Fixtures"]
        FIXTURES["Pytest<br/>Fixtures"]
        SNAPSHOTS["Snapshot<br/>Testing"]
    end

    Infra2 --> Unit_Tests
    Infra2 --> Integration_Tests
    Infra2 --> E2E_Tests2

    style Unit_Tests fill:#0c4a6e,stroke:#38bdf8,color:#e2e8f0
    style Integration_Tests fill:#4c1d95,stroke:#a78bfa,color:#e2e8f0
    style E2E_Tests2 fill:#064e3b,stroke:#34d399,color:#e2e8f0
    style Infra2 fill:#1e293b,stroke:#94a3b8,color:#e2e8f0
```

### Running Tests

```bash
# All tests
uv run pytest -v

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests
uv run pytest tests/integration/ -v

# E2E tests (requires browser)
uv run pytest tests/e2e/ -v

# With coverage
uv run pytest --cov=browser_pilot --cov-report=html

# Specific test
uv run pytest tests/unit/test_planner.py -v
```

---

## 🔒 Security

### Safety Measures

```mermaid
flowchart TB
    subgraph Input_Security["🛡️ Input Security"]
        URL_VALID["URL Allowlist<br/>Validation"]
        SANITIZE_INPUT["Input<br/>Sanitization"]
        INJECTION_PREV["JS Injection<br/>Prevention"]
    end

    subgraph Runtime_Security["🔐 Runtime Security"]
        SANDBOXED["Sandboxed<br/>Browser"]
        TIMEOUT_GUARD["Timeout<br/>Guards"]
        ACTION_LIMIT["Action<br/>Rate Limits"]
        COST_CAP["Cost<br/>Budget Caps"]
    end

    subgraph API_Security["🔑 API Security"]
        API_KEY_AUTH["API Key<br/>Authentication"]
        RATE_LIMIT["Per-IP<br/>Rate Limiting"]
        CORS_POLICY["CORS<br/>Policy"]
        INPUT_VALID2["Request<br/>Validation"]
    end

    style Input_Security fill:#1e293b,stroke:#ef4444,color:#e2e8f0
    style Runtime_Security fill:#1e293b,stroke:#f97316,color:#e2e8f0
    style API_Security fill:#1e293b,stroke:#10b981,color:#e2e8f0
```

- **Never run with elevated privileges** — always use a non-root user
- **URL allowlists** — restrict which domains the agent can visit
- **Action budgets** — limit total API cost per task
- **Timeout guards** — prevent infinite loops
- **Input sanitization** — prevent prompt injection attacks
- **Secrets in `.env`** — never hardcoded

---

## 📂 Project Structure

```
BrowserPilot/
├── .github/workflows/        # CI/CD pipelines
├── src/browser_pilot/
│   ├── agent/                 # 🧠 Core agent logic
│   │   ├── action_loop.py     #    Main observe-decide-act loop
│   │   ├── planner.py         #    Task decomposition
│   │   ├── critic.py          #    Completion validation
│   │   ├── memory.py          #    Context management
│   │   ├── prompts.py         #    LLM prompt templates
│   │   └── state.py           #    Agent state machine
│   ├── vision/                # 👁️ Vision pipeline
│   │   ├── screenshot.py      #    Screenshot capture
│   │   ├── annotator.py       #    DOM element overlay
│   │   ├── interpreter.py     #    GPT-4o vision analysis
│   │   └── grounding.py       #    Anti-hallucination checks
│   ├── browser/               # 🌐 Browser automation
│   │   ├── controller.py      #    Playwright lifecycle
│   │   ├── dom_inspector.py   #    DOM tree extraction
│   │   ├── actions.py         #    Click, type, scroll, etc.
│   │   ├── anti_detection.py  #    Stealth features
│   │   └── profiles.py        #    Browser profiles
│   ├── server/                # 🖥️ FastAPI server
│   │   ├── app.py             #    Application factory
│   │   ├── routes/            #    API endpoints
│   │   ├── middleware.py      #    Auth & rate limiting
│   │   └── schemas.py         #    Request/response models
│   ├── tools/                 # 🛠️ LangChain tools
│   ├── models/                # 📦 Data models
│   └── utils/                 # 🔧 Utilities
├── tests/                     # 🧪 Test suites
├── examples/                  # 📝 Usage examples
├── docs/                      # 📚 Documentation
├── .env.example               # Environment template
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

---

## 🔄 CI/CD Pipeline

```mermaid
flowchart LR
    PUSH["📤 Git Push"]
    LINT2["🔍 Ruff Lint<br/>& Format"]
    TYPE2["📝 Type Check"]
    UNIT3["🔬 Unit Tests"]
    INT3["🔗 Integration<br/>Tests"]
    E2E3["🌐 E2E Tests"]
    BUILD2["📦 Build<br/>Package"]
    COV2["📊 Coverage<br/>Report"]

    PUSH --> LINT2 --> TYPE2 --> UNIT3
    UNIT3 --> INT3 --> E2E3
    E2E3 --> BUILD2 --> COV2

    TAG["🏷️ Tag Push<br/>v*.*.*"]
    RELEASE["📋 GitHub<br/>Release"]
    PYPI["📦 PyPI<br/>Publish"]
    DOCKER["🐳 Docker<br/>Image"]

    TAG --> RELEASE
    TAG --> PYPI
    TAG --> DOCKER

    style PUSH fill:#3b82f6,stroke:#fff,color:#fff
    style TAG fill:#8b5cf6,stroke:#fff,color:#fff
```

All test jobs use `continue-on-error: true` so every test
suite runs regardless of individual failures.

---

## 🤝 Contributing

We welcome contributions! Please see the following workflow:

```mermaid
gitgraph
    commit id: "main"
    branch feature/my-feature
    checkout feature/my-feature
    commit id: "feat: add feature"
    commit id: "test: add tests"
    commit id: "docs: update README"
    checkout main
    merge feature/my-feature
    commit id: "release: v1.0.0" tag: "v1.0.0"
```

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing`)
3. **Write tests** first (TDD approach)
4. **Implement** the feature
5. **Run** linting: `uv run ruff check .`
6. **Run** tests: `uv run pytest -v`
7. **Commit** with conventional commits
8. **Push** and open a Pull Request

### Commit Convention

| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `test:` | Tests |
| `refactor:` | Code refactoring |
| `perf:` | Performance |
| `ci:` | CI/CD changes |
| `chore:` | Maintenance |

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE)
for details.

---

## 🙏 Acknowledgments

- [browser-use](https://github.com/browser-use/browser-use) —
  Core agentic browser framework
- [Playwright](https://playwright.dev/) — Browser automation
- [LangChain](https://www.langchain.com/) — LLM orchestration
- [OpenAI](https://openai.com/) — GPT-4o vision model
- [FastAPI](https://fastapi.tiangolo.com/) — API framework

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/chirag127">Chirag Singhal</a>
</p>
