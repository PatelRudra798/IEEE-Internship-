# Secure AI Chatbot - Product Requirements Document (PRD)

## 1. Overview
The Secure AI Chatbot is a backend REST API service built with FastAPI that provides conversational AI capabilities while strictly enforcing safety guardrails. It is designed to be used as a backend for professional customer service or enterprise applications where inappropriate content, hallucinations, and prompt injections must be blocked.

## 2. Objectives
- Provide a responsive, ReAct-style AI assistant using external LLMs (Gemini/OpenAI).
- Guarantee structured, parseable JSON output on every request.
- Ensure 100% adherence to safety guidelines, blocking all malicious intent.
- Hide internal processing ("Chain of Thought") from the end user to maintain a professional facade.

## 3. Target Audience
- Frontend developers building chat interfaces.
- Enterprise customers needing a safe, compliant AI solution.

## 4. Key Features
1. **Strict Guardrails**: Pre-checks all input for blocked keywords (hacking, malware, phishing) and prompt injection attempts.
2. **Intent Classification**: Automatically tags the intent of the user's message (e.g., technical support, billing) before processing.
3. **Structured Output**: The API strictly returns JSON containing the `intent`, `risk_level`, and the final `response`.
4. **Resilience**: Fallback mechanisms if the AI generates malformed output, ensuring the API never crashes or returns broken strings.

## 5. Non-Functional Requirements
- **Performance**: The API should respond within 2-5 seconds depending on the LLM provider.
- **Security**: No sensitive data or internal prompts are ever exposed in the API response.
- **Scalability**: Built on FastAPI, allowing for asynchronous, high-throughput request handling.
