import os
import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from .models import SecurityEvent, Alert
from .alert_engine import AlertEngine
from .frame_indexer import FrameIndexer

load_dotenv()
logger = logging.getLogger(__name__)

DRONE_AGENT_MODEL = os.getenv("DRONE_AGENT_MODEL", "qwen2:7b")
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
def get_events_file() -> Path:
    """Return the current events file path, allowing for runtime overrides."""
    return Path(os.getenv("EVENTS_FILE", "events.jsonl")).resolve()

# Shared singletons — avoid multiple DB handles
_alert_engine = None
_indexer      = None

def _get_alert_engine():
    global _alert_engine
    if _alert_engine is None:
        _alert_engine = AlertEngine()
    return _alert_engine

def _get_indexer():
    global _indexer
    if _indexer is None:
        _indexer = FrameIndexer()
    return _indexer


# ------------------------------------------------------------------ #
# Tools                                                               #
# ------------------------------------------------------------------ #

@tool
def evaluate_alert_rules(description: str, location: str,
                         timestamp: str, frame_id: str) -> str:
    """Run the deterministic alert engine on the current frame.
    Returns a JSON list of triggered alert objects."""
    telemetry = {"location_label": location, "timestamp": timestamp, "frame_id": frame_id}
    visit_history = _build_visit_history(description)
    alerts = _get_alert_engine().evaluate(description, telemetry, visit_history)
    return json.dumps([a.model_dump() for a in alerts])


@tool
def search_frame_history(query: str) -> str:
    """Semantic search of ChromaDB for similar past events.
    Returns JSON list with id, document, timestamp, location."""
    results = _get_indexer().query_by_text(query, n=3)
    slim = [
        {
            "id":        r["id"],
            "document":  r["document"][:200],
            "timestamp": r["metadata"].get("timestamp", ""),
            "location":  r["metadata"].get("location_label", ""),
        }
        for r in results
    ]
    return json.dumps(slim)


@tool
def count_object_visits(object_type: str, location: str) -> str:
    """Count how many times an object type was seen at a location this session.
    Returns the integer count as a string."""
    results = _get_indexer().query_by_object(object_type)
    count = sum(
        1 for r in results
        if r["metadata"].get("location_label", "") == location
    )
    return str(count)


@tool
def log_security_event(frame_id: str, timestamp: str, location: str,
                       vlm_description: str, objects_detected_json: str,
                       alerts_triggered_json: str, agent_summary: str,
                       threat_level: str, recommended_action: str,
                       context_from_history: str) -> str:
    """Persist a structured SecurityEvent to events.jsonl. Call this LAST."""
    try:
        objects_detected: List[str] = json.loads(objects_detected_json)
    except Exception:
        objects_detected = [s.strip() for s in objects_detected_json.split(",") if s.strip()]

    try:
        alerts = [Alert(**a) for a in json.loads(alerts_triggered_json)]
    except Exception:
        alerts = []

    event = SecurityEvent(
        frame_id=frame_id, timestamp=timestamp, location=location,
        vlm_description=vlm_description, objects_detected=objects_detected,
        alerts_triggered=alerts, agent_summary=agent_summary,
        threat_level=threat_level.upper(),
        recommended_action=recommended_action,
        context_from_history=context_from_history,
    )
    try:
        with open(get_events_file(), "a", encoding="utf-8") as fh:
            fh.write(event.model_dump_json() + "\n")
    except IOError as exc:
        logger.error("Failed to write event: %s", exc)
        return f"ERROR: {exc}"
    return "Event logged successfully."


# ------------------------------------------------------------------ #
# Internal helpers                                                     #
# ------------------------------------------------------------------ #

def _build_visit_history(description: str) -> dict:
    vehicle_labels = ["blue truck", "truck", "red car", "white van", "van", "dark vehicle"]
    desc_lower = description.lower()
    visit_history: dict = {}
    for label in vehicle_labels:
        # check if any word of the label matches
        if any(w in desc_lower for w in label.split()):
            results = _get_indexer().query_by_object(label.split()[0])  # use first keyword
            if results:
                visit_history[label] = len(results)
    return visit_history


_SYSTEM_PROMPT = """You are an AI security analyst for a property monitoring drone system.
For each video frame you receive, follow this exact order:
1. Call evaluate_alert_rules first with the frame data.
2. If any alerts fired, call search_frame_history to check for patterns.
3. If a vehicle or person was seen before, call count_object_visits.
4. Call log_security_event LAST with your complete assessment.

log_security_event MUST include:
- frame_id, timestamp, location, vlm_description
- objects_detected_json: JSON array string e.g. '["truck","person"]'
- alerts_triggered_json: the JSON from evaluate_alert_rules
- agent_summary: 1-sentence factual description
- threat_level: NONE | LOW | MEDIUM | HIGH | CRITICAL
- recommended_action: specific action for the security team
- context_from_history: relevant past observations or "None"

Be factual. Do not speculate beyond what is visible."""


# ------------------------------------------------------------------ #
# SecurityAgent                                                        #
# ------------------------------------------------------------------ #

class SecurityAgent:
    """LangGraph ReAct agent that analyses each drone frame and logs events."""

    def __init__(self):
        self.llm = ChatOllama(
            model=DRONE_AGENT_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )
        self.tools = [
            evaluate_alert_rules,
            search_frame_history,
            count_object_visits,
            log_security_event,
        ]
        self.graph = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=_SYSTEM_PROMPT,
        )

    async def process_frame(self, description: str, telemetry: dict) -> dict:
        """Run the agent pipeline for one frame. Always writes an event."""
        input_text = (
            f"Description: {description}\n"
            f"Location:    {telemetry.get('location_label', 'unknown')}\n"
            f"Timestamp:   {telemetry.get('timestamp', '')}\n"
            f"Frame ID:    {telemetry.get('frame_id', 'unknown')}\n"
            f"Time of Day: {telemetry.get('time_of_day', 'day')}"
        )
        try:
            result = await self.graph.ainvoke(
                {"messages": [HumanMessage(content=input_text)]}
            )
            return {"output": result["messages"][-1].content}
        except Exception as exc:
            logger.error("SecurityAgent error for %s: %s", telemetry.get("frame_id"), exc)
            await self._write_fallback_event(description, telemetry)
            return {"output": f"Agent failed; fallback event written. Reason: {exc}"}

    async def _write_fallback_event(self, description: str, telemetry: dict) -> None:
        """Write a minimal SecurityEvent using only the alert engine (no LLM)."""
        visit_history = _build_visit_history(description)
        alerts = _get_alert_engine().evaluate(description, telemetry, visit_history)
        threat_level = _get_alert_engine().get_threat_level(alerts)
        objects_detected = _get_indexer()._extract_objects(description)

        event = SecurityEvent(
            frame_id=telemetry.get("frame_id", "unknown"),
            timestamp=telemetry.get("timestamp", datetime.now().isoformat() + "Z"),
            location=telemetry.get("location_label", "unknown"),
            vlm_description=description,
            objects_detected=objects_detected,
            alerts_triggered=alerts,
            agent_summary=f"[Fallback] {description[:150]}",
            threat_level=threat_level,
            recommended_action="Review alert details. LLM agent was unavailable.",
            context_from_history="Agent unavailable — no history lookup performed.",
        )
        try:
            with open(get_events_file(), "a", encoding="utf-8") as fh:
                fh.write(event.model_dump_json() + "\n")
        except IOError as exc:
            logger.error("Fallback event write failed: %s", exc)


if __name__ == "__main__":
    import asyncio
    agent = SecurityAgent()
    asyncio.run(agent.process_frame(
        "A blue truck is parked at the garage entrance.",
        {"location_label": "garage", "timestamp": "2025-05-13T08:00:00Z",
         "frame_id": "frame_test_001", "time_of_day": "day"},
    ))
