# Secure AI Chatbot - Functional Requirements Document (FRD)

## 1. System Architecture
The application follows a modular, object-oriented design:
- **API Layer (`app/main.py`)**: FastAPI application handling HTTP requests and CORS.
- **Orchestrator (`app/chatbot.py`)**: Manages the pipeline of safety checking, intent detection, LLM querying, and parsing.
- **Safety Module (`app/safety.py`)**: Regex and keyword-based filtering system.
- **Intent Module (`app/intent.py`)**: Keyword-scoring system for fast intent categorization.
- **Parser (`parsers/json_parser.py`)**: Extracts and validates JSON from raw LLM text.

## 2. API Specifications

### `POST /chat`
**Request Body**:
```json
{
  "message": "Hello, I need help resetting my password."
}
```
*Constraints*: `message` max length is 1000 characters.

**Success Response (200 OK)**:
```json
{
  "intent": "technical_support",
  "risk_level": "low",
  "response": "Hello! I can certainly help you with that. Please navigate to the login page and click on 'Forgot Password'."
}
```

**Blocked Response (200 OK - Safety Triggered)**:
```json
{
  "intent": "malicious_activity",
  "risk_level": "high",
  "response": "I cannot fulfill this request. Prompt injection attempt detected."
}
```

## 3. Security Rules
- **Rule 1**: Inputs exceeding 1000 characters are blocked.
- **Rule 2**: Inputs matching patterns in `BLOCKED_KEYWORDS` immediately return a blocked response without calling the LLM.
- **Rule 3**: Regex patterns detect common prompt injection phrases (e.g., "ignore all previous instructions").
- **Rule 4**: The system prompts instruct the LLM to only return the final JSON, never the reasoning.

## 4. Configuration
The system is configured via environment variables (or `.env` file):
- `PROVIDER`: "gemini" or "openai"
- `GEMINI_API_KEY` / `OPENAI_API_KEY`: Authentication keys.
- `GEMINI_MODEL`: Default is "gemini-1.5-flash".
