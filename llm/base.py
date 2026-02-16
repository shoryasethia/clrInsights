from abc import ABC, abstractmethod
from typing import Any, Optional
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    GROQ = "groq"


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str,
        fallback_model: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 3,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        self.current_model = model_name
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate completion from prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Generate completion with streaming."""
        pass
    
    def switch_to_fallback(self) -> bool:
        """Switch to fallback model if available."""
        if self.fallback_model and self.current_model != self.fallback_model:
            self.current_model = self.fallback_model
            return True
        return False
    
    def reset_model(self) -> None:
        """Reset to primary model."""
        self.current_model = self.model_name
