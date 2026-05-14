import re
from typing import List, Optional
from datetime import datetime
from .models import Alert


class AlertEngine:
    """Deterministic rule-based alert evaluation.

    Evaluates all 8 rules against each frame's VLM description + telemetry.
    Rules can overlap (multiple alerts per frame is valid).

    Alert rules:
        ALERT_001 CRITICAL  Person + night (22:00–06:00)
        ALERT_002 HIGH      Person near main_gate OR perimeter (any time)
        ALERT_003 HIGH      Vehicle 3+ visits same session (requires visit_history)
        ALERT_004 MEDIUM    Unidentified vehicle (no recognizable color/type)
        ALERT_005 MEDIUM    Person running detected
        ALERT_006 MEDIUM    Group of 3+ people
        ALERT_007 LOW       Any vehicle outside business hours (19:00–07:00)
        ALERT_008 LOW       Any activity detected between 01:00–05:00
    """

    # ------------------------------------------------------------------ #
    # Top-level entry                                                      #
    # ------------------------------------------------------------------ #

    def evaluate(
        self,
        description: str,
        telemetry: dict,
        visit_history: Optional[dict] = None,
    ) -> List[Alert]:
        """Run all 8 rules; return list of triggered Alert objects.

        Args:
            description:   VLM natural-language frame description.
            telemetry:     Frame telemetry dict (must contain timestamp, location_label, frame_id).
            visit_history: Optional dict mapping object-label → visit count this session.
                           Example: {"blue truck": 3, "person": 1}
        """
        alerts: List[Alert] = []

        desc_lower    = description.lower()
        location      = telemetry.get("location_label", "unknown")
        timestamp     = telemetry.get("timestamp", datetime.now().isoformat() + "Z")
        frame_id      = telemetry.get("frame_id", "unknown")

        # ---- Parse hour robustly ----
        try:
            # Timestamp format: 2025-05-13T00:01:00Z
            time_part = timestamp.split("T")[1][:5]   # "HH:MM"
            hour = int(time_part.split(":")[0])
        except (IndexError, ValueError):
            hour = 12   # Safe default → daytime
            time_part = "12:00"

        # ---- Boolean detection helpers ----
        has_person  = bool(re.search(r"\b(person|people|guard|individual|man|woman|figure)\b", desc_lower))
        has_vehicle = bool(re.search(r"\b(vehicle|truck|car|van|forklift|sedan|pickup)\b", desc_lower))
        is_night      = hour >= 22 or hour < 6      # 22:00–05:59
        is_after_hours = hour >= 19 or hour < 7     # 19:00–06:59
        is_late_night  = 1 <= hour <= 5             # 01:00–05:00

        # ---------------------------------------------------------------- #
        # ALERT_001 — CRITICAL: Person at night                            #
        # ---------------------------------------------------------------- #
        if has_person and is_night:
            alerts.append(Alert(
                rule_id="ALERT_001",
                severity="CRITICAL",
                message=(
                    f"Person loitering at {location} at {time_part}. "
                    "Immediate review required."
                ),
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["person"],
            ))

        # ---------------------------------------------------------------- #
        # ALERT_002 — HIGH: Person near sensitive location (always fires,  #
        # even if ALERT_001 also fired — rules are independent)            #
        # ---------------------------------------------------------------- #
        if has_person and location in ("main_gate", "perimeter"):
            alerts.append(Alert(
                rule_id="ALERT_002",
                severity="HIGH",
                message=(
                    f"Person near {location} at {time_part}. "
                    "Monitor for unauthorized access."
                ),
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["person"],
            ))

        # ---------------------------------------------------------------- #
        # ALERT_003 — HIGH: Repeated vehicle entry (3+ visits)            #
        # visit_history keys are matched case-insensitively against desc   #
        # ---------------------------------------------------------------- #
        if has_vehicle and visit_history:
            for obj_label, count in visit_history.items():
                if count >= 3:
                    obj_lower = obj_label.lower()
                    label_words = obj_lower.split()
                    # Match if full label OR any individual word from the
                    # label appears in the description (handles 'truck',
                    # 'blue truck', 'F150', 'pickup', etc.)
                    label_in_desc = (
                        obj_lower in desc_lower
                        or any(w in desc_lower for w in label_words)
                    )
                    if label_in_desc:
                        alerts.append(Alert(
                            rule_id="ALERT_003",
                            severity="HIGH",
                            message=(
                                f"Vehicle repeated entry: {obj_label} at {location} — "
                                f"{count} visits today."
                            ),
                            frame_id=frame_id,
                            timestamp=timestamp,
                            location=location,
                            objects=[obj_label],
                        ))
                        break   # One ALERT_003 per frame is enough

        # ---------------------------------------------------------------- #
        # ALERT_004 — MEDIUM: Unidentified vehicle                         #
        # ---------------------------------------------------------------- #
        if has_vehicle and (
            "unidentified" in desc_lower
            or ("no license" in desc_lower)
            or ("dark vehicle" in desc_lower)
        ):
            alerts.append(Alert(
                rule_id="ALERT_004",
                severity="MEDIUM",
                message=(
                    f"Unidentified vehicle at {location} at {time_part}. "
                    "Plate not visible."
                ),
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["vehicle"],
            ))

        # ---------------------------------------------------------------- #
        # ALERT_005 — MEDIUM: Person running                               #
        # ---------------------------------------------------------------- #
        if re.search(r"\brunning\b", desc_lower):
            alerts.append(Alert(
                rule_id="ALERT_005",
                severity="MEDIUM",
                message=f"Person running detected at {location} at {time_part}.",
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["person"],
            ))

        # ---------------------------------------------------------------- #
        # ALERT_006 — MEDIUM: Group of 3+ people                          #
        # ---------------------------------------------------------------- #
        people_count = self._extract_people_count(desc_lower)
        if people_count >= 3:
            alerts.append(Alert(
                rule_id="ALERT_006",
                severity="MEDIUM",
                message=(
                    f"Group of people ({people_count}) at {location} at {time_part}."
                ),
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["people"],
            ))

        # ---------------------------------------------------------------- #
        # ALERT_007 — LOW: Vehicle detected after hours (19:00–07:00)     #
        # ---------------------------------------------------------------- #
        if has_vehicle and is_after_hours:
            alerts.append(Alert(
                rule_id="ALERT_007",
                severity="LOW",
                message=(
                    f"Vehicle detected after hours at {location} at {time_part}."
                ),
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["vehicle"],
            ))

        # ---------------------------------------------------------------- #
        # ALERT_008 — LOW: Any activity between 01:00–05:00               #
        # ---------------------------------------------------------------- #
        if (has_person or has_vehicle) and is_late_night:
            alerts.append(Alert(
                rule_id="ALERT_008",
                severity="LOW",
                message=(
                    f"Unusual late-night activity at {location} at {time_part}."
                ),
                frame_id=frame_id,
                timestamp=timestamp,
                location=location,
                objects=["activity"],
            ))

        return alerts

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_people_count(desc_lower: str) -> int:
        """Best-effort extraction of number of people mentioned in desc."""
        # "4 people", "two people", "a group of 3"
        word_map = {"two": 2, "three": 3, "four": 4, "five": 5,
                    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

        # Numeric: "4 people", "group of 4"
        m = re.search(r"(\d+)\s+people", desc_lower)
        if m:
            return int(m.group(1))

        # Word number: "group of four people"
        for word, val in word_map.items():
            if re.search(rf"\b{word}\b.{{0,20}}\bpeople\b", desc_lower):
                return val

        # Scene-level hints
        if "group of 4" in desc_lower or "four people" in desc_lower:
            return 4
        if "group" in desc_lower and "people" in desc_lower:
            return 3    # conservative: group implies ≥3

        return 1  # single person

    def get_threat_level(self, alerts: List[Alert]) -> str:
        """Derive overall threat level from a list of alerts."""
        if any(a.severity == "CRITICAL" for a in alerts): return "CRITICAL"
        if any(a.severity == "HIGH"     for a in alerts): return "HIGH"
        if any(a.severity == "MEDIUM"   for a in alerts): return "MEDIUM"
        if any(a.severity == "LOW"      for a in alerts): return "LOW"
        return "NONE"

    def get_visit_count(self, object_type: str, indexed_frames: list) -> int:
        """Count visits of an object type across a list of indexed frame metadata dicts."""
        count = 0
        obj_lower = object_type.lower()
        for frame in indexed_frames:
            meta = frame.get("metadata", {})
            objects_str = meta.get("objects_detected", "").lower()
            desc = frame.get("document", "").lower()
            if obj_lower in objects_str or obj_lower in desc:
                count += 1
        return count
