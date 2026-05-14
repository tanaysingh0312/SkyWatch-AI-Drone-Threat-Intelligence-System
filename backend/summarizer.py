import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM

from .frame_indexer import FrameIndexer

load_dotenv()
logger = logging.getLogger(__name__)

DRONE_AGENT_MODEL = os.getenv("DRONE_AGENT_MODEL", "qwen2:7b")
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Max characters of concatenated events we send to the LLM to prevent overflow
MAX_CONTEXT_CHARS = 3000


class SessionSummarizer:
    """Generates a single-sentence summary of a completed monitoring session.

    Uses the indexed ChromaDB frames for the session as context and sends
    them to an Ollama LLM with the exact prompt required by the spec.
    """

    def __init__(self, indexer: Optional[FrameIndexer] = None):
        # Accept an injected indexer (reuse the singleton) or create one
        self.indexer = indexer or FrameIndexer()
        self.llm = OllamaLLM(
            model=DRONE_AGENT_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
        )

    async def summarize_session(self, session_id: str) -> str:
        """Fetch session frames from ChromaDB and generate a ≤30-word summary.

        Args:
            session_id: The session whose frames to summarize.

        Returns:
            A one-sentence security summary string.
        """
        frames = self.indexer.get_session_frames(session_id)

        if not frames:
            return (
                "No observations recorded for this session — the drone "
                "was docked or no frames were indexed."
            )

        # Sort by timestamp so the summary reads chronologically
        frames.sort(key=lambda f: f["metadata"].get("timestamp", ""))

        # Build context string, prioritising alerted frames and trimming
        alerted = [
            f for f in frames if f["metadata"].get("alert_triggered", 0)
        ]
        normal  = [
            f for f in frames if not f["metadata"].get("alert_triggered", 0)
        ]

        # Put alerted events first for better summaries
        ordered = alerted + normal

        lines = []
        total_chars = 0
        for f in ordered:
            ts   = f["metadata"].get("timestamp", "")
            loc  = f["metadata"].get("location_label", "")
            desc = f["document"][:180]   # Trim very long descriptions
            line = f"{ts} [{loc}]: {desc}"
            if total_chars + len(line) > MAX_CONTEXT_CHARS:
                break
            lines.append(line)
            total_chars += len(line)

        context = "\n".join(lines)

        prompt = (
            "Given these security observations from a drone monitoring session:\n"
            f"{context}\n\n"
            "Write a single sentence that summarizes the most important security findings "
            "from this session. Include key objects, locations, and any alerts triggered. "
            "Keep it under 30 words."
        )

        try:
            response = await self.llm.ainvoke(prompt)
            summary = response.strip()
            # Enforce ≤30 words as per spec
            words = summary.split()
            if len(words) > 35:
                summary = " ".join(words[:30]) + "..."
            return summary
        except Exception as exc:
            logger.error("Summarizer LLM error: %s", exc)
            # Deterministic fallback
            locs    = list({f["metadata"].get("location_label", "") for f in frames})
            n_alert = len(alerted)
            return (
                f"Session recorded {len(frames)} frames across {', '.join(locs[:3])}; "
                f"{n_alert} frame(s) triggered security alerts."
            )
