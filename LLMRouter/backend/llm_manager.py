"""
LLM Manager for LLMRouter

Handles:
- Model initialization (Gemini, Mistral, Granite)
- Model selection (manual)
- Automatic routing based on query type
"""

import os
from typing import Tuple
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

# Load environment variables
load_dotenv()


class LLMManager:
    """
    Manages all LLMs and routing logic.
    """

    def __init__(self):
        """Initialize all available LLMs."""

        self.gemini: BaseChatModel | None = None
        self.mistral: BaseChatModel | None = None
        self.granite: BaseChatModel | None = None

        # -------------------------------
        # GEMINI INITIALIZATION
        # -------------------------------
        gemini_key = os.getenv("GEMINI_API_KEY")

        if gemini_key:
            self.gemini = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.3,
                google_api_key=gemini_key,  
            )
        else:
            print("[WARNING] GEMINI_API_KEY not found")

        # -------------------------------
        # MISTRAL INITIALIZATION (FIXED)
        # -------------------------------
        mistral_key = os.getenv("MISTRAL_API_KEY")

        if mistral_key:
            self.mistral = ChatMistralAI(
                model="mistral-small-latest",
                temperature=0.3,
                api_key=mistral_key,  
            )
        else:
            print("[WARNING] MISTRAL_API_KEY not found")

        # -------------------------------
        # GRANITE (OLLAMA)
        # -------------------------------
        try:
            self.granite = ChatOllama(
                model="granite3.2:8b",
                base_url="http://localhost:11434",
                temperature=0.3,
            )
        except Exception as e:
            print(f"[WARNING] Granite (Ollama) not available: {e}")

    # ============================================================
    # 🔀 AUTO ROUTING
    # ============================================================
    def route_query(self, query: str) -> Tuple[BaseChatModel, str]:
        """
        Automatically selects the best model.

        Rules:
        - Long / reasoning queries → Gemini
        - Short queries → Mistral
        - Medium queries → Granite
        """

        query_lower = query.lower()

        reasoning_keywords = [
            "explain",
            "why",
            "how",
            "analyze",
            "compare",
            "reason",
        ]

        is_reasoning = any(word in query_lower for word in reasoning_keywords)

        if len(query) > 200 or is_reasoning:
            return self.get_model("gemini")

        elif len(query) < 50:
            return self.get_model("mistral")

        else:
            return self.get_model("granite")

    # ============================================================
    # 🎯 MANUAL MODEL SELECTION
    # ============================================================
    def get_model(self, model_name: str) -> Tuple[BaseChatModel, str]:
        """
        Returns requested model.
        Falls back gracefully if unavailable.
        """

        if model_name == "gemini" and self.gemini:
            return self.gemini, "gemini"

        elif model_name == "mistral" and self.mistral:
            return self.mistral, "mistral"

        elif model_name == "granite" and self.granite:
            return self.granite, "granite"

        # -------------------------------
        # FALLBACK LOGIC
        # -------------------------------
        if self.gemini:
            return self.gemini, "gemini (fallback)"

        if self.mistral:
            return self.mistral, "mistral (fallback)"

        if self.granite:
            return self.granite, "granite (fallback)"

        raise ValueError(
            "No LLMs configured. Check API keys and Ollama connection."
        )