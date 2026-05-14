"""Tests for qa_agent.py — Tests 16-18 from the spec.

Uses retrieval fallback path so tests pass without Ollama.
"""
import os
import shutil
import json
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

os.environ.setdefault("DRONE_VLM_MODE", "text_fallback")

@pytest.fixture()
def indexed_qa_agent():
    """Set up a FrameIndexer with test data and a QAAgent pointing to it."""
    from backend.frame_indexer import FrameIndexer
    idx = FrameIndexer(collection_name="qa_test_frames")

    # Index representative frames mirroring the 5 spec example Q&As
    frames_data = [
        ("frame_sess_001_000", "A blue Ford F150 truck is parked at the garage entrance.",
         {"timestamp": "2025-05-13T08:00:00Z", "location_label": "garage",
          "time_of_day": "day", "session_id": "sess_001", "scene_id": "S001"}),
        ("frame_sess_001_001", "The blue Ford F150 truck re-entering the garage, second visit.",
         {"timestamp": "2025-05-13T14:30:00Z", "location_label": "garage",
          "time_of_day": "day", "session_id": "sess_001", "scene_id": "S002"}),
        ("frame_sess_001_002", "A person loitering near the main gate at midnight.",
         {"timestamp": "2025-05-13T00:01:00Z", "location_label": "main_gate",
          "time_of_day": "night", "session_id": "sess_001", "scene_id": "S004"}),
        ("frame_sess_001_003", "A delivery van unloading at the garage loading dock.",
         {"timestamp": "2025-05-13T09:15:00Z", "location_label": "garage",
          "time_of_day": "day", "session_id": "sess_001", "scene_id": "S005"}),
        ("frame_sess_001_004", "An unidentified dark vehicle on the perimeter, no plates visible.",
         {"timestamp": "2025-05-13T01:30:00Z", "location_label": "perimeter",
          "time_of_day": "night", "session_id": "sess_001", "scene_id": "S013"}),
        ("frame_sess_001_005", "Blue Ford F150 truck third entry at the garage — anomaly.",
         {"timestamp": "2025-05-13T23:00:00Z", "location_label": "garage",
          "time_of_day": "night", "session_id": "sess_001", "scene_id": "S015"}),
    ]
    for fid, desc, tel in frames_data:
        idx.index_frame(fid, desc, tel, alert_triggered="gate" in tel["location_label"]
                        or tel["time_of_day"] == "night")

    from backend.qa_agent import QAAgent
    with patch("backend.qa_agent.ChatOllama"):
        agent = QAAgent(indexer=idx)

    return agent, idx


# ── Test 16: Q&A returns a number for truck visit count ──────────────────────
@pytest.mark.asyncio
async def test_qa_truck_count_returns_number(indexed_qa_agent):
    """'How many times did the blue truck enter?' must mention a number."""
    agent, idx = indexed_qa_agent

    # Force retrieval fallback (no LLM) by making ainvoke raise
    agent.graph.ainvoke = AsyncMock(side_effect=RuntimeError("No LLM"))

    answer, sources = await agent.answer("How many times did the blue truck enter today?")

    import re
    # Answer must contain at least one digit
    assert re.search(r"\d", answer), (
        f"Expected a number in answer, got: {answer}"
    )


# ── Test 17: Q&A references midnight incident ────────────────────────────────
@pytest.mark.asyncio
async def test_qa_midnight_incident(indexed_qa_agent):
    """'Were there midnight incidents?' answer must reference 00:01."""
    agent, idx = indexed_qa_agent
    agent.graph.ainvoke = AsyncMock(side_effect=RuntimeError("No LLM"))

    answer, sources = await agent.answer("Were there any midnight incidents?")

    assert "00:01" in answer or "midnight" in answer.lower() or "main_gate" in answer.lower(), (
        f"Expected midnight reference in answer, got: {answer}"
    )


# ── Test 18: Q&A returns source frame IDs ────────────────────────────────────
@pytest.mark.asyncio
async def test_qa_returns_source_ids(indexed_qa_agent):
    """The answer tuple must include at least one frame ID as a source."""
    agent, idx = indexed_qa_agent
    agent.graph.ainvoke = AsyncMock(side_effect=RuntimeError("No LLM"))

    answer, sources = await agent.answer("What was observed at the garage?")

    assert len(sources) > 0, "Expected at least one source frame ID"
    # Sources should look like valid frame IDs
    assert all("frame_" in s for s in sources), (
        f"Source IDs don't look like frame IDs: {sources}"
    )


# ── Test: Q&A handles empty index gracefully ─────────────────────────────────
@pytest.mark.asyncio
async def test_qa_empty_index():
    """QAAgent must return a graceful message when no frames are indexed."""
    import backend.frame_indexer as fi_module
    import backend.qa_agent as qa_module

    fi_module._chroma_client = None
    qa_module._indexer = None
    os.environ["CHROMA_PERSIST_PATH"] = ":memory:"

    from backend.frame_indexer import FrameIndexer
    from backend.qa_agent import QAAgent

    idx = FrameIndexer(collection_name="empty_test")
    with patch("backend.qa_agent.ChatOllama"):
        agent = QAAgent(indexer=idx)

    agent.graph.ainvoke = AsyncMock(side_effect=RuntimeError("No LLM"))

    answer, sources = await agent.answer("What happened today?")
    assert isinstance(answer, str)
    assert len(answer) > 0

    fi_module._chroma_client = None
    qa_module._indexer = None
    os.environ.pop("CHROMA_PERSIST_PATH", None)
