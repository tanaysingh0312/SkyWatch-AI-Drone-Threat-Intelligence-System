from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str         # e.g., ALERT_001 .. ALERT_008
    severity: str        # CRITICAL | HIGH | MEDIUM | LOW
    message: str
    frame_id: str
    timestamp: str       # ISO UTC
    location: str
    objects: List[str]
    acknowledged: bool = False


class SecurityEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    frame_id: str
    timestamp: str
    location: str
    vlm_description: str
    objects_detected: List[str]
    alerts_triggered: List[Alert]
    agent_summary: str
    threat_level: str    # NONE | LOW | MEDIUM | HIGH | CRITICAL
    recommended_action: str
    context_from_history: str


class FrameData(BaseModel):
    frame_id: str
    session_id: str
    timestamp: str
    description: str
    telemetry: Dict[str, Any]
    alerts: List[Alert]
    threat_level: str


class SessionStatus(BaseModel):
    session_id: str
    started_at: str
    status: str          # active | stopped
    total_frames: Optional[int] = 0
    alerts_count: Optional[int] = 0


class SessionStopResponse(BaseModel):
    session_id: str
    started_at: str
    status: str
    summary: Optional[str] = None
    total_frames: int = 0
    alerts_count: int = 0


class SummaryResponse(BaseModel):
    summary: str
    session_id: str
    generated_at: str


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]


class FrameListResponse(BaseModel):
    frames: List[Dict[str, Any]]
    total: int
    page: int = 1


class AlertListResponse(BaseModel):
    alerts: List[Alert]
    total: int


class FrameDetailResponse(BaseModel):
    frame_id: str
    description: str
    telemetry: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    metadata: Dict[str, Any]
