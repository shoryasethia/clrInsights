import asyncio
from typing import Optional, AsyncIterator
from groq import Groq, AsyncGroq
from clrinsights.llm.base import BaseLLMClient


class GroqClient(BaseLLMClient):
    """Groq LLM client."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = AsyncGroq(api_key=self.api_key)
        self.sync_client = Groq(api_key=self.api_key)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate completion from Groq.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            **kwargs: Additional model parameters
            
        Returns:
            Generated text
        """
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                messages = []
                if system_prompt:
                    messages.append({
                        "role": "system",
                        "content": system_prompt
                    })
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                
                response = await self.client.chat.completions.create(
                    model=self.current_model,
                    messages=messages,
                    temperature=kwargs.get('temperature', self.temperature),
                    max_tokens=kwargs.get('max_tokens', 8192),
                )
                
                return response.choices[0].message.content
            
            except Exception as e:
                last_error = e
                retries += 1
                
                # Try fallback model on first failure
                if retries == 1 and self.switch_to_fallback():
                    continue
                
                # Retry with exponential backoff
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                    continue
        
        raise Exception(
            f"Groq generation failed after {self.max_retries} retries: {last_error}"
        )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate completion with streaming.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            **kwargs: Additional model parameters
            
        Yields:
            Text chunks
        """
        try:
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            stream = await self.client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', 8192),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            raise Exception(f"Groq streaming failed: {e}")
