import asyncio
import os
import json
import logging
import base64
from io import BytesIO
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .models import (
    SessionStatus, SessionStopResponse,
    SummaryResponse, QARequest, QAResponse,
    FrameListResponse, AlertListResponse, FrameDetailResponse,
    Alert, SecurityEvent,
)
from .frame_simulator import FrameSimulator
from .vlm_processor import VLMProcessor
from .frame_indexer import FrameIndexer
from .alert_engine import AlertEngine
from .security_agent import SecurityAgent
from .summarizer import SessionSummarizer
from .qa_agent import QAAgent
from .video_simulator import VideoSimulator

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# App & CORS                                                           #
# ------------------------------------------------------------------ #
app = FastAPI(
    title="Drone Security Analyst Agent API",
    version="1.0.0",
    description="Real-time drone security monitoring with VLM, ChromaDB, and LangChain",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
# Singleton service instances (one DB handle per process)             #
# ------------------------------------------------------------------ #
simulator  = FrameSimulator()
vlm        = VLMProcessor()
indexer    = FrameIndexer()                    # shared instance
alert_engine = AlertEngine()
agent      = SecurityAgent()
summarizer = SessionSummarizer(indexer=indexer)   # reuse same indexer
qa_agent   = QAAgent(indexer=indexer)             # reuse same indexer
video_sim  = VideoSimulator()                     # checks for demo.mp4

EVENTS_FILE = Path(os.getenv("EVENTS_FILE", "events.jsonl")).resolve()
ALERTS_FILE = Path(os.getenv("ALERTS_FILE", "alerts.jsonl")).resolve()
FRAME_INTERVAL_SEC = float(os.getenv("FRAME_INTERVAL_SEC", "1"))
DRONE_AGENT_TURBO = os.getenv("DRONE_AGENT_TURBO", "true").lower() == "true"

# ------------------------------------------------------------------ #
# Session state                                                        #
# ------------------------------------------------------------------ #
active_session: Optional[dict] = None
session_task:   Optional[asyncio.Task] = None
session_alert_count: int = 0
session_frame_count: int = 0

# ------------------------------------------------------------------ #
# WebSocket connection manager                                         #
# ------------------------------------------------------------------ #
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)
        logger.info("WS client connected. Total: %d", len(self.active))

    def disconnect(self, websocket: WebSocket):
        self.active.remove(websocket)
        logger.info("WS client disconnected. Total: %d", len(self.active))

    async def broadcast(self, message: dict):
        dead: List[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)

manager = ConnectionManager()

# ------------------------------------------------------------------ #
# Frame persistence helpers                                            #
# ------------------------------------------------------------------ #

def _append_alerts(alerts: List[Alert]) -> None:
    """Append alert objects to alerts.jsonl for GET /alerts endpoint."""
    if not alerts:
        return
    try:
        with open(ALERTS_FILE, "a", encoding="utf-8") as fh:
            for alert in alerts:
                fh.write(alert.model_dump_json() + "\n")
    except IOError as exc:
        logger.error("Failed to write alerts: %s", exc)


def _read_jsonl(filepath: Path) -> List[dict]:
    """Read all lines from a .jsonl file, newest first."""
    if not filepath.exists():
        return []
    lines = []
    with open(filepath, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    lines.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return list(reversed(lines))


# ------------------------------------------------------------------ #
# Monitoring loop                                                      #
# ------------------------------------------------------------------ #

async def monitoring_loop(session_id: str) -> None:
    global active_session, session_alert_count, session_frame_count

    logger.info("Monitoring loop started — session: %s", session_id)
    
    # Use video simulator if video file is present, otherwise fallback to scene simulator
    if video_sim.cap:
        logger.info("Streaming from video file...")
        max_frames = 100 # Default to 100 frames for a session
        frames_to_process = range(max_frames)
    else:
        logger.info("Streaming from synthetic scenes...")
        frames_to_process = simulator.scenes.keys()

    for frame_idx, source_id in enumerate(frames_to_process):
        # Check stop signal
        if not active_session or active_session["status"] == "stopped":
            break

        # ── 1. Generate/Extract frame ──────────────────────────────────────
        if video_sim.cap:
            res = video_sim.get_frame(frame_idx)
            if not res: break
            img, telemetry = res
            scene_id = f"VIDEO_{frame_idx:03d}"
        else:
            scene_id = source_id
            img, telemetry = simulator.generate_frame(scene_id, session_id, frame_idx)

        # ── 2. VLM perception ─────────────────────────────────────
        logger.info(f"[DEBUG] Step 2: Calling VLM (LLava) for frame {frame_idx}...")
        description = await vlm.describe_frame(img, telemetry)
        logger.info(f"[DEBUG] VLM Result: {description[:50]}...")

        # ── 3. Build visit history for ALERT_003 ──────────────────
        logger.info(f"[DEBUG] Step 3: Building visit history...")
        session_frames_so_far = indexer.get_session_frames(session_id)
        visit_history: dict = {}
        for vf in session_frames_so_far:
            for obj in vf["metadata"].get("objects_detected", "").split(","):
                obj = obj.strip()
                if obj:
                    visit_history[obj] = visit_history.get(obj, 0) + 1

        # ── 4. Alert evaluation ────────────────────────────────────
        alerts = alert_engine.evaluate(description, telemetry, visit_history)
        threat_level = alert_engine.get_threat_level(alerts)

        # ── 5. Persist alerts to alerts.jsonl ─────────────────────
        _append_alerts(alerts)
        session_alert_count += len(alerts)

        # ── 6. LangChain agent (deeper reasoning + event logging) ──
        if DRONE_AGENT_TURBO:
            logger.info(f"[TURBO] Skipping agent reasoning for speed. Writing fallback event.")
            await agent._write_fallback_event(description, telemetry)
        else:
            logger.info(f"[DEBUG] Step 6: Calling Security Agent (Qwen)...")
            await agent.process_frame(description, telemetry)
            logger.info(f"[DEBUG] Step 6: Security Agent processing complete.")

        # ── 7. Index frame in ChromaDB ────────────────────────────
        logger.info(f"[DEBUG] Step 7: Indexing frame {frame_idx} in ChromaDB...")
        try:
            indexer.index_frame(
                telemetry["frame_id"],
                description,
                telemetry,
                alert_triggered=len(alerts) > 0,
            )
        except Exception as e:
            logger.error(f"[DEBUG] ChromaDB Indexing Error: {e}")
        
        session_frame_count += 1

        # ── 8. Build base64 thumbnail for WebSocket payload ───────
        logger.info(f"[DEBUG] Step 8: Encoding image for broadcast...")
        buf = BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # ── 9. Broadcast WebSocket event ──────────────────────────
        logger.info(f"[DEBUG] Step 9: BROADCASTING frame {frame_idx} to {len(manager.active)} clients...")
        await manager.broadcast({
            "event":       "frame_processed",
            "frame_id":    telemetry["frame_id"],
            "scene_id":    scene_id,
            "timestamp":   telemetry["timestamp"],
            "description": description,
            "telemetry":   telemetry,
            "alerts":      [a.model_dump() for a in alerts],
            "threat_level": threat_level,
            "frame_b64":   img_b64,    # PNG thumbnail for Live Feed
        })

        await asyncio.sleep(FRAME_INTERVAL_SEC)

    # Session complete
    if active_session:
        active_session["status"] = "stopped"
    logger.info(
        "Session %s complete — %d frames, %d alerts.",
        session_id, session_frame_count, session_alert_count,
    )
    # Broadcast session end event
    await manager.broadcast({
        "event":       "session_stopped",
        "session_id":  session_id,
        "total_frames": session_frame_count,
        "alerts_count": session_alert_count,
    })


# ------------------------------------------------------------------ #
# REST endpoints                                                       #
# ------------------------------------------------------------------ #

@app.get("/", tags=["Health"])
async def health_check():
    """API health check."""
    return {
        "status":  "ok",
        "version": "1.0.0",
        "session": active_session["session_id"] if active_session else None,
    }


@app.post("/session/start", response_model=SessionStatus, tags=["Session"])
async def start_session():
    """Start a new monitoring session. Returns 409 if one is already active."""
    global active_session, session_task, session_alert_count, session_frame_count

    if active_session and active_session["status"] == "active":
        raise HTTPException(409, "A session is already active.")

    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_alert_count = 0
    session_frame_count = 0
    active_session = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat() + "Z",
        "status":     "active",
        "total_frames": 0,
        "alerts_count": 0,
    }
    session_task = asyncio.create_task(monitoring_loop(session_id))
    logger.info("Session started: %s", session_id)
    return active_session


@app.post("/session/stop", response_model=SessionStopResponse, tags=["Session"])
async def stop_session():
    """Stop the active session and trigger an LLM summary."""
    global active_session

    if not active_session:
        raise HTTPException(400, "No active session to stop.")

    active_session["status"]       = "stopped"
    active_session["total_frames"] = session_frame_count
    active_session["alerts_count"] = session_alert_count

    # Generate session summary via Summarizer
    summary_text = "Summary unavailable."
    try:
        summary_text = await summarizer.summarize_session(active_session["session_id"])
    except Exception as exc:
        logger.error("Summarizer error on stop: %s", exc)

    return SessionStopResponse(
        session_id=active_session["session_id"],
        started_at=active_session["started_at"],
        status="stopped",
        summary=summary_text,
        total_frames=session_frame_count,
        alerts_count=session_alert_count,
    )


@app.get("/frames", response_model=FrameListResponse, tags=["Frames"])
async def list_frames(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Return paginated list of all indexed frames, optionally filtered by session."""
    if session_id:
        frames = indexer.get_session_frames(session_id)
    else:
        frames = indexer.get_all_frames()

    total = len(frames)
    start = (page - 1) * page_size
    end   = start + page_size
    return FrameListResponse(frames=frames[start:end], total=total, page=page)


@app.get("/frames/{frame_id}", response_model=FrameDetailResponse, tags=["Frames"])
async def get_frame(frame_id: str):
    """Return full data for a single frame by its ID."""
    frame = indexer.get_frame_by_id(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame '{frame_id}' not found.")

    # Also attach any alerts from alerts.jsonl that reference this frame
    all_alerts = _read_jsonl(ALERTS_FILE)
    frame_alerts = [a for a in all_alerts if a.get("frame_id") == frame_id]

    return FrameDetailResponse(
        frame_id=frame["id"],
        description=frame["document"],
        telemetry=frame["metadata"],
        alerts=frame_alerts,
        metadata=frame["metadata"],
    )


@app.get("/alerts", tags=["Alerts"])
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL|HIGH|MEDIUM|LOW"),
):
    """Return all logged alerts, optionally filtered by severity."""
    all_alerts = _read_jsonl(ALERTS_FILE)

    if severity:
        all_alerts = [
            a for a in all_alerts
            if a.get("severity", "").upper() == severity.upper()
        ]

    return {"alerts": all_alerts, "total": len(all_alerts)}


@app.get("/events", tags=["Events"])
async def get_events(
    limit: int = Query(50, ge=1, le=200),
    threat_level: Optional[str] = Query(None, description="Filter by threat_level"),
):
    """Return all security events logged by the agent, newest first."""
    events = _read_jsonl(EVENTS_FILE)

    if threat_level:
        events = [
            e for e in events
            if e.get("threat_level", "").upper() == threat_level.upper()
        ]

    return {"events": events[:limit], "total": len(events)}


@app.post("/qa", response_model=QAResponse, tags=["Intelligence"])
async def ask_qa(request: QARequest):
    """Submit a natural-language question to the Q&A agent."""
    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty.")

    answer_text, sources = await qa_agent.answer(request.question)
    return QAResponse(
        question=request.question,
        answer=answer_text,
        sources=sources,
    )


@app.get("/summary", response_model=SummaryResponse, tags=["Intelligence"])
async def get_summary(
    session_id: Optional[str] = Query(None, description="Session ID to summarise (defaults to latest)"),
):
    """Generate a one-sentence LLM summary of a monitoring session."""
    sid = session_id or (active_session["session_id"] if active_session else None)
    if not sid:
        raise HTTPException(400, "No session ID provided and no session has been run.")

    summary_text = await summarizer.summarize_session(sid)
    return SummaryResponse(
        summary=summary_text,
        session_id=sid,
        generated_at=datetime.now().isoformat() + "Z",
    )


# ------------------------------------------------------------------ #
# WebSocket endpoint                                                   #
# ------------------------------------------------------------------ #

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """WebSocket endpoint for real-time frame event streaming."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive — client sends pings, we ignore them
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ------------------------------------------------------------------ #
# Entry point                                                          #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
