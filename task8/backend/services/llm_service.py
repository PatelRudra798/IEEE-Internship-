import logging
import os
from abc import ABC, abstractmethod
import httpx
from openai import OpenAI
import google.generativeai as genai
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_answer(self, context: str, question: str) -> str:
        """
        Generates an answer to the question strictly based on the provided context.
        
        Args:
            context: Combined text passages retrieved from the vector database.
            question: The user's query.
            
        Returns:
            The generated response string.
        """
        pass


class OllamaProvider(BaseLLMProvider):
    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model
        logger.info(f"Initialized OllamaProvider at {self.host} using model {self.model}")

    def generate_answer(self, context: str, question: str) -> str:
        url = f"{self.host}/api/generate"
        
        prompt = (
            "You are a document assistant.\n"
            "Answer ONLY from the provided context.\n"
            "If the answer is not found in the context, say:\n"
            "\"I could not find this information in the uploaded documents.\"\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0  # Encourage deterministic responses strictly based on context
            }
        }

        try:
            logger.info(f"Calling Ollama API ({self.model}) at {url}")
            # Ollama generation can take time, especially on CPU or slow host machines; timeout set to 90 seconds
            with httpx.Client(timeout=90.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                answer = result.get("response", "").strip()
                return answer
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Ollama generation failed: {e}")


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAIProvider using model {self.model}")

    def generate_answer(self, context: str, question: str) -> str:
        prompt = (
            "You are a document assistant.\n"
            "Answer ONLY from the provided context.\n"
            "If the answer is not found in the context, say:\n"
            "\"I could not find this information in the uploaded documents.\"\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )

        try:
            logger.info(f"Calling OpenAI Chat Completion API ({self.model})")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}", exc_info=True)
            raise RuntimeError(f"OpenAI generation failed: {e}")


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = None):
        genai.configure(api_key=api_key, transport="rest")
        # Use model from env if provided, otherwise default to gemini-3.5-flash
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        logger.info(f"Initialized GeminiProvider using model {self.model_name} with REST transport")

    def generate_answer(self, context: str, question: str) -> str:
        prompt = (
            "You are a document assistant.\n"
            "Answer ONLY from the provided context.\n"
            "If the answer is not found in the context, say:\n"
            "\"I could not find this information in the uploaded documents.\"\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )

        try:
            logger.info(f"Calling Gemini API ({self.model_name})")
            model = genai.GenerativeModel(self.model_name)
            generation_config = genai.types.GenerationConfig(
                temperature=0.0
            )
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Gemini generation failed: {e}")


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function to retrieve the configured LLM provider from settings.
    """
    provider_name = settings.llm_provider.lower().strip()
    
    if provider_name == "ollama":
        return OllamaProvider(host=settings.ollama_host, model=settings.ollama_model)
        
    elif provider_name == "openai":
        if not settings.openai_api_key:
            logger.error("LLM_PROVIDER is set to OpenAI, but OPENAI_API_KEY is missing.")
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        return OpenAIProvider(api_key=settings.openai_api_key)
        
    elif provider_name == "gemini":
        if not settings.gemini_api_key:
            logger.error("LLM_PROVIDER is set to Gemini, but GEMINI_API_KEY is missing.")
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        return GeminiProvider(api_key=settings.gemini_api_key)
        
    else:
        logger.error(f"Unsupported LLM_PROVIDER name: {provider_name}")
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}. "
            "Supported values are 'ollama', 'openai', or 'gemini'."
        )
