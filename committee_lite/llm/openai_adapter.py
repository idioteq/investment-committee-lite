"""OpenAI LLM adapter."""

from typing import Optional
from openai import OpenAI
from committee_lite.llm.client import LLMClient


class OpenAIAdapter(LLMClient):
    """OpenAI API adapter."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """Generate completion using OpenAI API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content
