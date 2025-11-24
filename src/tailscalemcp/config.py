"""
Configuration management for Tailscale MCP.

Handles environment variables, settings, and secure credential storage.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Also try loading from current directory
    load_dotenv()


class TailscaleConfig(BaseSettings):
    """Tailscale MCP configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required settings
    tailscale_api_key: str = Field(..., description="Tailscale API key")
    tailscale_tailnet: str = Field(..., description="Tailnet name")

    # Optional settings
    log_level: str = Field(default="INFO", description="Logging level")
    api_timeout: float = Field(
        default=30.0, description="API request timeout in seconds"
    )
    api_base_url: str = Field(
        default="https://api.tailscale.com", description="Tailscale API base URL"
    )

    # Rate limiting
    rate_limit_per_second: float = Field(
        default=1.0, description="API requests per second limit"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(
        default=2.0, description="Exponential backoff factor"
    )

    # Connection pooling
    max_connections: int = Field(default=10, description="Max HTTP connections")
    max_keepalive_connections: int = Field(
        default=5, description="Max keepalive connections"
    )

    # Monitoring
    prometheus_port: int = Field(default=9091, description="Prometheus metrics port")

    # Funnel configuration (for Phase 6)
    funnel_enabled: bool = Field(default=False, description="Enable Tailscale Funnel")
    funnel_port: int = Field(default=8000, description="Funnel port")
    funnel_name: str | None = Field(default=None, description="Funnel name")
    funnel_auth_token: str | None = Field(default=None, description="Funnel auth token")

    @classmethod
    def from_env(cls) -> "TailscaleConfig":
        """Load configuration from environment variables.

        Returns:
            TailscaleConfig instance

        Raises:
            ValueError: If required settings are missing
        """
        api_key = os.getenv("TAILSCALE_API_KEY")
        tailnet = os.getenv("TAILSCALE_TAILNET")

        if not api_key:
            raise ValueError(
                "TAILSCALE_API_KEY environment variable is required. "
                "Set it in .env file or environment."
            )

        if not tailnet:
            raise ValueError(
                "TAILSCALE_TAILNET environment variable is required. "
                "Set it in .env file or environment."
            )

        return cls(
            tailscale_api_key=api_key,
            tailscale_tailnet=tailnet,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_timeout=float(os.getenv("API_TIMEOUT", "30.0")),
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", "9091")),
        )


def get_config() -> TailscaleConfig:
    """Get the application configuration.

    Returns:
        TailscaleConfig instance
    """
    return TailscaleConfig.from_env()
