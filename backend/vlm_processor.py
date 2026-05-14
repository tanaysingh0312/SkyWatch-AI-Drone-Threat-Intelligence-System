import base64
import json
import os
import httpx
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DRONE_VLM_MODE = os.getenv("DRONE_VLM_MODE", "text_fallback")
DRONE_VLM_MODEL = os.getenv("DRONE_VLM_MODEL", "llava")

class VLMProcessor:
    def __init__(self):
        self.system_prompt = (
            "You are a drone security camera analyst. Your job is to describe exactly what you see "
            "in this frame in 1-2 sentences. Focus on: "
            "- Objects present: vehicles (color, type), people (count, behavior, clothing) "
            "- Location context visible in the image (gate, garage, fence, parking lot) "
            "- Any unusual, suspicious, or noteworthy activity "
            "- Time context if visible (lighting, shadows) "
            "Output ONLY the description. No preamble, no explanation. Be specific and factual."
        )

    def _encode_image(self, image: Image.Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    async def describe_frame(self, image: Image.Image, telemetry: dict) -> str:
        if DRONE_VLM_MODE == "text_fallback":
            # In fallback mode, we use the ground truth description from the simulator
            return telemetry.get("raw_description", "No description available.")

        image_b64 = self._encode_image(image)
        
        prompt = f"{self.system_prompt}\n\nContext from telemetry: Location is {telemetry.get('location_label')}, Time of day is {telemetry.get('time_of_day')}."
        
        payload = {
            "model": DRONE_VLM_MODEL,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    print(f"Ollama API error: {response.status_code}")
                    return telemetry.get("raw_description", "Error calling VLM API.")
        except Exception as e:
            print(f"Exception calling Ollama: {e}")
            return telemetry.get("raw_description", "Fallback due to connection error.")

    async def describe_frame_batch(self, frames):
        descriptions = []
        for img, tel in frames:
            desc = await self.describe_frame(img, tel)
            descriptions.append(desc)
        return descriptions
