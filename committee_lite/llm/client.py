"""Unified LLM client interface."""

from abc import ABC, abstractmethod
from typing import Optional
from committee_lite.config import Config


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a completion from the LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        pass


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    mock: bool = False,
) -> LLMClient:
    """
    Factory function to get the appropriate LLM client.

    Args:
        provider: "openai", "anthropic", or None (uses Config.LLM_PROVIDER)
        model: Model name or None (uses Config default)
        mock: Force mock mode

    Returns:
        LLMClient instance
    """
    from committee_lite.llm.mock_adapter import MockAdapter
    from committee_lite.llm.openai_adapter import OpenAIAdapter
    from committee_lite.llm.anthropic_adapter import AnthropicAdapter

    # Check if mock mode
    if mock or Config.is_mock_mode():
        return MockAdapter()

    # Determine provider
    provider = provider or Config.LLM_PROVIDER

    if provider == "openai":
        model = model or Config.OPENAI_MODEL
        return OpenAIAdapter(api_key=Config.OPENAI_API_KEY, model=model)
    elif provider == "anthropic":
        model = model or Config.ANTHROPIC_MODEL
        return AnthropicAdapter(api_key=Config.ANTHROPIC_API_KEY, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")
