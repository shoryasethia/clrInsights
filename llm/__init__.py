"""LLM client implementations."""

from clrinsights.llm.base import BaseLLMClient, LLMProvider
from clrinsights.llm.gemini import GeminiClient
from clrinsights.llm.groq import GroqClient
from clrinsights.config import settings


# Initialize clients
gemini_client = GeminiClient(
    api_key=settings.gemini_api_key,
    model_name=settings.gemini_model,
    fallback_model=settings.gemini_fallback_model,
    temperature=settings.default_temperature,
    max_retries=settings.max_retries,
    timeout=settings.request_timeout
)

groq_client = GroqClient(
    api_key=settings.groq_api_key,
    model_name=settings.groq_model,
    fallback_model=settings.groq_fallback_model,
    temperature=settings.default_temperature,
    max_retries=settings.max_retries,
    timeout=settings.request_timeout
)


def get_client(provider: LLMProvider = LLMProvider.GEMINI) -> BaseLLMClient:
    """
    Get LLM client by provider.
    
    Args:
        provider: LLM provider enum
        
    Returns:
        LLM client instance
    """
    if provider == LLMProvider.GEMINI:
        return gemini_client
    elif provider == LLMProvider.GROQ:
        return groq_client
    else:
        raise ValueError(f"Unknown provider: {provider}")


def update_api_key(provider: str, new_key: str):
    """Update the API key for a provider at runtime and reinitialize its client."""
    global gemini_client, groq_client

    if provider == 'gemini':
        gemini_client.api_key = new_key
        from google import genai
        gemini_client.client = genai.Client(api_key=new_key)
    elif provider == 'groq':
        from groq import Groq as _Groq, AsyncGroq as _AsyncGroq
        groq_client.api_key = new_key
        groq_client.client = _AsyncGroq(api_key=new_key)
        groq_client.sync_client = _Groq(api_key=new_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")


__all__ = [
    'BaseLLMClient',
    'GeminiClient',
    'GroqClient',
    'LLMProvider',
    'gemini_client',
    'groq_client',
    'get_client',
    'update_api_key'
]
