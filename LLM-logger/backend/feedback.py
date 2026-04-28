"""
feedback.py

Handles user feedback for LLM responses.
"""

import json
from datetime import datetime


FEEDBACK_FILE = "../data/feedback.jsonl"


def log_feedback(response_id: str, rating: str, comment: str = "") -> dict:
    """
    Logs user feedback.

    Args:
        response_id (str): ID of the LLM response
        rating (str): 'upvote' or 'downvote'
        comment (str, optional): Additional feedback

    Returns:
        dict: Feedback data
    """
    if rating not in ["upvote", "downvote"]:
        raise ValueError("Rating must be 'upvote' or 'downvote'")

    feedback = {
        "response_id": response_id,
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(feedback) + "\n")

    return feedback