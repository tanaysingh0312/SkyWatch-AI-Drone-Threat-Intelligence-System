# Drone Security Analyst Agent — Feature Specification

## 1. Overview
The Drone Security Analyst Agent is a prototype system designed to demonstrate how a docked drone can autonomously monitor a property, analyze visual data using Multimodal Large Language Models (VLM), and reason about security threats using an agentic framework.

## 2. Key Features

### 2.1 Visual Perception Layer (VLM)
- **Ollama LLaVA-7B Integration:** Processes raw camera frames into detailed natural language descriptions.
- **Context-Aware Prompts:** Injects drone telemetry (location, time) into the VLM prompt for more accurate scene analysis.
- **Text Fallback Mode:** Allows the system to operate and be tested in environments without a GPU by utilizing ground-truth scene descriptions.

### 2.2 Cross-Domain Vector Indexing
- **ChromaDB Integration:** Stores every frame description along with rich metadata (GPS, Altitude, Battery, Alert Status).
- **Semantic Search:** Enables the security team to query historical data using natural language (e.g., "Find all truck visits at the garage").
- **Metadata Filtering:** High-speed retrieval based on time ranges, specific locations, or detected object types.

### 2.3 Intelligent Alert Engine
- **Deterministic Rule Base:** 8 predefined security rules covering critical scenarios:
  - **CRITICAL:** Midnight loitering detection.
  - **HIGH:** Repeated unauthorized vehicle entry.
  - **MEDIUM:** Unidentified vehicles or running persons.
  - **LOW:** Late-night activity or after-hours vehicle detection.

### 2.4 Agentic Reasoning (LangChain)
- **ReAct Pattern:** A LangChain agent (using qwen3:8b) that uses tools to:
  - Evaluate rules deterministically.
  - Search history for patterns (e.g., checking if a vehicle has been seen before).
  - Log structured security events with recommended actions and threat levels.

### 2.5 Real-Time Dashboard
- **WebSocket Streaming:** Live updates of frame processing, alerts, and events.
- **4-Tab Command Center:**
  - **Live Feed:** Visual monitoring and telemetry.
  - **Alerts:** Historical alert log with severity filtering.
  - **Event Log:** Detailed agent-reasoned events with drill-down capability.
  - **Intelligence Q&A:** A RAG-powered chat interface to query system history.

## 3. Success Metrics
- **Correctness:** Ability of the system to trigger all 8 alert rules on designed scenarios.
- **Reasoning:** Agent's ability to correlate current observations with historical data (e.g., identifying a 3rd visit of a vehicle).
- **Usability:** A production-grade UI that surfaces complex AI reasoning in an intuitive manner.
