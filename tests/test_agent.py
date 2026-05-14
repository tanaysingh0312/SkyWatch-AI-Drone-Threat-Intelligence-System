"""Tests for security_agent.py — Tests 13-15 from the spec.

These tests are designed to work WITHOUT Ollama by:
  1. Testing initialization (structure) synchronously.
  2. Mocking the agent_executor for end-to-end flow tests so they
     pass in CI/CD without a GPU.
  3. Testing the deterministic fallback path (which never calls the LLM).

Set DRONE_VLM_MODE=text_fallback in your env to skip Ollama for VLM too.
"""
import asyncio
import json
import os
import shutil
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Force text_fallback mode so VLM doesn't need Ollama
os.environ.setdefault("DRONE_VLM_MODE", "text_fallback")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_tel(location="main_gate", ts="2025-05-13T00:01:00Z",
              frame_id="frame_sess_test_001", tod="night"):
    return {
        "frame_id":      frame_id,
        "session_id":    "sess_test",
        "location_label": location,
        "timestamp":     ts,
        "time_of_day":   tod,
    }


# ── Test 13: Agent initialises with correct tool set ─────────────────────────
def test_agent_initialises():
    """SecurityAgent must initialise with 4 tools and an executor."""
    from backend.security_agent import SecurityAgent
    with patch("backend.security_agent.ChatOllama"):   # skip actual Ollama connect
        agent = SecurityAgent()
    assert len(agent.tools) == 4
    assert agent.graph is not None
    tool_names = {t.name for t in agent.tools}
    assert "evaluate_alert_rules"  in tool_names
    assert "search_frame_history"  in tool_names
    assert "count_object_visits"   in tool_names
    assert "log_security_event"    in tool_names


# ── Test 14: Fallback event has all SecurityEvent fields ─────────────────────
@pytest.mark.asyncio
async def test_fallback_event_has_all_fields(tmp_path):
    """When agent fails, _write_fallback_event must produce a valid SecurityEvent."""
    os.environ["EVENTS_FILE"] = str(tmp_path / "events.jsonl")

    from backend.security_agent import SecurityAgent
    with patch("backend.security_agent.ChatOllama"):
        agent = SecurityAgent()

    description = "A person is loitering near the main gate at midnight."
    telemetry   = _make_tel()

    await agent._write_fallback_event(description, telemetry)

    events_file = tmp_path / "events.jsonl"
    assert events_file.exists(), "events.jsonl was not created"

    with open(events_file) as fh:
        line = fh.readline()
    event = json.loads(line)

    required_fields = [
        "event_id", "frame_id", "timestamp", "location",
        "vlm_description", "objects_detected", "alerts_triggered",
        "agent_summary", "threat_level", "recommended_action",
        "context_from_history",
    ]
    for field in required_fields:
        assert field in event, f"Missing SecurityEvent field: {field}"

    os.environ.pop("EVENTS_FILE", None)


# ── Test 15: Fallback midnight person → CRITICAL threat_level ────────────────
@pytest.mark.asyncio
async def test_fallback_midnight_person_critical(tmp_path):
    """Person at midnight must produce threat_level CRITICAL via fallback path."""
    os.environ["EVENTS_FILE"] = str(tmp_path / "events.jsonl")

    from backend.security_agent import SecurityAgent
    with patch("backend.security_agent.ChatOllama"):
        agent = SecurityAgent()

    description = "A person is loitering near the main gate at midnight."
    telemetry   = _make_tel("main_gate", "2025-05-13T00:01:00Z")
    await agent._write_fallback_event(description, telemetry)

    with open(tmp_path / "events.jsonl") as fh:
        event = json.loads(fh.readline())

    assert event["threat_level"] == "CRITICAL", (
        f"Expected CRITICAL threat_level, got {event['threat_level']}"
    )
    os.environ.pop("EVENTS_FILE", None)


# ── Test 16: process_frame falls back gracefully when LLM errors ─────────────
@pytest.mark.asyncio
async def test_process_frame_fallback_on_llm_error(tmp_path):
    """process_frame must write a fallback event and not raise when LLM fails."""
    os.environ["EVENTS_FILE"] = str(tmp_path / "events.jsonl")

    from backend.security_agent import SecurityAgent
    with patch("backend.security_agent.ChatOllama"):
        agent = SecurityAgent()

    # Make the graph raise to force fallback
    agent.graph.ainvoke = AsyncMock(side_effect=RuntimeError("LLM offline"))

    description = "A blue truck is at the garage."
    telemetry   = _make_tel("garage", "2025-05-13T08:00:00Z", tod="day")

    result = await agent.process_frame(description, telemetry)

    # Should not raise; returns a dict with 'output'
    assert isinstance(result, dict)
    assert "output" in result

    # Fallback event should still be written
    assert (tmp_path / "events.jsonl").exists()
    os.environ.pop("EVENTS_FILE", None)
