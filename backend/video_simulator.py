import cv2
import os
import random
import base64
import io
from PIL import Image
from datetime import datetime
from typing import Tuple, Optional

from pathlib import Path

class VideoSimulator:
    def __init__(self, video_filename: str = "demo.mp4"):
        # Use absolute path based on this file's location
        base_path = Path(__file__).parent.resolve()
        self.video_path = base_path / "data" / "video" / video_filename
        
        self.cap = None
        self.total_frames = 0
        if self.video_path.exists():
            self.cap = cv2.VideoCapture(str(self.video_path))
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"VideoSimulator: Loaded video {self.video_path} with {self.total_frames} frames.")
        else:
            print(f"VideoSimulator: Video file {self.video_path} not found. Fallback mode enabled.")

    def get_frame(self, frame_idx: int) -> Optional[Tuple[Image.Image, dict]]:
        if not self.cap or not self.cap.isOpened():
            return None

        # Jump to frame_idx (or loop if end of video)
        target_frame = frame_idx % self.total_frames
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Convert OpenCV BGR to PIL RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Resize to 640x480 for consistency
        img = img.resize((640, 480))

        # Generate realistic telemetry
        timestamp = datetime.now().isoformat() + "Z"
        telemetry = {
            "frame_id":      f"video_frame_{frame_idx:04d}",
            "session_id":    "video_session",
            "timestamp":     timestamp,
            "drone_lat":     26.8467 + random.uniform(-0.0005, 0.0005),
            "drone_lon":     75.8000 + random.uniform(-0.0005, 0.0005),
            "altitude_m":    round(random.uniform(15.0, 25.0), 2),
            "heading_deg":   random.randint(0, 360),
            "battery_pct":   max(0, 100 - frame_idx // 10),
            "location_label": "surveillance_zone",
            "time_of_day":   "day",
            "scene_id":      f"V{frame_idx:03d}",
            "weather":       "clear",
            "raw_description": "Analyzing real-time video stream...",
        }

        return img, telemetry

    def __del__(self):
        if self.cap:
            self.cap.release()
