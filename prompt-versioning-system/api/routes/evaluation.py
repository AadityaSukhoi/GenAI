"""
API routes for prompt evaluation.
"""

from fastapi import APIRouter
from services.evaluation_service import evaluate

router = APIRouter()


@router.post("/")
def evaluate_prompts(prompt1: str, prompt2: str):
    return evaluate(prompt1, prompt2)