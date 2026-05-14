import os
import logging
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

logger = logging.getLogger(__name__)

CHROMA_PERSIST_PATH = os.getenv("CHROMA_PERSIST_PATH", "./chroma_db")

# Singleton client — shared across all FrameIndexer instances in the process
# to avoid "cannot open DB from multiple handles" issues.
# Tests override this by setting _chroma_client = None + new CHROMA_PERSIST_PATH.
_chroma_client: Optional[chromadb.PersistentClient] = None


def _get_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        path = os.getenv("CHROMA_PERSIST_PATH", "./chroma_db")
        if path == ":memory:":
            _chroma_client = chromadb.EphemeralClient(
                settings=chromadb.config.Settings(anonymized_telemetry=False, allow_reset=True),
            )
        else:
            _chroma_client = chromadb.PersistentClient(
                path=path,
                settings=chromadb.config.Settings(anonymized_telemetry=False, allow_reset=True),
            )
    return _chroma_client


class FrameIndexer:
    """Stores and queries drone frame observations in ChromaDB.

    Schema (per document):
        id:                        "frame_{session_id}_{number}"
        document:                  VLM natural-language description
        embedding:                 auto (all-MiniLM-L6-v2 via DefaultEmbeddingFunction)
        metadata.frame_id:         str
        metadata.timestamp:        ISO UTC string
        metadata.time_of_day:      "day" | "night" | "dawn" | "dusk"
        metadata.location_label:   str  e.g. "main_gate"
        metadata.drone_lat:        float
        metadata.drone_lon:        float
        metadata.altitude_m:       float
        metadata.objects_detected: comma-separated e.g. "truck,person"
        metadata.alert_triggered:  bool (stored as int 0/1 for ChromaDB compat)
        metadata.session_id:       str
        metadata.scene_id:         str
    """

    def __init__(self, collection_name: str = "drone_frames"):
        self.client = _get_client()
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------ #
    # Write                                                                #
    # ------------------------------------------------------------------ #

    def index_frame(
        self,
        frame_id: str,
        description: str,
        telemetry: dict,
        alert_triggered: bool = False,
    ) -> bool:
        """Embed description and store frame in ChromaDB.

        Returns True on success, False if frame_id already exists.
        """
        # Guard: skip duplicate IDs (re-indexing same frame_id twice crashes)
        existing = self.collection.get(ids=[frame_id])
        if existing["ids"]:
            logger.warning("Frame %s already indexed — skipping.", frame_id)
            return False

        objects = self._extract_objects(description)

        metadata = {
            "frame_id":        frame_id,
            "timestamp":       telemetry.get("timestamp", ""),
            "time_of_day":     telemetry.get("time_of_day", "day"),
            "location_label":  telemetry.get("location_label", "unknown"),
            "drone_lat":       float(telemetry.get("drone_lat", 0.0)),
            "drone_lon":       float(telemetry.get("drone_lon", 0.0)),
            "altitude_m":      float(telemetry.get("altitude_m", 0.0)),
            "objects_detected": ",".join(objects),
            # ChromaDB metadata values must be str | int | float | bool.
            # Use int so filtering works reliably across ChromaDB versions.
            "alert_triggered": 1 if alert_triggered else 0,
            "session_id":      telemetry.get("session_id", "default"),
            "scene_id":        telemetry.get("scene_id", "unknown"),
        }

        try:
            self.collection.add(
                ids=[frame_id],
                documents=[description],
                metadatas=[metadata],
            )
            return True
        except Exception as exc:
            logger.error("ChromaDB add error for %s: %s", frame_id, exc)
            return False

    # ------------------------------------------------------------------ #
    # Read — semantic search                                               #
    # ------------------------------------------------------------------ #

    def query_by_text(self, query: str, n: int = 5) -> List[dict]:
        """Semantic similarity search over VLM descriptions."""
        if self.collection.count() == 0:
            return []
        # Clamp n to available docs
        n = min(n, self.collection.count())
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n,
            )
            return self._format_query_results(results)
        except Exception as exc:
            logger.error("query_by_text error: %s", exc)
            return []

    # ------------------------------------------------------------------ #
    # Read — metadata filters                                              #
    # ------------------------------------------------------------------ #

    def query_by_time_range(self, start_iso: str, end_iso: str) -> List[dict]:
        """Return frames whose timestamp falls within [start_iso, end_iso].

        ChromaDB does NOT support $gte/$lte on string metadata fields.
        We fetch all frames and filter in Python using ISO string comparison
        (ISO-8601 strings sort lexicographically, so this is safe).
        """
        all_frames = self.get_all_frames()
        filtered = []
        for f in all_frames:
            ts = f["metadata"].get("timestamp", "")
            if ts and start_iso <= ts <= end_iso:
                filtered.append(f)
        return filtered

    def query_by_object(self, object_type: str) -> List[dict]:
        """Return frames where objects_detected contains the given object type.

        Always uses Python-side filtering for maximum ChromaDB version
        compatibility ($contains operator support is unreliable across versions).
        """
        return self._query_by_object_fallback(object_type)

    def _query_by_object_fallback(self, object_type: str) -> List[dict]:
        """Python-side filtering when ChromaDB $contains is unavailable."""
        all_frames = self.get_all_frames()
        obj_lower = object_type.lower()
        return [
            f for f in all_frames
            if obj_lower in f["metadata"].get("objects_detected", "").lower()
            or obj_lower in f["document"].lower()
        ]

    def query_by_location(self, location: str) -> List[dict]:
        """Return frames matching a specific location_label."""
        try:
            results = self.collection.get(
                where={"location_label": {"$eq": location}}
            )
            return self._format_get_results(results)
        except Exception as exc:
            logger.error("query_by_location error: %s", exc)
            return []

    def query_alerted_frames(self) -> List[dict]:
        """Return all frames that triggered at least one alert."""
        try:
            results = self.collection.get(
                where={"alert_triggered": {"$eq": 1}}
            )
            return self._format_get_results(results)
        except Exception as exc:
            logger.error("query_alerted_frames error: %s", exc)
            return []

    def get_session_frames(self, session_id: str) -> List[dict]:
        """Return all frames belonging to a specific session."""
        try:
            results = self.collection.get(
                where={"session_id": {"$eq": session_id}}
            )
            return self._format_get_results(results)
        except Exception as exc:
            logger.error("get_session_frames error: %s", exc)
            return []

    def get_frame_by_id(self, frame_id: str) -> Optional[dict]:
        """Return a single frame dict by its frame_id, or None."""
        try:
            results = self.collection.get(ids=[frame_id])
            formatted = self._format_get_results(results)
            return formatted[0] if formatted else None
        except Exception as exc:
            logger.error("get_frame_by_id error: %s", exc)
            return None

    def get_all_frames(self) -> List[dict]:
        """Return every indexed frame (use sparingly on large collections)."""
        try:
            results = self.collection.get()
            return self._format_get_results(results)
        except Exception as exc:
            logger.error("get_all_frames error: %s", exc)
            return []

    def count(self) -> int:
        """Total number of indexed frames."""
        return self.collection.count()

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_objects(description: str) -> List[str]:
        """Extract known object types from a VLM description string."""
        desc_lower = description.lower()
        known = ["truck", "person", "car", "van", "forklift", "vehicle", "sedan", "guard"]
        return [obj for obj in known if obj in desc_lower]

    @staticmethod
    def _format_query_results(results: dict) -> List[dict]:
        """Convert ChromaDB .query() response into list of dicts."""
        if not results.get("ids") or not results["ids"][0]:
            return []
        formatted = []
        for i, doc_id in enumerate(results["ids"][0]):
            formatted.append({
                "id":       doc_id,
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": (results["distances"][0][i]
                             if results.get("distances") else None),
            })
        return formatted

    @staticmethod
    def _format_get_results(results: dict) -> List[dict]:
        """Convert ChromaDB .get() response into list of dicts."""
        if not results.get("ids"):
            return []
        formatted = []
        for i, doc_id in enumerate(results["ids"]):
            formatted.append({
                "id":       doc_id,
                "document": results["documents"][i] if results.get("documents") else "",
                "metadata": results["metadatas"][i] if results.get("metadatas") else {},
            })
        return formatted


if __name__ == "__main__":
    idx = FrameIndexer()
    print(f"Total frames indexed: {idx.count()}")
