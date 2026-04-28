"""
utils.py

Utility functions for the LLM logging system.
Handles PII masking and helper operations.
"""

import re


def mask_pii(text: str) -> str:
    """
    Masks sensitive information like emails and phone numbers.

    Args:
        text (str): Input text containing possible PII

    Returns:
        str: Text with masked PII
    """
    if not text:
        return text

    # Mask emails
    text = re.sub(r'\S+@\S+', '[EMAIL_REDACTED]', text)

    # Mask phone numbers (simple 10-digit pattern)
    text = re.sub(r'\b\d{10}\b', '[PHONE_REDACTED]', text)

    return text