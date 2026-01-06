"""Utility Functions Module"""
from typing import AsyncIterator
from .exceptions import ValidationError


async def handle_streaming_response(stream) -> AsyncIterator[str]:
    """
    Unified handling of streaming responses
    Note: This is a generic interface, specific implementation is handled by each client class
    
    :param stream: Streaming response object
    :return: Async iterator, yields a string chunk each time
    """
    # This function is mainly for type hints and possible unified processing in the future
    # Actual processing logic is implemented in respective client classes
    async for chunk in stream:
        yield chunk


def validate_prompt(prompt: str) -> None:
    """
    Validate prompt
    
    :param prompt: Prompt string
    :raises ValidationError: If prompt is empty or invalid
    """
    if not prompt or not isinstance(prompt, str):
        raise ValidationError("Prompt must be a non-empty string")
    
    if not prompt.strip():
        raise ValidationError("Prompt cannot be only whitespace")

