# 🧪 Testing & Validation Documentation

## 1. Overview
The Drone Security Analyst Agent (DSAA) has been validated using a multi-layered testing strategy to ensure reliability across real-time perception, deterministic alerting, and semantic reasoning.

---

## 2. Automated Testing Suite (Pytest)
We maintain a suite of **18 automated test cases** that validate the core backend logic in isolation. These tests utilize a `text_fallback` mode, allowing them to run without requiring a GPU or a running Ollama instance.

### **Core Test Modules:**
*   **`test_alert_engine.py`**: Validates all 8 security rules. 
    *   *Scenario:* Ensuring a "Critical" alert triggers if a person is detected at the "Main Gate" after 00:00 UTC.
*   **`test_indexer.py`**: Verifies ChromaDB integration.
    *   *Scenario:* Ingesting a frame with specific metadata and ensuring it can be retrieved via metadata filters (Location/ID).
*   **`test_qa.py`**: Tests the RAG (Retrieval-Augmented Generation) pipeline.
    *   *Scenario:* Asking "What vehicles were seen?" and validating that the agent returns sources from the vector database.
*   **`test_agent.py`**: Validates tool-calling and reasoning.
    *   *Scenario:* Ensuring the agent calls `evaluate_alert_rules` before `log_security_event`.

---

## 3. Dynamic Input Validation (Real-World Media)
Functional validation of the video pipeline was performed using dynamic MP4 inputs to simulate high-stakes security environments.

### **Test Scenario: Perimeter Intrusion (Video)**
*   **Input:** `backend/data/video/demo.mp4` (Surveillance footage of a restricted area).
*   **Process:** The `VideoSimulator` extracted frames at 1-second intervals.
*   **Validation:** 
    *   Verified the **VLM (LLava)** correctly identified vehicles and human figures in the footage.
    *   Confirmed that frames were successfully broadcasted via WebSockets to the React frontend with < 100ms latency.

---

## 4. Emergency Response & Alert Scenarios
We validated the system’s ability to respond to emergencies through specific "Threat Injections."

| Threat Scenario | Trigger Condition | System Response |
| :--- | :--- | :--- |
| **Midnight Intruder** | Time > 22:00 AND Object == "Person" | Immediate **CRITICAL** alert in AlertPanel + UI Red Pulse. |
| **Suspicious Vehicle** | AlertEngine detects "Truck" at "Main Gate" | **HIGH** alert triggered; Alert History logged in ChromaDB. |
| **Drone Battery Critical** | Telemetry Battery < 20% | **MEDIUM** alert; Dashboard Telemetry bar turns Red. |
| **Perimeter Breach** | Location == "Restricted_Zone" | **CRITICAL** alert; Agent recommends "Dispatch Ground Team." |

---

## 5. UI/UX Robustness Testing
The frontend dashboard was stress-tested for "Crash Resistance" during high-speed data streams.

*   **Data Resiliency:** Validated that the UI remains stable even if the AI backend sends malformed or missing telemetry data (using flattening logic in `useWebSocket`).
*   **Empty State Validation:** Confirmed that the "Analytics" and "Event Log" screens show helpful empty states rather than blank screens when no data has been collected yet.
*   **Turbo Mode Testing:** Verified that enabling "Turbo Mode" reduces frame-to-frame processing time by ~60% by skipping deep-thinking reasoning steps while maintaining alert integrity.

---

## 6. Manual Diagnostic Tools
A set of scratch scripts (e.g., `scratch/test_video.py`) were used to verify low-level hardware access and model connectivity before full system integration.

### **Validation Checkpoint List:**
1. [x] **Ollama Connectivity:** `ollama list` confirms models are loaded.
2. [x] **WebSocket Handshake:** Browser console confirms `WS Connected`.
3. [x] **Database Persistence:** Restarting the server preserves previous session history in `chroma_db/`.
4. [x] **Video Extraction:** `cv2` successfully opens and reads `demo.mp4`.
