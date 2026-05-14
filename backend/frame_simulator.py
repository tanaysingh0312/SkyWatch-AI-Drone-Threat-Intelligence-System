import random
import io
import base64
from datetime import datetime
from PIL import Image, ImageDraw
import os
from pathlib import Path
from typing import Tuple, List, Optional


# Fixed base date for reproducible timestamps
SESSION_DATE = "2025-05-13"


class FrameSimulator:
    """Generates synthetic 640x480 PIL frames and paired telemetry dicts.
    
    Supports 15 predefined security scenes, each designed to trigger
    specific alert rules in the AlertEngine.
    """

    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.scenes = {
            "S001": {
                "desc": "High-altitude thermal scan of perimeter fence. No breaches detected.",
                "objects": ["perimeter fence"], "time": "22:00",
                "location": "perimeter", "weather": "night"
            },
            "S002": {
                "desc": "Tactical view of parking lot in rainy conditions. Tracked vehicle entering secure zone.",
                "objects": ["dark vehicle"], "time": "23:30",
                "location": "parking_lot", "weather": "rainy"
            },
            "S003": {
                "desc": "Roof-level surveillance of warehouse skylights. Unidentified individual detected in restricted area.",
                "objects": ["person"], "time": "01:00",
                "location": "warehouse", "weather": "night"
            },
            "S004": {
                "desc": "Person loitering near main gate at midnight",
                "objects": ["person"], "time": "00:01",
                "location": "main_gate", "weather": "night"
            },
            "S005": {
                "desc": "Delivery van unloading at loading dock",
                "objects": ["white van"], "time": "09:15",
                "location": "loading_dock", "weather": "clear"
            },
            "S006": {
                "desc": "Two people standing near perimeter fence",
                "objects": ["2 people"], "time": "15:00",
                "location": "perimeter", "weather": "clear"
            },
            "S007": {
                "desc": "Red sedan driving through parking lot",
                "objects": ["red car"], "time": "13:00",
                "location": "parking_lot", "weather": "clear"
            },
            "S008": {
                "desc": "Empty compound — no activity detected",
                "objects": [], "time": "03:00",
                "location": "perimeter", "weather": "night"
            },
            "S009": {
                "desc": "Security guard on patrol near warehouse",
                "objects": ["person (uniform)"], "time": "06:00",
                "location": "warehouse", "weather": "dawn"
            },
            "S010": {
                "desc": "Forklift operating in loading zone",
                "objects": ["forklift"], "time": "10:00",
                "location": "loading_zone", "weather": "clear"
            },
            "S011": {
                "desc": "Person running across open ground",
                "objects": ["person (running)"], "time": "22:45",
                "location": "perimeter", "weather": "night"
            },
            "S012": {
                "desc": "Group of 4 people at side entrance",
                "objects": ["4 people"], "time": "17:00",
                "location": "side_entrance", "weather": "dusk"
            },
            "S013": {
                "desc": "Unidentified vehicle — no license visible",
                "objects": ["dark vehicle"], "time": "01:30",
                "location": "perimeter", "weather": "night"
            },
            "S014": {
                "desc": "Drone docked, clear sky, perimeter empty",
                "objects": [], "time": "12:00",
                "location": "docking_station", "weather": "clear"
            },
            "S015": {
                "desc": "Blue Ford F150 third entry — anomaly flag",
                "objects": ["blue truck"], "time": "23:00",
                "location": "garage", "weather": "night"
            },
        }

    # ------------------------------------------------------------------ #
    # Sky helpers                                                          #
    # ------------------------------------------------------------------ #

    def _get_time_of_day(self, hour: int) -> str:
        """Returns canonical time-of-day string per schema."""
        if 5 <= hour < 8:   return "dawn"
        if 8 <= hour < 18:  return "day"
        if 18 <= hour < 21: return "dusk"
        return "night"

    def _get_sky_gradient(self, time_of_day: str) -> Tuple[int, int, int]:
        """Returns dominant sky RGB colour for the given time bucket."""
        palettes = {
            "dawn":  (255, 160, 100),   # warm orange
            "day":   (0,   191, 255),   # sky blue
            "dusk":  (255, 100, 50),    # deep orange
            "night": (15,  15,  60),    # near-black blue
        }
        return palettes.get(time_of_day, (0, 191, 255))

    # ------------------------------------------------------------------ #
    # Object drawers                                                       #
    # ------------------------------------------------------------------ #

    def _draw_vehicle(self, draw: ImageDraw.Draw, x: int, y: int,
                      color: str, label: str) -> None:
        """Draws a simplified vehicle (rectangle body + roof + wheels)."""
        body_color = {"blue": (30, 100, 200), "white": (220, 220, 220),
                      "red": (200, 40, 40), "gray": (100, 100, 100)}.get(color, (100, 100, 100))
        # Body
        draw.rectangle([x, y, x + 120, y + 60], fill=body_color, outline="black")
        # Roof cabin
        draw.rectangle([x + 20, y - 30, x + 100, y], fill=body_color, outline="black")
        # Wheels
        draw.ellipse([x + 10, y + 50, x + 30, y + 70], fill="black")
        draw.ellipse([x + 90, y + 50, x + 110, y + 70], fill="black")
        # Label
        draw.text((x + 5, y + 15), label[:12], fill="white")

    def _draw_person(self, draw: ImageDraw.Draw, x: int, y: int,
                     label: str = "Person") -> None:
        """Draws a stick-figure person."""
        # Head
        draw.ellipse([x, y, x + 18, y + 18], fill=(255, 220, 185), outline="black")
        # Body
        draw.line([x + 9, y + 18, x + 9, y + 55], fill="black", width=2)
        # Arms
        draw.line([x - 10, y + 28, x + 28, y + 28], fill="black", width=2)
        # Legs
        draw.line([x + 9, y + 55, x - 2, y + 88], fill="black", width=2)
        draw.line([x + 9, y + 55, x + 20, y + 88], fill="black", width=2)
        # Label above head
        draw.text((x - 10, y - 15), label[:12], fill="red")

    # ------------------------------------------------------------------ #
    # Core generators                                                      #
    # ------------------------------------------------------------------ #

    def generate_frame(self, scene_id: str, session_id: str = "session_001",
                       frame_idx: int = 0) -> Tuple[Image.Image, dict]:
        """Generate a single PIL frame and telemetry dict for the given scene.

        Returns:
            (PIL.Image, telemetry_dict)
        """
        scene = self.scenes.get(scene_id, self.scenes["S014"])
        time_str = scene["time"]
        hour = int(time_str.split(":")[0])
        time_of_day = self._get_time_of_day(hour)
        sky_color = self._get_sky_gradient(time_of_day)

        # ---- Build image ----
        # Try to load cinematic frame if it exists
        # Use absolute path based on this file's location
        base_path = Path(__file__).parent.resolve()
        cinematic_path = base_path / "data" / "cinematic" / f"{scene_id}.png"
        
        if cinematic_path.exists():
            img = Image.open(str(cinematic_path)).convert("RGB").resize((self.width, self.height))
            draw = ImageDraw.Draw(img)
            # Skip the drawing logic for synthetic frames if we have a real one
        else:
            # Fallback drawing logic
            img = Image.new("RGB", (self.width, self.height), color=sky_color)
            draw = ImageDraw.Draw(img)

            # Ground strip
            ground_y = self.height // 2
            draw.rectangle([0, ground_y, self.width, self.height], fill=(34, 139, 34))

            # Location marker line (fence silhouette)
            for fx in range(0, self.width, 30):
                draw.line([fx, ground_y - 20, fx, ground_y], fill=(80, 50, 20), width=3)
            draw.line([0, ground_y - 20, self.width, ground_y - 20], fill=(80, 50, 20), width=2)

            # Draw vehicles
            desc_lower = scene["desc"].lower()
            if any(k in desc_lower for k in ["truck", "vehicle", "van", "car", "forklift", "sedan"]):
                vehicle_color = (
                    "blue"  if "blue"  in desc_lower else
                    "white" if "white" in desc_lower else
                    "red"   if "red"   in desc_lower else
                    "gray"
                )
                v_label = scene["objects"][0] if scene["objects"] else "Vehicle"
                self._draw_vehicle(draw, 180, 290, vehicle_color, v_label)

            # Draw people
            if any(k in desc_lower for k in ["person", "people", "guard"]):
                p_label = scene["objects"][0] if scene["objects"] else "Person"
                self._draw_person(draw, 390, 310, p_label)

                if "2 people" in desc_lower:
                    self._draw_person(draw, 440, 310, "Person2")

                if "4 people" in desc_lower or "group" in desc_lower:
                    for offset, lbl in [(440, "P2"), (490, "P3"), (540, "P4")]:
                        self._draw_person(draw, offset, 310, lbl)

        # Overlay HUD text
        timestamp = f"{SESSION_DATE}T{time_str}:00Z"
        draw.rectangle([0, 0, self.width, 70], fill=(0, 0, 0, 160))
        draw.text((10, 8),  f"TIME:  {timestamp}",            fill="white")
        draw.text((10, 26), f"LOC:   {scene['location'].upper()}", fill=(0, 212, 255))
        draw.text((10, 44), f"SCENE: {scene_id} | WX: {scene['weather'].upper()}", fill=(200, 200, 200))

        # Night overlay tint
        if time_of_day == "night":
            night_overlay = Image.new("RGBA", (self.width, self.height),
                                      (0, 0, 30, 80))
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, night_overlay).convert("RGB")

        # ---- Telemetry ----
        telemetry = {
            "frame_id":      f"frame_{session_id}_{frame_idx:03d}",
            "session_id":    session_id,
            "timestamp":     timestamp,
            "drone_lat":     26.8467 + random.uniform(-0.001, 0.001),
            "drone_lon":     75.8000 + random.uniform(-0.001, 0.001),
            "altitude_m":    round(random.uniform(10.0, 20.0), 2),
            "heading_deg":   random.randint(0, 360),
            "battery_pct":   max(0, 100 - frame_idx * 5),
            "location_label": scene["location"],
            "time_of_day":   time_of_day,       # day | night | dawn | dusk
            "scene_id":      scene_id,
            "weather":       scene["weather"],
            "raw_description": scene["desc"],   # Used by text_fallback VLM mode
        }

        return img, telemetry

    def generate_session(self, session_id: str = "session_001",
                         n_frames: Optional[int] = None) -> List[Tuple[Image.Image, dict]]:
        """Generate an ordered sequence of frames for all (or n) scenes.

        Args:
            session_id: Session identifier to embed in telemetry.
            n_frames:   If specified, only generate the first n scenes.

        Returns:
            List of (PIL.Image, telemetry_dict) tuples.
        """
        scene_ids = sorted(self.scenes.keys())
        if n_frames is not None:
            scene_ids = scene_ids[:n_frames]

        frames = []
        for i, scene_id in enumerate(scene_ids):
            frames.append(self.generate_frame(scene_id, session_id, i))
        return frames

    def get_frame_as_base64(self, scene_id: str, session_id: str = "session_001",
                            frame_idx: int = 0) -> str:
        """Returns base64-encoded PNG of the frame (for serving via API)."""
        img, _ = self.generate_frame(scene_id, session_id, frame_idx)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


if __name__ == "__main__":
    sim = FrameSimulator()
    img, tel = sim.generate_frame("S004")
    img.save("test_frame_S004.png")
    print("Telemetry:", tel)
    print("Session frames:", len(sim.generate_session()))
