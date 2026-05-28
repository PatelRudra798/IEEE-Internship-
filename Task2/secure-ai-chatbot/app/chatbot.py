# app/chatbot.py
# Core chatbot engine implementing the ReAct-style workflow.
# It integrates safety checks, intent detection, the language model, and JSON parsing.

import httpx
import json
from typing import Dict, Any, Optional

from app.config import config
from app.safety import SafetyChecker
from app.intent import IntentDetector
from parsers.json_parser import JSONParser


class SecureChatbot:
    """
    The main orchestrator for the secure AI chatbot.

    Workflow:
    1. Safety check: Reject unsafe inputs immediately.
    2. Intent detection: Categorize the user's request.
    3. LLM API Call: Send structured prompt to Gemini/OpenAI.
    4. JSON Parsing: Ensure the LLM output is strict, valid JSON.
    5. Return safe, structured JSON to the API layer.
    """

    def __init__(self):
        self.safety = SafetyChecker()
        self.intent_detector = IntentDetector()
        self.parser = JSONParser()

        # Load system prompts
        self.system_prompt = config.load_prompt("system_prompt.txt")
        self.response_prompt = config.load_prompt("response_prompt.txt")

    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Processes a user message end-to-end securely.

        Args:
            message: The raw user input string.

        Returns:
            Dict containing intent, risk_level, and response.
        """
        # Step 1: Safety Check
        safety_result = self.safety.check(message)
        if not safety_result["is_safe"]:
            return {
                "intent": "malicious_activity",
                "risk_level": safety_result["risk_level"],
                "response": "I cannot fulfill this request. " + safety_result["reason"]
            }

        # Step 2: Intent Detection (Fast local check)
        intent_data = self.intent_detector.detect_with_context(message)
        detected_intent = intent_data["intent"]

        # Step 3: LLM Integration (Drafting the response)
        try:
            llm_response_text = await self._call_llm(message, detected_intent)
        except Exception as e:
            print(f"[ERROR] LLM API failure: {e}")
            return self.parser.build_fallback(
                intent=detected_intent,
                response="The service is temporarily unavailable. Please try again later."
            )

        # Step 4: Output Parsing and Validation
        parsed_json = self.parser.parse(llm_response_text)

        if not parsed_json:
            print(f"[WARNING] Failed to parse LLM output: {llm_response_text}")
            return self.parser.build_fallback(
                intent=detected_intent,
                response="I encountered an internal error while structuring my response."
            )

        return parsed_json

    async def _call_llm(self, message: str, intent: str) -> str:
        """
        Sends the request to the configured LLM provider.
        Hides the internal chain-of-thought from the final output.
        """
        if config.PROVIDER == "gemini":
            return await self._call_gemini(message, intent)
        elif config.PROVIDER == "openai":
            return await self._call_openai(message, intent)
        else:
            raise ValueError(f"Unknown provider: {config.PROVIDER}")

    async def _call_gemini(self, message: str, intent: str) -> str:
        """Calls Google Gemini API."""
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
        
        # Construct the final prompt injecting the system instructions and intent
        full_prompt = f"{self.system_prompt}\n\nDetected Intent: {intent}\n\n{self.response_prompt}\n\nUser: {message}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.2, # Low temperature for more deterministic/professional output
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from Gemini response structure
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                print(f"[ERROR] Unexpected Gemini response format: {data}")
                return ""

    async def _call_openai(self, message: str, intent: str) -> str:
        """Calls OpenAI API."""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        full_prompt = f"Detected Intent: {intent}\n\n{self.response_prompt}"

        payload = {
            "model": config.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                print(f"[ERROR] Unexpected OpenAI response format: {data}")
                return ""
