# SkyWatch-AI — Real-Time Drone Threat Intelligence System


<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-FF6B35?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-LLaVA--7B-black?style=for-the-badge)

**An AI-powered real-time drone surveillance system with Vision Language Models, semantic frame indexing, deterministic alerting, and agentic security reasoning.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Demo](#-demo) • [Tech Stack](#-tech-stack) • [Testing](#-testing)

</div>

---

## 🔍 What is SkyWatch AI?

SkyWatch AI is a production-grade prototype of an autonomous drone security analyst. It replaces passive CCTV systems with an active AI pipeline that:

- 👁️ **Sees** — processes drone video frames through LLaVA-7B (Vision Language Model) to generate natural language descriptions
- 🧠 **Reasons** — a LangChain ReAct agent analyses patterns, cross-references history, and determines threat level
- ⚡ **Alerts** — a deterministic rule engine fires instant alerts (CRITICAL → LOW) without waiting for LLM latency
- 🗃️ **Remembers** — every frame is semantically indexed in ChromaDB, queryable via natural language
- 📡 **Streams** — a FastAPI WebSocket server pushes live events to a real-time React dashboard

---

## 🚀 Quick Start

**1. Dashboard — Live Feed with LLaVA-7B Real-Time Frame Analysis**

 <img width="1920" height="922" alt="Screenshot 2026-05-14 140038" src="https://github.com/user-attachments/assets/f0719e37-2987-49df-912d-d7d5bce9ed03" />

**2. Event History — Security Event Log with Threat Classification**

<img width="1919" height="922" alt="Screenshot 2026-05-14 140155" src="https://github.com/user-attachments/assets/6ca7ef66-6c90-4282-96c7-19d77ca9de2c" />

**3. Analytics — Threat Timeline, Alert Distribution & Session Metrics**

<img width="1919" height="915" alt="Screenshot 2026-05-14 140230" src="https://github.com/user-attachments/assets/010c0ef4-1561-4689-8619-b51f8805d341" />

**4. Q&A Agent — Natural Language Surveillance History Query Interface**

<img width="1919" height="918" alt="Screenshot 2026-05-14 140456" src="https://github.com/user-attachments/assets/14297a3d-2858-4189-b6e5-30796d2040b3" />

## ✨ Features

- 🎥 **Real-Time Frame Processing** — simulated drone camera feed processed at configurable tick rate
- 🤖 **VLM Perception Layer** — LLaVA-7B converts visual frames into structured security observations
- 🚨 **8 Deterministic Alert Rules** — instant classification from `NONE` → `LOW` → `MEDIUM` → `HIGH` → `CRITICAL`
- 🧩 **LangChain ReAct Agent** — 4 custom tools for pattern detection, history search, and event logging
- 🗂️ **Semantic Frame Index** — ChromaDB stores every frame with rich metadata for vector search
- 💬 **Natural Language Q&A** — ask "What vehicles were seen at the main gate today?" and get cited answers
- 📊 **Analytics Dashboard** — threat timeline, object frequency charts, alert distribution gauge
- ⚡ **WebSocket Live Feed** — sub-second event streaming from backend to React UI
- 🧪 **18 Pytest Cases** — full test suite runnable without GPU via text fallback mode

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      7-LAYER PIPELINE                           │
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
| VLM | Ollama LLaVA-7B | Converts frames to structured natural-language observations |
| Index | ChromaDB | Stores every frame as a vector with telemetry metadata for semantic search |
| Alert Engine | `backend/alert_engine.py` | 8 deterministic rules producing NONE → CRITICAL alerts instantly |
| Agent | LangChain ReAct + Qwen3:8b | Slow-path reasoning with 4 custom tools for pattern detection |
| API | FastAPI + WebSocket | Streams live events to the UI; exposes REST endpoints for history and Q&A |
| UI | React + Vite | Live feed, alert panel, event log, analytics, and AI Q&A interface |

### Design Decisions

- **Decoupled fast/slow paths** — The rule engine provides instant deterministic alerts while the LLM agent performs deeper pattern analysis asynchronously, avoiding latency for time-critical events
- **Swappable VLM layer** — LLaVA can be replaced with Claude Vision or GPT-4V without touching the indexing or reasoning layers
- **Full auditability** — Every frame is stored in ChromaDB, making the entire session history searchable and auditable

---



### Prerequisites

**1. Ollama** — Install from [ollama.com](https://ollama.com) then pull models:
```bash
ollama pull llava
ollama pull qwen3:8b
```

**2. Python 3.10+**

**3. Node.js 18+**

---

### Installation

```bash
# Clone the repo
git clone https://github.com/tanaysingh0312/SkyWatch-AI-Drone-Threat-Intelligence-System.git
cd sentinel-ai-drone-security

# Copy environment config
cp .env.example .env
```

### Backend
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
# → http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### One-Click Start (Windows)
```bash
start_drone_system.bat
```

Open the dashboard → click **START MISSION** → the simulator begins emitting frames and the agent starts processing in real-time.

---

## 📂 Project Structure

```
sentinel-ai-drone-security/
├── backend/
│   ├── main.py               # FastAPI app, WebSocket server
│   ├── agent.py              # LangChain ReAct agent + 4 custom tools
│   ├── alert_engine.py       # 8 deterministic security rules
│   ├── simulator.py          # Synthetic telemetry + frame generator
│   ├── indexer.py            # ChromaDB ingestion pipeline
│   └── qa.py                 # Q&A retrieval chain
├── frontend/
│   ├── src/
│   │   ├── components/       # LiveFeed, AlertPanel, EventLog, Analytics, QAAgent
│   │   └── App.jsx
│   └── package.json
├── tests/
│   └── test_*.py             # 18 pytest cases
├── docs/
│   ├── architecture_diagram.png
│   └── feature_spec.md
├── chroma_db/                # Persisted vector store (auto-created, gitignored)
├── events.jsonl              # Sample simulated event data
├── requirements.txt
├── .env.example
├── start_drone_system.bat
└── README.md
```

---

## 🧪 Testing

18 pytest cases across all core modules. Runs in `text_fallback` mode — no GPU or Ollama required.

```bash
pytest tests/ -v
```

| Module | Test Cases |
|---|---|
| Simulator | Frame generation, telemetry emission, tick rate |
| Alert Engine | All 8 rules (midnight trigger, perimeter breach, repeat vehicle) |
| Indexer | ChromaDB ingestion, metadata filtering, query results |
| Agent Tools | Pattern detection, event logging, anomaly search |
| API Endpoints | REST routes, WebSocket handshake, Q&A response format |

---

## 🔍 Example Outputs

**Frame Observation (LLaVA)**
```
[01:00:05Z | WAREHOUSE_ENTRANCE | Alt: 8.0m]
A person in dark clothing is standing near the main gate.
No visible ID. Loitering for over 3 minutes.
```

**Security Alerts**
```
[CRITICAL] Person loitering at main gate at midnight.    — RULE_MIDNIGHT_MOTION
[HIGH]     Unknown vehicle — 3rd entry today.            — RULE_REPEAT_VEHICLE
[MEDIUM]   Unexpected thermal signature detected.        — RULE_THERMAL_ANOMALY
```

**Q&A Agent**
```
User:  How many vehicles today?
Agent: 9 vehicle events detected this session.
       Notable: frame_001 (Ford F150, 3 visits) and frame_006 (Delivery Van).
Sources: frame_session001_001, frame_session001_006, frame_session001_086
```

---

## 📊 Tech Stack

| Category | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Pydantic, Uvicorn |
| AI / Reasoning | LangChain ReAct, Ollama (LLaVA-7B, Qwen3:8b) |
| Vector Store | ChromaDB |
| Frontend | React 18, Vite, Vanilla CSS, Lucide Icons, Recharts |
| Testing | Pytest (18 test cases) |

---

## 🔮 Future Improvements

- **Higher-resolution VLM** — Replace LLaVA-7B with LLaVA-34B or Claude Vision for better low-light accuracy
- **Persistent session storage** — Move from in-memory state to PostgreSQL for multi-day session review
- **Video summarisation** — Auto-generate a shift report at the end of each mission
- **Multi-drone support** — Extend WebSocket layer for concurrent UAV feeds with independent agent instances
- **Active learning loop** — Operator feedback on false positives used to fine-tune alert thresholds

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

## 👨‍💻 Author

<img src="https://github.com/tanaysingh0312.png" width="100" style="border-radius: 50%"/>

### Tanay Singh
**AI/ML Engineer | B.Tech CSE (AI/ML) — SPSU Udaipur**

*Building production AI systems with LangChain, FastAPI, and Vision Language Models*

[![GitHub](https://img.shields.io/badge/GitHub-tanaysingh0312-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tanaysingh0312)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-stanay657-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/stanay657)
[![Email](https://img.shields.io/badge/Email-stanay657@gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:stanay657@gmail.com)

---

*If you found this project useful, drop a ⭐ — it helps others discover it.*

</div>
