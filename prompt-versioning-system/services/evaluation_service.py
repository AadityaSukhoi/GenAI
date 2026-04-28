"""
Service for evaluating prompt versions using embedding-based similarity.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def load_dataset(path="data/test_dataset.json"):
    """
    Load evaluation dataset.
    """
    with open(path, "r") as f:
        return json.load(f)


def run_prompt(prompt: str, input_text: str):
    """
    Simulate LLM response (replace with real model later).
    """
    return f"{prompt} {input_text}"


def embedding_similarity(output: str, expected: str) -> float:
    """
    Compute cosine similarity between embeddings.
    """
    emb1 = model.encode(output, normalize_embeddings=True)
    emb2 = model.encode(expected, normalize_embeddings=True)

    return float(np.dot(emb1, emb2))  


def evaluate(prompt1: str, prompt2: str):
    """
    Compare two prompt versions using semantic similarity.
    """
    dataset = load_dataset()

    score1 = 0
    score2 = 0

    for item in dataset:
        input_text = item["input"]
        expected = item["expected"]

        # Generate outputs
        out1 = run_prompt(prompt1, input_text)
        out2 = run_prompt(prompt2, input_text)

        # Compute semantic similarity
        sim1 = embedding_similarity(out1, expected)
        sim2 = embedding_similarity(out2, expected)

        score1 += sim1
        score2 += sim2

    avg1 = score1 / len(dataset)
    avg2 = score2 / len(dataset)

    # 🔥 Threshold-based regression detection
    threshold = 0.05
    regression = avg2 < (avg1 - threshold)

    return {
        "prompt1_score": round(avg1, 4),
        "prompt2_score": round(avg2, 4),
        "regression": regression
    }