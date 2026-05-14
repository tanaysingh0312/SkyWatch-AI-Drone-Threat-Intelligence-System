"""pytest conftest.py — shared fixtures and path configuration."""
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path so `from backend.xxx import` works
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import backend.frame_indexer as fi
import backend.security_agent as sa
import backend.qa_agent as qa

# Default to text_fallback VLM mode so tests run without Ollama/GPU
os.environ.setdefault("DRONE_VLM_MODE", "text_fallback")
os.environ["CHROMA_PERSIST_PATH"] = ":memory:"

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all module-level singletons before each test to ensure isolation."""
    # Reset ChromaDB client singleton
    if fi._chroma_client is not None:
        try:
            # If it's a persistent client, reset it (if allowed)
            fi._chroma_client.reset()
        except Exception:
            pass
    fi._chroma_client = None
    
    # Reset Agent singletons
    sa._alert_engine = None
    sa._indexer = None
    qa._indexer = None
    
    yield
    
    # Also reset after test
    fi._chroma_client = None
    sa._alert_engine = None
    sa._indexer = None
    qa._indexer = None
