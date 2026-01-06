"""Custom Exception Class Definitions"""


class LLMClientError(Exception):
    """LLM client base exception class"""
    pass


class ConfigurationError(LLMClientError):
    """Configuration error exception"""
    pass


class APIError(LLMClientError):
    """API call error exception"""
    pass


class NetworkError(LLMClientError):
    """Network error exception"""
    pass


class ValidationError(LLMClientError):
    """Validation error exception"""
    pass

