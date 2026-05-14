import os
import json
import logging
import re
from typing import Optional, Tuple, List
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from .frame_indexer import FrameIndexer

load_dotenv()
logger = logging.getLogger(__name__)

DRONE_AGENT_MODEL = os.getenv("DRONE_AGENT_MODEL", "qwen2:7b")
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

_indexer: Optional[FrameIndexer] = None


def _get_indexer() -> FrameIndexer:
    global _indexer
    if _indexer is None:
        _indexer = FrameIndexer()
    return _indexer


# ------------------------------------------------------------------ #
# Tools                                                                #
# ------------------------------------------------------------------ #

@tool
def search_observations(query: str) -> str:
    """Search drone monitoring observations semantically.
    Returns the most relevant frame descriptions with timestamps and locations."""
    results = _get_indexer().query_by_text(query, n=5)
    if not results:
        return "No matching observations found in the indexed history."
    slim = [
        {
            "frame_id":  r["id"],
            "timestamp": r["metadata"].get("timestamp", ""),
            "location":  r["metadata"].get("location_label", ""),
            "summary":   r["document"][:200],
        }
        for r in results
    ]
    return json.dumps(slim, indent=2)


@tool
def count_visits_by_object(object_type: str) -> str:
    """Count how many frames contain a specific object type across the whole session.
    Use this for 'how many times did the truck enter?'"""
    results = _get_indexer().query_by_object(object_type)
    if not results:
        return f"No frames found containing '{object_type}'."
    visits: dict = {}
    for r in results:
        loc = r["metadata"].get("location_label", "unknown")
        ts  = r["metadata"].get("timestamp", "")
        visits.setdefault(loc, []).append(ts)
    lines = [f"- {loc}: {len(ts_list)} visit(s) at {', '.join(ts_list)}"
             for loc, ts_list in visits.items()]
    total = sum(len(v) for v in visits.values())
    return f"Total {total} frame(s) with '{object_type}':\n" + "\n".join(lines)


@tool
def get_critical_alerts() -> str:
    """Retrieve all frames that triggered security alerts."""
    results = _get_indexer().query_alerted_frames()
    if not results:
        return "No alerts were triggered during this session."
    items = [
        f"[{r['metadata'].get('timestamp','')}] "
        f"{r['metadata'].get('location_label','')}: {r['document'][:180]}"
        for r in results
    ]
    return "\n".join(items)


# ------------------------------------------------------------------ #
# System prompt                                                        #
# ------------------------------------------------------------------ #

_QA_SYSTEM_PROMPT = """You are a Security Intelligence Assistant with access to a drone's observation history.
Answer questions clearly and concisely. Always cite the frame IDs you used as sources.
Use the available tools to search observation history before answering."""


# ------------------------------------------------------------------ #
# QAAgent                                                              #
# ------------------------------------------------------------------ #

class QAAgent:
    """LangGraph ReAct agent for Q&A over indexed drone observations."""

    def __init__(self, indexer: Optional[FrameIndexer] = None):
        global _indexer
        if indexer is not None:
            _indexer = indexer

        self.llm = ChatOllama(
            model=DRONE_AGENT_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )
        self.tools = [search_observations, count_visits_by_object, get_critical_alerts]
        self.graph = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=_QA_SYSTEM_PROMPT,
        )

    async def answer(self, question: str) -> Tuple[str, List[str]]:
        """Answer a natural language question about the indexed session history.

        Returns:
            (answer_text, list_of_source_frame_ids)
        """
        try:
            result = await self.graph.ainvoke(
                {"messages": [HumanMessage(content=question)]}
            )
            answer_text = result["messages"][-1].content
            # Extract frame IDs from the answer text
            source_ids = list(set(re.findall(r"frame_[\w]+_\d+", answer_text)))
            if not source_ids:
                hits = _get_indexer().query_by_text(question, n=3)
                source_ids = [h["id"] for h in hits]
            return answer_text, source_ids
        except Exception as exc:
            logger.error("QAAgent error: %s", exc)
            return await self._retrieval_fallback(question)

    async def _retrieval_fallback(self, question: str) -> Tuple[str, List[str]]:
        """Pure retrieval answer without LLM synthesis."""
        results = _get_indexer().query_by_text(question, n=3)
        if not results:
            return (
                "I could not find relevant observations in the indexed history.",
                [],
            )
        lines = [
            f"[{r['metadata'].get('timestamp','')}] "
            f"{r['metadata'].get('location_label','')}: {r['document'][:200]}"
            for r in results
        ]
        answer = "Based on indexed observations:\n" + "\n".join(lines)
        sources = [r["id"] for r in results]
        return answer, sources
