# app/safety.py
# Implements AI safety guardrails: blocked keyword detection,
# prompt injection prevention, and risk level classification.

import re
from app.config import config


class SafetyChecker:
    """
    Scans user messages for unsafe content before they reach the AI model.

    Checks performed:
    - Blocked keyword detection (hacking, malware, phishing, etc.)
    - Prompt injection attempt detection
    - System prompt extraction attempts
    - Input length validation
    """

    # --- Blocked keyword categories ---
    BLOCKED_KEYWORDS = [
        # Hacking / Exploitation
        "hack", "hacking", "exploit", "exploit code", "zero-day", "sql injection",
        "xss", "cross-site scripting", "buffer overflow", "reverse shell",
        "privilege escalation", "rootkit", "keylogger",

        # Malware / Ransomware
        "malware", "ransomware", "trojan", "virus code", "worm", "spyware",
        "create virus", "write malware", "deploy ransomware",

        # Phishing / Social Engineering
        "phishing", "spear phishing", "fake login", "credential harvesting",
        "social engineering", "impersonate", "steal credentials",

        # Password / Admin Credentials
        "admin password", "root password", "bypass login", "brute force password",
        "crack password", "default credentials", "get admin access",

        # Illegal / Dangerous
        "ddos", "denial of service", "botnet", "dark web", "illegal",
        "make bomb", "build weapon",
    ]

    # --- Prompt injection patterns (regex) ---
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions?",
        r"forget\s+(all\s+)?(previous|above|prior)\s+instructions?",
        r"disregard\s+(all\s+)?(previous|above|prior)\s+instructions?",
        r"you\s+are\s+now\s+a\s+(different|new|evil|unrestricted)\s+(ai|bot|assistant)",
        r"pretend\s+(you\s+are|to\s+be)\s+(evil|unrestricted|jailbreak)",
        r"act\s+as\s+(if\s+you\s+have\s+no\s+)?(restrictions?|rules?|limits?)",
        r"do\s+anything\s+now",
        r"jailbreak",
        r"dan\s+mode",
        r"developer\s+mode\s+enabled",
        r"bypass\s+(safety|filter|restriction|guardrail)",
    ]

    # --- System prompt extraction attempts ---
    SYSTEM_PROMPT_EXTRACTION = [
        r"(show|reveal|print|output|tell\s+me|what\s+is)\s+(your|the)\s+system\s+prompt",
        r"(show|reveal|print|output)\s+(your|the)\s+(hidden|internal|secret)\s+instructions?",
        r"repeat\s+(everything|all)\s+(above|before|prior)",
        r"output\s+(your|the)\s+prompt",
        r"what\s+instructions?\s+(were|are)\s+you\s+given",
        r"ignore\s+instructions?\s+and\s+(tell|show|reveal)",
    ]

    def __init__(self):
        # Pre-compile all regex patterns for performance
        self._injection_re = [
            re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS
        ]
        self._extraction_re = [
            re.compile(p, re.IGNORECASE) for p in self.SYSTEM_PROMPT_EXTRACTION
        ]

    def check(self, message: str) -> dict:
        """
        Runs all safety checks on the user message.

        Args:
            message: Raw user input string.

        Returns:
            A dict with keys:
              - is_safe (bool): True if message passes all checks.
              - risk_level (str): "low", "medium", or "high".
              - reason (str): Human-readable explanation if blocked.
        """
        # 1. Length check
        if len(message) > config.MAX_INPUT_LENGTH:
            return self._block(
                config.RISK_LEVEL_MEDIUM,
                "Message exceeds maximum allowed length."
            )

        # 2. Empty message check
        if not message.strip():
            return self._block(
                config.RISK_LEVEL_LOW,
                "Message is empty."
            )

        msg_lower = message.lower()

        # 3. Blocked keyword detection
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in msg_lower:
                return self._block(
                    config.RISK_LEVEL_HIGH,
                    f"Message contains a blocked topic: '{keyword}'."
                )

        # 4. Prompt injection detection
        for pattern in self._injection_re:
            if pattern.search(message):
                return self._block(
                    config.RISK_LEVEL_HIGH,
                    "Prompt injection attempt detected."
                )

        # 5. System prompt extraction attempt detection
        for pattern in self._extraction_re:
            if pattern.search(message):
                return self._block(
                    config.RISK_LEVEL_HIGH,
                    "Attempt to extract internal instructions detected."
                )

        # All checks passed
        return {
            "is_safe": True,
            "risk_level": config.RISK_LEVEL_LOW,
            "reason": ""
        }

    @staticmethod
    def _block(risk_level: str, reason: str) -> dict:
        """Helper to build a blocked result dict."""
        return {
            "is_safe": False,
            "risk_level": risk_level,
            "reason": reason
        }
