"""
Network operations service layer.

Provides network, DNS, and ACL policy operations using the Tailscale API client.
"""

from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class NetworkOperations:
    """Service layer for network, DNS, and ACL operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize network operations.

        Args:
            config: Configuration object (if provided, api_key and tailnet are ignored)
            api_key: Tailscale API key (optional if config provided)
            tailnet: Tailnet name (optional if config provided)
        """
        if config:
            self.config = config
        else:
            self.config = TailscaleConfig(
                tailscale_api_key=api_key or "",
                tailscale_tailnet=tailnet or "",
            )
        self.client = TailscaleAPIClient(self.config)

    async def get_dns_config(self) -> dict[str, Any]:
        """Get DNS configuration for the tailnet.

        Returns:
            DNS configuration dictionary

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            config = await self.client.get_dns_config()
            logger.info("DNS configuration retrieved")
            return config

        except Exception as e:
            logger.error("Error getting DNS config", error=str(e))
            raise TailscaleMCPError(f"Failed to get DNS config: {e}") from e

    async def update_dns_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Update DNS configuration for the tailnet.

        Args:
            config: DNS configuration dictionary

        Returns:
            Updated DNS configuration

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            updated_config = await self.client.update_dns_config(config)
            logger.info("DNS configuration updated")
            return updated_config

        except Exception as e:
            logger.error("Error updating DNS config", error=str(e))
            raise TailscaleMCPError(f"Failed to update DNS config: {e}") from e

    async def get_acl_policy(self) -> dict[str, Any]:
        """Get the current ACL policy for the tailnet.

        Returns:
            ACL policy dictionary

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            policy = await self.client.get_acl_policy()
            logger.info("ACL policy retrieved")
            return policy

        except Exception as e:
            logger.error("Error getting ACL policy", error=str(e))
            raise TailscaleMCPError(f"Failed to get ACL policy: {e}") from e

    async def update_acl_policy(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Update the ACL policy for the tailnet.

        Args:
            policy: ACL policy dictionary

        Returns:
            Updated ACL policy confirmation

        Raises:
            TailscaleMCPError: If API call fails or policy validation fails
        """
        try:
            updated_policy = await self.client.update_acl_policy(policy)
            logger.info("ACL policy updated")
            return updated_policy

        except Exception as e:
            logger.error("Error updating ACL policy", error=str(e))
            raise TailscaleMCPError(f"Failed to update ACL policy: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
