"""Tests for alert_engine.py — Tests 4-8 from the spec + extras."""
import pytest
from backend.alert_engine import AlertEngine


@pytest.fixture(scope="module")
def engine():
    return AlertEngine()


def _tel(location="main_gate", timestamp="2025-05-13T00:01:00Z", frame_id="f_test"):
    return {"location_label": location, "timestamp": timestamp, "frame_id": frame_id}


# ── Test 4: ALERT_001 — Person at night triggers CRITICAL ────────────────────
def test_alert_001_critical_night(engine):
    """S004: person near main gate at midnight → ALERT_001 CRITICAL."""
    alerts = engine.evaluate(
        "A person is loitering near the main gate at midnight.",
        _tel("main_gate", "2025-05-13T00:01:00Z"),
    )
    rule_ids = [a.rule_id for a in alerts]
    assert "ALERT_001" in rule_ids
    a001 = next(a for a in alerts if a.rule_id == "ALERT_001")
    assert a001.severity == "CRITICAL"


# ── Test 5: ALERT_001 — Person in daytime does NOT fire ──────────────────────
def test_no_alert_001_daytime(engine):
    """Person at noon must NOT trigger ALERT_001."""
    alerts = engine.evaluate(
        "A person is walking near the main gate.",
        _tel("main_gate", "2025-05-13T12:00:00Z"),
    )
    assert not any(a.rule_id == "ALERT_001" for a in alerts)


# ── Test 6: ALERT_002 — Person near main_gate or perimeter fires HIGH ────────
def test_alert_002_person_near_gate(engine):
    alerts = engine.evaluate(
        "A person is walking near the main gate.",
        _tel("main_gate", "2025-05-13T12:00:00Z"),
    )
    assert any(a.rule_id == "ALERT_002" and a.severity == "HIGH" for a in alerts)


def test_alert_002_person_near_perimeter(engine):
    alerts = engine.evaluate(
        "Two people are standing near the perimeter fence.",
        _tel("perimeter", "2025-05-13T15:00:00Z"),
    )
    assert any(a.rule_id == "ALERT_002" for a in alerts)


# ── Test 7: ALERT_003 — Vehicle 3+ visits triggers HIGH ──────────────────────
def test_alert_003_repeated_vehicle(engine):
    """S015: 3rd truck visit at garage → ALERT_003 HIGH."""
    alerts = engine.evaluate(
        "The blue Ford F150 truck has entered the garage again.",
        _tel("garage", "2025-05-13T23:00:00Z"),
        visit_history={"blue truck": 3},
    )
    assert any(a.rule_id == "ALERT_003" and a.severity == "HIGH" for a in alerts)


def test_alert_003_not_fired_two_visits(engine):
    """2 visits must NOT trigger ALERT_003."""
    alerts = engine.evaluate(
        "A blue truck is parked at the garage.",
        _tel("garage", "2025-05-13T14:30:00Z"),
        visit_history={"blue truck": 2},
    )
    assert not any(a.rule_id == "ALERT_003" for a in alerts)


# ── Test 8: ALERT_004 — Unidentified vehicle → MEDIUM ────────────────────────
def test_alert_004_unidentified_vehicle(engine):
    alerts = engine.evaluate(
        "An unidentified dark vehicle is parked with no license plate visible.",
        _tel("perimeter", "2025-05-13T01:30:00Z"),
    )
    assert any(a.rule_id == "ALERT_004" and a.severity == "MEDIUM" for a in alerts)


# ── Test: ALERT_005 — Person running → MEDIUM ────────────────────────────────
def test_alert_005_person_running(engine):
    """S011: person running at night → ALERT_005."""
    alerts = engine.evaluate(
        "A person is running across the open ground.",
        _tel("perimeter", "2025-05-13T22:45:00Z"),
    )
    assert any(a.rule_id == "ALERT_005" and a.severity == "MEDIUM" for a in alerts)


# ── Test: ALERT_006 — Group of 4 people → MEDIUM ─────────────────────────────
def test_alert_006_group_of_people(engine):
    """S012: 4 people at side entrance → ALERT_006."""
    alerts = engine.evaluate(
        "A group of 4 people are standing at the side entrance.",
        _tel("side_entrance", "2025-05-13T17:00:00Z"),
    )
    assert any(a.rule_id == "ALERT_006" and a.severity == "MEDIUM" for a in alerts)


# ── Test: ALERT_007 — Vehicle after hours → LOW ──────────────────────────────
def test_alert_007_vehicle_after_hours(engine):
    """Vehicle at 23:00 → ALERT_007 LOW."""
    alerts = engine.evaluate(
        "A blue truck is at the garage entrance.",
        _tel("garage", "2025-05-13T23:00:00Z"),
    )
    assert any(a.rule_id == "ALERT_007" and a.severity == "LOW" for a in alerts)


# ── Test: ALERT_008 — Late night activity → LOW ──────────────────────────────
def test_alert_008_late_night_activity(engine):
    """S013: dark vehicle at 01:30 → ALERT_008."""
    alerts = engine.evaluate(
        "An unidentified dark vehicle is on the perimeter.",
        _tel("perimeter", "2025-05-13T01:30:00Z"),
    )
    assert any(a.rule_id == "ALERT_008" and a.severity == "LOW" for a in alerts)


# ── Test: Empty scene → zero alerts ──────────────────────────────────────────
def test_empty_scene_no_alerts(engine):
    """S014: empty compound at noon → no alerts at all."""
    alerts = engine.evaluate(
        "The compound is empty. No activity detected.",
        _tel("docking_station", "2025-05-13T12:00:00Z"),
    )
    assert len(alerts) == 0


# ── Test: get_threat_level helper ────────────────────────────────────────────
def test_get_threat_level(engine):
    alerts = engine.evaluate(
        "A person is loitering at midnight near the main gate.",
        _tel("main_gate", "2025-05-13T00:01:00Z"),
    )
    assert engine.get_threat_level(alerts) == "CRITICAL"


def test_get_threat_level_none(engine):
    assert engine.get_threat_level([]) == "NONE"


# ── Test: Multiple rules fire on same frame ───────────────────────────────────
def test_multiple_rules_same_frame(engine):
    """S011: person running at night → ALERT_001 + ALERT_005."""
    alerts = engine.evaluate(
        "A person is running across the open ground at night.",
        _tel("perimeter", "2025-05-13T22:45:00Z"),
    )
    rule_ids = {a.rule_id for a in alerts}
    assert "ALERT_001" in rule_ids
    assert "ALERT_005" in rule_ids
