"""Anthropic (Claude) LLM adapter."""

from typing import Optional
from anthropic import Anthropic
from committee_lite.llm.client import LLMClient


class AnthropicAdapter(LLMClient):
    """Anthropic (Claude) API adapter."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            model: Model name
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """Generate completion using Anthropic API."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text
