"""Tests for frame_simulator.py — Tests 1-4 (covers spec tests 1, 2, 3)."""
import pytest
from PIL import Image
from backend.frame_simulator import FrameSimulator


@pytest.fixture(scope="module")
def sim():
    return FrameSimulator()


# ── Test 1: All required telemetry keys present ──────────────────────────────
def test_telemetry_required_keys(sim):
    """Frame telemetry must contain all spec-defined keys."""
    _, tel = sim.generate_frame("S001")
    required = [
        "frame_id", "session_id", "timestamp",
        "drone_lat", "drone_lon", "altitude_m",
        "heading_deg", "battery_pct", "location_label",
        "time_of_day", "scene_id", "raw_description",
    ]
    for key in required:
        assert key in tel, f"Missing telemetry key: {key}"


# ── Test 2: Image dimensions exactly 640×480 ─────────────────────────────────
def test_image_dimensions(sim):
    img, _ = sim.generate_frame("S001")
    assert isinstance(img, Image.Image)
    assert img.size == (640, 480), f"Expected (640,480), got {img.size}"


# ── Test 3: generate_session returns exactly 15 frames ───────────────────────
def test_generate_session_count(sim):
    frames = sim.generate_session()
    assert len(frames) == 15


# ── Test 4: n_frames parameter works correctly ───────────────────────────────
def test_generate_session_n_frames(sim):
    frames = sim.generate_session(n_frames=5)
    assert len(frames) == 5


# ── Test 5: All 15 scenes generate without error ─────────────────────────────
def test_all_scenes_generate(sim):
    for scene_id in sim.scenes:
        img, tel = sim.generate_frame(scene_id)
        assert isinstance(img, Image.Image)
        assert tel["scene_id"] == scene_id


# ── Test 6: time_of_day values are within spec ───────────────────────────────
def test_time_of_day_values(sim):
    valid = {"day", "night", "dawn", "dusk"}
    for scene_id in sim.scenes:
        _, tel = sim.generate_frame(scene_id)
        assert tel["time_of_day"] in valid, (
            f"Scene {scene_id} has invalid time_of_day: {tel['time_of_day']}"
        )


# ── Test 7: Night scenes correctly labelled ──────────────────────────────────
def test_night_scenes_labelled_correctly(sim):
    """S004 (00:01) and S015 (23:00) must be labelled 'night'."""
    for scene_id in ["S004", "S011", "S013", "S015"]:
        _, tel = sim.generate_frame(scene_id)
        assert tel["time_of_day"] == "night", (
            f"Scene {scene_id} should be 'night', got '{tel['time_of_day']}'"
        )


# ── Test 8: Battery decrements across session ────────────────────────────────
def test_battery_decrements(sim):
    frames = sim.generate_session()
    batteries = [tel["battery_pct"] for _, tel in frames]
    # Battery should generally decrease or at least start at 100
    assert batteries[0] == 100
    assert batteries[-1] < batteries[0]
