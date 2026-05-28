# app/intent.py
# Detects the user's intent category from their message.
# Uses keyword matching first (fast path), then falls back to AI classification.

import re
from typing import Tuple


class IntentDetector:
    """
    Classifies user messages into predefined intent categories.

    Intent categories:
    - greeting        : Hi, hello, hey
    - farewell        : Bye, goodbye, see you
    - product_info    : Questions about products/services
    - technical_support : Technical help requests
    - billing         : Payment, invoice, subscription questions
    - complaint       : Dissatisfaction or issue reporting
    - general_query   : Any other question
    - unknown         : Cannot be classified
    """

    # Keyword map: intent -> list of trigger words/phrases
    INTENT_KEYWORDS = {
        "greeting": [
            "hello", "hi", "hey", "good morning", "good afternoon",
            "good evening", "howdy", "greetings", "what's up", "sup"
        ],
        "farewell": [
            "bye", "goodbye", "see you", "later", "take care",
            "farewell", "ciao", "ttyl", "have a good day"
        ],
        "product_info": [
            "what is", "tell me about", "describe", "features", "product",
            "service", "offer", "plan", "package", "pricing", "how does",
            "what can you do", "capabilities"
        ],
        "technical_support": [
            "error", "bug", "issue", "problem", "not working", "broken",
            "fix", "help me", "how to", "trouble", "crash", "failed",
            "cannot", "can't", "doesn't work", "setup", "install", "configure"
        ],
        "billing": [
            "invoice", "payment", "bill", "charge", "refund", "subscription",
            "cancel", "upgrade", "downgrade", "receipt", "cost", "price",
            "how much", "discount", "coupon", "trial"
        ],
        "complaint": [
            "unhappy", "disappointed", "frustrated", "angry", "bad",
            "worst", "terrible", "awful", "complaint", "unacceptable",
            "not satisfied", "poor service", "rude", "slow"
        ],
    }

    def detect(self, message: str) -> Tuple[str, float]:
        """
        Detects the intent of a user message using keyword matching.

        Args:
            message: The user's cleaned input string.

        Returns:
            A tuple of (intent_label, confidence_score).
            confidence_score is 1.0 for keyword match, 0.5 for fallback.
        """
        msg_lower = message.lower()

        # Score each intent based on keyword hits
        scores: dict[str, int] = {intent: 0 for intent in self.INTENT_KEYWORDS}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    scores[intent] += 1

        # Find the best scoring intent
        best_intent = max(scores, key=lambda k: scores[k])
        best_score = scores[best_intent]

        if best_score > 0:
            # Normalize confidence: cap at 1.0
            confidence = min(1.0, best_score * 0.35)
            return best_intent, confidence

        # No keyword matched → fall back to general_query
        return "general_query", 0.5

    def detect_with_context(self, message: str, history: list = None) -> dict:
        """
        Detects intent and returns a structured result dictionary.

        Args:
            message: Current user message.
            history: Optional list of previous messages (for future context use).

        Returns:
            Dict with 'intent' and 'confidence' keys.
        """
        intent, confidence = self.detect(message)
        return {
            "intent": intent,
            "confidence": round(confidence, 2)
        }
