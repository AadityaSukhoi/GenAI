"""
Utility functions for scoring similarity.
"""

def similarity_score(output: str, expected: str) -> float:
    """
    Improved similarity using F1 score.
    """

    out_words = set(output.lower().split())
    exp_words = set(expected.lower().split())

    common = len(out_words & exp_words)

    if common == 0:
        return 0.0

    precision = common / len(out_words)
    recall = common / len(exp_words)

    return 2 * (precision * recall) / (precision + recall)