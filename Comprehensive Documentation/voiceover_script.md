# 🎙️ Drone Security Analyst Agent — Demo Voiceover Script

> **Target Duration:** 5-7 Minutes
> **Note:** Speak clearly, keep a professional pace, and use the "Architecture Walk" to ground the technical depth of the project.

---

## 0:00 – 0:30 | Introduction
"Hi, I'm Tanay Singh from SPSU Udaipur. This is my submission for the FlytBase AI Engineer Technical Assessment — the Drone Security Analyst Agent. The system demonstrates an end-to-end AI pipeline for a docked drone monitoring a property. It integrates real-time visual perception, semantic indexing, and autonomous reasoning into a single command center."

## 0:30 – 1:30 | Architecture & Pipeline
"[Show docs/architecture_diagram.png] Before we see the dashboard, let's look at the engine. We've built a 7-layer pipeline. 
1. A **Frame Simulator** generates synthetic PIL images for 15 security scenarios.
2. An **Ollama-powered LLaVA-7B** model acts as our perception layer, describing scenes in natural language.
3. Every observation is stored in **ChromaDB**, creating a cross-domain searchable history.
4. Two intelligence layers run in parallel: a **Deterministic Alert Engine** with 8 rules and a **LangChain ReAct Agent** that reasons about patterns.
5. All of this is served via a **FastAPI backend** and a real-time **React dashboard**."

## 1:30 – 2:30 | Live Feed & Perception
"[Switch to Live Feed tab, click 'Start Session'] As the monitoring session begins, you can see the frames updating every second. On the right, the VLM is generating descriptions in real-time. Notice the telemetry card showing GPS, altitude, and battery levels — this metadata is synchronized with every frame and indexed into our vector database."

## 2:30 – 3:30 | Alerts & Rule Engine
"[Wait for Scene S004] Look at this detection: 'A person loitering near the main gate at midnight.' The Alert Engine immediately fires ALERT_001. [Switch to Alerts tab] This is a CRITICAL severity alert. The pulsing red border in the feed and the entry in this log provide immediate situational awareness for the security team."

## 3:30 – 4:15 | Agentic Reasoning
"[Switch to Event Log tab] Beyond simple rules, we have a LangChain analyst. If we expand this event, we can see the agent's reasoning. For example, it doesn't just see a truck; it queries ChromaDB history, sees that this is the 3rd time this vehicle has entered today, and flags the visit as an anomaly with specific recommended actions."

## 4:15 – 5:00 | Semantic Search & Intelligence Q&A
"[Switch to Q&A tab] Let's ask the Intelligence assistant: 'Were there any midnight incidents today?' The agent performs a RAG retrieval from ChromaDB and synthesizes an answer, citing the exact source frame IDs. This turns raw video data into an actionable knowledge base."

## 5:00 – 5:30 | Session Summary
"[Click 'Stop Session'] When a session ends, our Summarizer module concatenates the top events and uses an LLM to generate a single-sentence security summary. You can see it here: [Read summary]. This is a key requirement for quick reporting."

## 5:30 – 6:00 | Test Suite
"[Show terminal window] Finally, reliability is key. We have an 18-case test suite covering everything from the simulator to the Q&A agent. It runs in a text-fallback mode, ensuring the logic can be validated even in CI/CD environments without a GPU."

## 6:00 – 6:30 | Conclusion
"This prototype demonstrates how modern VLMs and agentic frameworks can transform drone monitoring from a manual task into an autonomous, intelligent security solution. Thank you for your time."
