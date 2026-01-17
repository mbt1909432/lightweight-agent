"""Client Module"""
from .base import BaseClient
from .openai_client import OpenAIClient

# Optional dependency: anthropic
try:
    from .anthropic_client import AnthropicClient  # type: ignore
except Exception:  # pragma: no cover
    AnthropicClient = None  # type: ignore

__all__ = ["BaseClient", "OpenAIClient", "AnthropicClient"]

