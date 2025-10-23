"""
Tailscale MCP Exceptions

This module defines exceptions specific to the Tailscale MCP server.
"""

from typing import Any


class TailscaleMCPError(Exception):
    """Base exception for all Tailscale MCP errors."""

    def __init__(
        self,
        message: str = "An error occurred in the Tailscale MCP server",
        code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            code: Error code (HTTP status code)
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert the exception to a dictionary.

        Returns:
            Dictionary containing error details
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class AuthenticationError(TailscaleMCPError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, code=401)


class AuthorizationError(TailscaleMCPError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message=message, code=403)


class NotFoundError(TailscaleMCPError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, resource_id: str) -> None:
        message = f"{resource} '{resource_id}' not found"
        super().__init__(message=message, code=404)


class ValidationError(TailscaleMCPError):
    """Raised when input validation fails."""

    def __init__(
        self, message: str = "Validation failed", errors: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message=message, code=400, details={"errors": errors or {}})


class RateLimitExceededError(TailscaleMCPError):
    """Raised when the rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message=message, code=429)


class ServerError(TailscaleMCPError):
    """Raised when an internal server error occurs."""

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message=message, code=500)


class TailscaleAPIError(TailscaleMCPError):
    """Raised when an error occurs while communicating with the Tailscale API."""

    def __init__(self, message: str = "Error communicating with Tailscale API") -> None:
        super().__init__(message=message, code=502)


class ConfigurationError(TailscaleMCPError):
    """Raised when there is a configuration error."""

    def __init__(self, message: str = "Configuration error") -> None:
        super().__init__(message=message, code=500)
