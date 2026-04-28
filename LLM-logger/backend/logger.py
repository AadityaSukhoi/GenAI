"""
logger.py

Handles structured logging of LLM interactions.
"""

import json
import time
import uuid
from datetime import datetime
from utils import mask_pii


LOG_FILE = "../data/logs.jsonl"


def log_llm_interaction(prompt: str, response: str, model: str, latency: float) -> dict:
    """
    Logs an LLM interaction with metadata.

    Args:
        prompt (str): User input
        response (str): Model output
        model (str): Model name

    Returns:
        dict: Logged interaction data
    """
    log = {
        "id": str(uuid.uuid4()),
        "prompt": mask_pii(prompt),
        "response": mask_pii(response),
        "model": model,
        "latency_ms": latency,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

    return log