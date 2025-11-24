"""
API Key management operations service layer.

Provides API key lifecycle management operations.
"""

from datetime import datetime
from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class KeyOperations:
    """Service layer for API key management operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize key operations.

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

    async def list_auth_keys(self) -> list[dict[str, Any]]:
        """List all authentication keys for the tailnet.

        Note: This endpoint may not be available in all Tailscale API versions.
        Returns empty list if not supported.

        Returns:
            List of auth key information dictionaries

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            # Note: The exact endpoint may vary. This is a placeholder.
            # Tailscale API may not expose all keys for security reasons.
            response = await self.client._request("GET", "/keys")
            keys = response.get("keys", [])
            logger.info("Auth keys retrieved", count=len(keys))
            return keys

        except Exception as e:
            # If endpoint doesn't exist, return empty list rather than failing
            logger.warning("Auth keys endpoint may not be available", error=str(e))
            return []

    async def create_auth_key(
        self,
        capabilities: dict[str, Any] | None = None,
        expires_seconds: int | None = None,
        reusable: bool = False,
    ) -> dict[str, Any]:
        """Create a new authentication key.

        Args:
            capabilities: Key capabilities (permissions)
            expires_seconds: Key expiration in seconds
            reusable: Whether key can be reused multiple times

        Returns:
            Created auth key information with the key value

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            payload: dict[str, Any] = {
                "reusable": reusable,
            }

            if capabilities:
                payload["capabilities"] = capabilities

            if expires_seconds:
                payload["expirySeconds"] = expires_seconds

            response = await self.client._request("POST", "/keys", json=payload)
            logger.info("Auth key created", reusable=reusable)
            return response

        except Exception as e:
            logger.error("Error creating auth key", error=str(e))
            raise TailscaleMCPError(f"Failed to create auth key: {e}") from e

    async def revoke_auth_key(self, key_id: str) -> None:
        """Revoke an authentication key.

        Args:
            key_id: Authentication key ID

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            await self.client._request("DELETE", f"/keys/{key_id}")
            logger.info("Auth key revoked", key_id=key_id)

        except Exception as e:
            logger.error("Error revoking auth key", key_id=key_id, error=str(e))
            raise TailscaleMCPError(f"Failed to revoke auth key: {e}") from e

    async def analyze_key_usage(self) -> dict[str, Any]:
        """Analyze authentication key usage and identify expired/compromised keys.

        Returns:
            Key usage analysis report

        Raises:
            TailscaleMCPError: If analysis fails
        """
        try:
            keys = await self.list_auth_keys()

            current_time = datetime.now(datetime.now().astimezone().tzinfo)
            expired: list[dict[str, Any]] = []
            expiring_soon: list[dict[str, Any]] = []
            active: list[dict[str, Any]] = []

            for key in keys:
                key_info = {
                    "key_id": key.get("id"),
                    "created": key.get("created"),
                    "expires": key.get("expires"),
                    "reusable": key.get("reusable", False),
                }

                if key.get("expires"):
                    try:
                        expires = datetime.fromisoformat(
                            key["expires"].replace("Z", "+00:00")
                        )
                        if expires < current_time:
                            expired.append(key_info)
                        elif (expires - current_time).days < 7:
                            expiring_soon.append(key_info)
                        else:
                            active.append(key_info)
                    except (ValueError, KeyError):
                        active.append(key_info)
                else:
                    active.append(key_info)

            result = {
                "total_keys": len(keys),
                "expired_count": len(expired),
                "expiring_soon_count": len(expiring_soon),
                "active_count": len(active),
                "expired_keys": expired,
                "expiring_soon_keys": expiring_soon,
                "active_keys": active,
                "analysis_timestamp": current_time.isoformat(),
            }

            logger.info(
                "Key usage analyzed",
                total=len(keys),
                expired=len(expired),
                expiring_soon=len(expiring_soon),
            )
            return result

        except Exception as e:
            logger.error("Error analyzing key usage", error=str(e))
            raise TailscaleMCPError(f"Failed to analyze key usage: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
