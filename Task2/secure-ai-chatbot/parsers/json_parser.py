# parsers/json_parser.py
# Parses and validates AI model responses into structured JSON format.
# Ensures the output always contains the required fields.

import json
import re
from typing import Optional


class JSONParser:
    """
    Extracts, parses, and validates JSON from raw AI response strings.

    The chatbot always returns JSON with:
    {
        "intent": str,
        "risk_level": str,
        "response": str
    }

    This parser handles cases where the AI wraps JSON in markdown code blocks
    or adds extra text around the JSON object.
    """

    # Required fields in every valid chatbot response
    REQUIRED_FIELDS = {"intent", "risk_level", "response"}

    # Valid risk level values
    VALID_RISK_LEVELS = {"low", "medium", "high"}

    def parse(self, raw_text: str) -> Optional[dict]:
        """
        Attempts to extract and validate a JSON object from raw AI output.

        Args:
            raw_text: The raw string returned by the AI model.

        Returns:
            A validated dict if successful, or None on failure.
        """
        if not raw_text or not raw_text.strip():
            return None

        # Step 1: Try direct JSON parse
        result = self._try_parse(raw_text.strip())
        if result:
            return result

        # Step 2: Extract JSON from markdown code fences (```json ... ```)
        extracted = self._extract_from_codeblock(raw_text)
        if extracted:
            result = self._try_parse(extracted)
            if result:
                return result

        # Step 3: Extract first {...} block using regex
        extracted = self._extract_json_block(raw_text)
        if extracted:
            result = self._try_parse(extracted)
            if result:
                return result

        return None

    def _try_parse(self, text: str) -> Optional[dict]:
        """
        Tries to JSON-decode a string and validate required fields.

        Args:
            text: Clean JSON string candidate.

        Returns:
            Validated dict or None.
        """
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return self._validate(data)
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    def _extract_from_codeblock(self, text: str) -> Optional[str]:
        """
        Strips markdown code fence wrappers like ```json ... ```.

        Args:
            text: Raw text possibly containing a markdown code block.

        Returns:
            The content inside the code fence, or None.
        """
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_json_block(self, text: str) -> Optional[str]:
        """
        Finds the first complete {...} JSON block in a string.

        Args:
            text: Raw text that may contain embedded JSON.

        Returns:
            The first {...} substring, or None.
        """
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]
        return None

    def _validate(self, data: dict) -> Optional[dict]:
        """
        Ensures the parsed dict contains all required fields with valid values.

        Args:
            data: Parsed JSON dictionary.

        Returns:
            Cleaned/normalized dict, or None if critical fields are missing.
        """
        # All required fields must exist
        missing = self.REQUIRED_FIELDS - data.keys()
        if missing:
            return None

        # Normalize risk_level to a valid value
        risk = str(data.get("risk_level", "low")).lower()
        if risk not in self.VALID_RISK_LEVELS:
            risk = "low"

        # Ensure string types for all fields
        return {
            "intent": str(data.get("intent", "unknown")).strip(),
            "risk_level": risk,
            "response": str(data.get("response", "")).strip()
        }

    def build_fallback(self, intent: str = "unknown",
                       risk_level: str = "low",
                       response: str = "I was unable to process your request. Please try again.") -> dict:
        """
        Builds a safe fallback response when parsing fails.

        Args:
            intent: Intent label string.
            risk_level: Risk level string.
            response: Human-readable response message.

        Returns:
            A valid chatbot response dict.
        """
        return {
            "intent": intent,
            "risk_level": risk_level,
            "response": response
        }
