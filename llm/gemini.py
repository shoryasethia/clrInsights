import asyncio
from typing import Optional, AsyncIterator
from google import genai
from google.genai import types
from clrinsights.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM client using google-genai library."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = genai.Client(api_key=self.api_key)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate completion from Gemini.
        
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
                config = types.GenerateContentConfig(
                    temperature=kwargs.get('temperature', self.temperature),
                    max_output_tokens=kwargs.get('max_tokens', 8192),
                    system_instruction=system_prompt if system_prompt else None
                )
                
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.current_model,
                    contents=prompt,
                    config=config
                )
                
                return response.text
            
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
            f"Gemini generation failed after {self.max_retries} retries: {last_error}"
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
            config = types.GenerateContentConfig(
                temperature=kwargs.get('temperature', self.temperature),
                max_output_tokens=kwargs.get('max_tokens', 8192),
                system_instruction=system_prompt if system_prompt else None
            )
            
            async for chunk in self.client.aio.models.generate_content_stream(
                model=self.current_model,
                contents=prompt,
                config=config
            ):
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            raise Exception(f"Gemini streaming failed: {e}")
