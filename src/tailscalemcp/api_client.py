"""
Tailscale API Client

Real implementation using httpx for authenticating with and calling the Tailscale Admin API.
"""

import os
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class TailscaleAPIClient:
    """Client for Tailscale Admin API."""

    BASE_URL = "https://api.tailscale.com"

    def __init__(self, api_key: str | None = None, tailnet: str | None = None):
        """Initialize Tailscale API client.

        Args:
            api_key: Tailscale API key (from TAILSCALE_API_KEY env var if not provided)
            tailnet: Tailnet name (from TAILSCALE_TAILNET env var if not provided)
        """
        self.api_key = api_key or os.getenv("TAILSCALE_API_KEY")
        self.tailnet = tailnet or os.getenv("TAILSCALE_TAILNET")

        if not self.api_key:
            raise ValueError(
                "Tailscale API key is required. Set TAILSCALE_API_KEY environment variable or pass api_key parameter."
            )

        if not self.tailnet:
            raise ValueError(
                "Tailnet name is required. Set TAILSCALE_TAILNET environment variable or pass tailnet parameter."
            )

        self.base_url = f"{self.BASE_URL}/api/v2/tailnet/{self.tailnet}"

        logger.info("Tailscale API client initialized", tailnet=self.tailnet)

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make an authenticated request to the Tailscale API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (relative to tailnet URL)
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response from the API

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.debug(
                    "Making API request",
                    method=method,
                    url=url,
                    endpoint=endpoint,
                )

                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()

                # Handle empty responses
                if response.status_code == 204:
                    return {}

                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "API request failed",
                    method=method,
                    url=url,
                    status_code=e.response.status_code,
                    response=e.response.text,
                )
                raise
            except Exception as e:
                logger.error("Unexpected error during API request", error=str(e))
                raise

    async def list_devices(self) -> list[dict[str, Any]]:
        """List all devices in the tailnet.

        Returns:
            List of device information
        """
        try:
            response = await self._request("GET", "/devices")
            devices = response.get("devices", [])

            logger.info("Devices retrieved from API", count=len(devices))

            return devices

        except Exception as e:
            logger.error("Failed to list devices from API", error=str(e))
            raise

    async def get_device(self, device_id: str) -> dict[str, Any]:
        """Get details for a specific device.

        Args:
            device_id: Device ID or stable ID

        Returns:
            Device information
        """
        try:
            response = await self._request("GET", f"/devices/{device_id}")

            logger.info("Device retrieved from API", device_id=device_id)

            return response

        except Exception as e:
            logger.error(
                "Failed to get device from API", device_id=device_id, error=str(e)
            )
            raise
