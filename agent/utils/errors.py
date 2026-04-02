"""
Custom exceptions for the agent
"""


class AppException(Exception):
    """Base exception for application"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class MCPConnectionError(AppException):
    """Failed to connect to MCP server"""
    def __init__(self, message: str):
        super().__init__(message, "MCP_CONNECTION_ERROR")


class MCPToolError(AppException):
    """MCP tool invocation failed"""
    def __init__(self, tool_name: str, message: str):
        super().__init__(f"Tool '{tool_name}' failed: {message}", "MCP_TOOL_ERROR")


class LLMError(AppException):
    """LLM inference error"""
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR")


class PPTGenerationError(AppException):
    """PPT generation error"""
    def __init__(self, message: str):
        super().__init__(message, "PPT_GENERATION_ERROR")


class AuthenticationError(AppException):
    """Authentication error"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_ERROR")


class ValidationError(AppException):
    """Input validation error"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class RateLimitError(AppException):
    """Rate limit exceeded"""
    def __init__(self, message: str, retry_after: int):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR")
