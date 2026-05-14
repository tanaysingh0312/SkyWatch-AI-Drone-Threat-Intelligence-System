# 🚁 Drone Security Analyst Agent (DSAA)

> **FlytBase AI Engineer Assignment** | Candidate: Tanay Singh

A production-grade prototype of an AI-powered drone security monitoring system. The agent processes simulated drone telemetry and video frames in real-time, using a Vision Language Model (LLaVA) for multimodal perception and a LangChain ReAct agent for security reasoning — all surfaced through a live WebSocket dashboard.

---

## 📋 Feature Specification

### Value Proposition
The Drone Security Analyst Agent enhances physical security for property owners by replacing passive camera systems with an active AI analyst that monitors continuously, reasons about events, and surfaces only what matters.

### Key Requirements
1. **Real-Time Perception** — The system must ingest drone telemetry (position, altitude, heading) and video frames simultaneously, analysing each frame with a VLM to produce structured, timestamped observations.
2. **Intelligent Alerting** — A deterministic rule engine must classify events from `NONE` to `CRITICAL`, triggering immediate alerts for high-risk conditions (e.g., midnight loitering, perimeter breach) without waiting for agent reasoning.
3. **Queryable History** — Every observation must be indexed in a vector store with rich metadata so operators can ask natural-language questions like *"What vehicles were seen at the main gate today?"* and receive cited, accurate answers.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        7-LAYER PIPELINE                         │
│                                                                 │
│  1. SIMULATOR ──► 2. VLM (LLaVA) ──► 3. CHROMADB INDEX        │
│                                              │                  │
│  7. REACT UI ◄── 6. FASTAPI/WS ◄── 5. LANGCHAIN AGENT         │
│                                              │                  │
│                              4. ALERT ENGINE (Rule-Based)       │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Component | Role |
|---|---|---|
| Simulator | `backend/simulator.py` | Emits synthetic telemetry + frame descriptions on a configurable tick |
| VLM | Ollama LLaVA-7B | Converts frame text/image to structured natural-language observations |
| Index | ChromaDB | Stores every frame as a vector with telemetry metadata for semantic search |
| Alert Engine | `backend/alert_engine.py` | 8 deterministic rules; produces NONE → LOW → MEDIUM → HIGH → CRITICAL alerts |
| Agent | LangChain ReAct + Qwen-8B | Slow-path reasoning with 4 custom tools for pattern detection and event logging |
| API | FastAPI + WebSocket | Streams live events to the UI; exposes REST endpoints for history and Q&A |
| UI | React + Vite | Live feed, alert panel, event log, analytics, and AI Q&A interface |

### Design Rationale
- **Decoupled fast/slow paths:** The rule engine provides instant deterministic alerts while the LLM agent performs deeper pattern analysis asynchronously — avoiding latency for time-critical events.
- **Swappable VLM layer:** LLaVA can be replaced with Claude Vision or GPT-4V without touching the indexing or reasoning layers.
- **Full auditability:** Every frame is stored in ChromaDB, making the entire session history searchable and auditable through the Q&A interface.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Pydantic, Uvicorn |
| AI / Reasoning | LangChain ReAct, Ollama (LLaVA-7B, Qwen2-7B) |
| Vector Store | ChromaDB |
| Frontend | React 18, Vite, Vanilla CSS, Lucide Icons |
| Testing | Pytest (18 test cases) |

---

## 🚀 Quick Start

### Prerequisites

1. **Ollama** — Install from [ollama.com](https://ollama.com) and pull the required models:
   ```bash
   ollama pull llava
   ollama pull qwen2:7b
   ```
2. **Python 3.10+**
3. **Node.js 18+**

### 1 · Clone & Configure

```bash
git clone <your-private-repo-url>
cd drone-security-analyst-agent
cp .env.example .env
# Edit .env if needed (default values work for local Ollama)
```

### 2 · Backend

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
# API available at http://localhost:8000
```

### 3 · Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

### 4 · One-Click Start (Windows)

```bash
start_drone_system.bat
```

### 5 · Start a Mission

Open the dashboard → click **START MISSION** → the simulator begins emitting frames and the agent starts processing in real-time.

---

## 📂 Project Structure

```
drone-security-analyst-agent/
├── backend/
│   ├── main.py               # FastAPI app, WebSocket server
│   ├── agent.py              # LangChain ReAct agent + 4 custom tools
│   ├── alert_engine.py       # 8 deterministic security rules
│   ├── simulator.py          # Synthetic telemetry + frame generator
│   ├── indexer.py            # ChromaDB ingestion pipeline
│   └── qa.py                 # Q&A retrieval chain
├── frontend/
│   ├── src/
│   │   ├── components/       # Dashboard, AlertPanel, EventLog, Analytics, QAAgent
│   │   └── App.jsx
│   └── package.json
├── chroma_db/                # Persisted vector store (auto-created)
├── docs/
│   ├── architecture_diagram.png
│   └── feature_spec.md
├── tests/
│   └── test_*.py             # 18 pytest cases
├── events.jsonl              # Sample simulated event data
├── requirements.txt
├── .env.example
├── start_drone_system.bat
└── README.md
```

---

## 🧪 Testing

The project includes **18 pytest cases** across all core modules. Tests run in `text_fallback` mode — no GPU or running Ollama instance required.

```bash
pytest tests/ -v
```

### Test Coverage

| Module | Test Cases |
|---|---|
| Simulator | Frame generation, telemetry emission, tick rate |
| Alert Engine | All 8 rules (e.g., midnight trigger, perimeter breach) |
| Indexer | ChromaDB ingestion, metadata filtering, query results |
| Agent Tools | Pattern detection, event logging, anomaly search |
| API Endpoints | REST routes, WebSocket handshake, Q&A response format |

---

## 🔍 Example Outputs

### Frame Observation (LLaVA)
```
[01:00:05Z | WAREHOUSE_ENTRANCE | UAV-7A | Alt: 8.0m]
Thermal signature confirmed as a large stray dog. Animal is
scavenging near trash receptacles. No security threat.
```

### Security Alerts
```
[CRITICAL] Person loitering at main gate at midnight.       — RULE_MIDNIGHT_MOTION
[HIGH]     Subject in flight. Tracking active.              — RULE_TRACKING_ACTIVE
[MEDIUM]   Unexpected thermal signature detected.           — RULE_THERMAL_ANOMALY
```

### Event Log Entry
```
Time: 01:00:05Z | Location: WAREHOUSE_ENTRANCE | Objects: dog
Threat: LOW | Agent Summary: Confirmed wildlife. False alarm for intrusion.
```

### Q&A Agent
```
User:  How many vehicles today?
Agent: I have detected 9 vehicle events in this session.
       Notable entries include frame_001 (Ford F150) and
       frame_006 (Delivery Van).
Sources: frame_session001_001, frame_session001_006, frame_session001_086
```

---

## 🤖 AI Integration & Workflow Impact

The development of the DSAA prototype utilized a state-of-the-art AI-assisted workflow, which significantly accelerated the engineering timeline from conceptualization to a production-grade dashboard.

| AI Tool | Integration Role | Impact on Workflow |
| :--- | :--- | :--- |
| **Antigravity (Coding Agent)** | Primary implementation partner for Backend (FastAPI), Vector DB (ChromaDB), and Frontend (React). | Reduced "boilerplate" time by 80%. Enabled rapid iteration on complex WebSocket data mapping and UI redesigns. |
| **Ollama (LLaVA-7B)** | Perceptual Brain. Processed visual frames to generate natural language descriptions. | Eliminated the need for manual labeling. Allowed the agent to "see" and "describe" scenes with human-like nuance. |
| **Ollama (Qwen3:8b)** | Reasoning Brain. Powered the LangChain/LangGraph ReAct agent. | Enabled complex multi-step reasoning (e.g., comparing current observations with history) using natural language tools. |
| **Claude (Architectural Review)** | Design and logic validation. | Used to stress-test the 7-Layer Pipeline architecture and refine the deterministic alert rule-set for maximum accuracy. |

---

## 📈 Analytics

The Analytics dashboard tracks:
- **Total Frames Processed** across the session
- **Alerts Fired** (breakdown by severity)
- **Critical Events** count
- **Threat Timeline** — 60-minute rolling chart of threat levels
- **Object Frequency** — bar chart of detected object categories
- **Alert Distribution** — gauge showing the session's overall security posture

---

## 🔮 Future Improvements

Given more time, the following enhancements would meaningfully improve the system:

- **Higher-resolution VLM** — Replace LLaVA-7B with a larger model (e.g., Claude Vision or LLaVA-34B) for more accurate object detection in low-light or cluttered frames.
- **Persistent session storage** — Move from in-memory state to PostgreSQL so sessions survive server restarts and can be reviewed days later.
- **Video summarisation** — Use an LLM to auto-generate a one-paragraph shift report at the end of each mission.
- **Multi-drone support** — Extend the WebSocket layer to handle concurrent UAV feeds with independent agent instances per drone.
- **Active learning feedback loop** — Allow operators to correct false positives/negatives, using that feedback to fine-tune alert rule thresholds over time.

---

## 📄 License

This project was built as part of the FlytBase AI Engineer Assignment. All code is original work by Tanay Singh.