"""Tests for frame_indexer.py — Tests 9-12 from the spec + extras."""
import os
import shutil
import pytest
from backend.frame_indexer import FrameIndexer, _get_client

@pytest.fixture()
def indexer():
    """Fresh FrameIndexer for each test with a unique collection name."""
    import uuid
    coll_name = f"test_coll_{uuid.uuid4().hex}"
    return FrameIndexer(collection_name=coll_name)


def _make_tel(location="main_gate", ts="2025-05-13T12:00:00Z",
              session="sess_test", scene="S001", tod="day"):
    return {
        "timestamp":     ts,
        "time_of_day":   tod,
        "location_label": location,
        "drone_lat":     26.8,
        "drone_lon":     75.8,
        "altitude_m":    15.0,
        "session_id":    session,
        "scene_id":      scene,
    }


# ── Test 9: Indexed frame retrieved by frame_id ──────────────────────────────
def test_index_and_retrieve_by_id(indexer):
    tel = _make_tel()
    indexer.index_frame("frame_sess_001", "A blue truck at the garage.", tel)
    result = indexer.get_frame_by_id("frame_sess_001")
    assert result is not None
    assert result["id"] == "frame_sess_001"
    assert "blue truck" in result["document"].lower()


# ── Test 10: Semantic query 'truck at garage' returns truck events ────────────
def test_semantic_query_truck(indexer):
    tel = _make_tel(location="garage")
    indexer.index_frame("frame_truck_001", "A blue Ford F150 truck is parked at the garage.", tel)
    indexer.index_frame("frame_person_001", "A person is walking near the gate.", _make_tel())

    results = indexer.query_by_text("truck at garage", n=2)
    assert len(results) > 0
    assert any("truck" in r["document"].lower() for r in results)


# ── Test 11: Time range query returns only in-range frames ───────────────────
def test_query_by_time_range(indexer):
    indexer.index_frame("f_morning", "Morning frame.", _make_tel(ts="2025-05-13T08:00:00Z"))
    indexer.index_frame("f_noon",    "Noon frame.",    _make_tel(ts="2025-05-13T12:00:00Z"))
    indexer.index_frame("f_night",   "Night frame.",   _make_tel(ts="2025-05-13T23:00:00Z", tod="night"))

    results = indexer.query_by_time_range(
        "2025-05-13T07:00:00Z",
        "2025-05-13T13:00:00Z",
    )
    result_ids = {r["id"] for r in results}
    assert "f_morning" in result_ids
    assert "f_noon"    in result_ids
    assert "f_night"   not in result_ids


# ── Test 12: Object query 'person' returns only person frames ─────────────────
def test_query_by_object_person(indexer):
    indexer.index_frame("f_person", "A person is at the gate.", _make_tel())
    indexer.index_frame("f_truck",  "A blue truck is at the garage.", _make_tel(location="garage"))

    results = indexer.query_by_object("person")
    ids = {r["id"] for r in results}
    assert "f_person" in ids
    assert "f_truck"  not in ids


# ── Test: Session frame retrieval ─────────────────────────────────────────────
def test_get_session_frames(indexer):
    indexer.index_frame("f_s1_001", "Frame A.", _make_tel(session="sess_A"))
    indexer.index_frame("f_s1_002", "Frame B.", _make_tel(session="sess_A"))
    indexer.index_frame("f_s2_001", "Frame C.", _make_tel(session="sess_B"))

    results = indexer.get_session_frames("sess_A")
    ids = {r["id"] for r in results}
    assert "f_s1_001" in ids
    assert "f_s1_002" in ids
    assert "f_s2_001" not in ids


# ── Test: Count increments correctly ─────────────────────────────────────────
def test_count(indexer):
    assert indexer.count() == 0
    indexer.index_frame("f1", "desc1", _make_tel())
    assert indexer.count() == 1
    indexer.index_frame("f2", "desc2", _make_tel())
    assert indexer.count() == 2


# ── Test: Duplicate frame_id skipped gracefully ──────────────────────────────
def test_duplicate_index_skipped(indexer):
    indexer.index_frame("dup_001", "First insert.", _make_tel())
    result = indexer.index_frame("dup_001", "Second insert.", _make_tel())
    assert result is False          # Should return False for duplicate
    assert indexer.count() == 1    # Only one document stored


# ── Test: query_alerted_frames returns alert-flagged frames only ──────────────
def test_query_alerted_frames(indexer):
    indexer.index_frame("f_alert",  "Alert frame.", _make_tel(), alert_triggered=True)
    indexer.index_frame("f_normal", "Normal frame.", _make_tel())

    alerted = indexer.query_alerted_frames()
    ids = {r["id"] for r in alerted}
    assert "f_alert"  in ids
    assert "f_normal" not in ids


# ── Test: get_all_frames returns everything ───────────────────────────────────
def test_get_all_frames(indexer):
    for i in range(3):
        indexer.index_frame(f"fall_{i}", f"Description {i}.", _make_tel())
    all_frames = indexer.get_all_frames()
    assert len(all_frames) == 3
