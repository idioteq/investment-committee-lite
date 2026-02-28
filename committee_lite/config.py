"""Configuration for Investment Committee Lite."""

import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration class."""

    # LLM Provider
    LLM_PROVIDER: Literal["openai", "anthropic"] = os.getenv("LLM_PROVIDER", "openai")

    # API Keys (optional - empty means mock mode)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Model Selection
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    # Committee Configuration
    DISAGREEMENT_THRESHOLD: int = int(os.getenv("DISAGREEMENT_THRESHOLD", "15"))
    MAX_RECONCILE_ROUNDS: int = int(os.getenv("MAX_RECONCILE_ROUNDS", "1"))

    # Mock Mode
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

    @classmethod
    def get_active_api_key(cls) -> str:
        """Get the API key for active provider."""
        if cls.LLM_PROVIDER == "anthropic":
            return cls.ANTHROPIC_API_KEY
        return cls.OPENAI_API_KEY

    @classmethod
    def get_active_model(cls) -> str:
        """Get the model name for active provider."""
        if cls.LLM_PROVIDER == "anthropic":
            return cls.ANTHROPIC_MODEL
        return cls.OPENAI_MODEL

    @classmethod
    def is_mock_mode(cls) -> bool:
        """Check if running in mock mode (no API keys needed)."""
        # Auto-enable mock mode if no API key is set
        if not cls.get_active_api_key():
            return True
        return cls.MOCK_MODE

    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if not cls.is_mock_mode():
            # Real mode: require API key
            if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
                raise ValueError(
                    "ANTHROPIC_API_KEY required when LLM_PROVIDER=anthropic. "
                    "Set in .env or use --mock flag."
                )
            elif cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY required when LLM_PROVIDER=openai. "
                    "Set in .env or use --mock flag."
                )
