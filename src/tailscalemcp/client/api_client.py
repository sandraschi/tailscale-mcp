"""
Enhanced Tailscale API Client.

Provides comprehensive API integration with rate limiting, retry logic,
and proper error handling.
"""

import os
from typing import Any

import httpx
import structlog

from tailscalemcp.client.rate_limiter import RateLimiter
from tailscalemcp.client.retry import RetryHandler
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitExceededError,
    TailscaleAPIError,
)
from tailscalemcp.models.service import Service

logger = structlog.get_logger(__name__)


class TailscaleAPIClient:
    """Enhanced client for Tailscale Admin API with rate limiting and retry."""

    BASE_URL = "https://api.tailscale.com"

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ) -> None:
        """Initialize Tailscale API client.

        Args:
            config: Configuration object (if provided, api_key and tailnet are ignored)
            api_key: Tailscale API key (optional if config provided)
            tailnet: Tailnet name (optional if config provided)
        """
        if config:
            self.config = config
            self.api_key = config.tailscale_api_key
            self.tailnet = config.tailscale_tailnet
            self.timeout = config.api_timeout
            self.base_url = config.api_base_url
        else:
            self.config = None
            self.api_key = api_key or os.getenv("TAILSCALE_API_KEY")
            self.tailnet = tailnet or os.getenv("TAILSCALE_TAILNET")
            self.timeout = 30.0
            self.base_url = self.BASE_URL

        if not self.api_key:
            raise ValueError(
                "Tailscale API key is required. Set TAILSCALE_API_KEY environment "
                "variable, pass api_key parameter, or provide config."
            )

        if not self.tailnet:
            raise ValueError(
                "Tailnet name is required. Set TAILSCALE_TAILNET environment "
                "variable, pass tailnet parameter, or provide config."
            )

        self.api_base_url = f"{self.base_url}/api/v2/tailnet/{self.tailnet}"

        # Initialize rate limiter and retry handler
        if self.config:
            self.rate_limiter = RateLimiter(
                rate=self.config.rate_limit_per_second,
                window=self.config.rate_limit_window,
            )
            self.retry_handler = RetryHandler(
                max_retries=self.config.max_retries,
                backoff_factor=self.config.retry_backoff_factor,
            )
        else:
            self.rate_limiter = RateLimiter()
            self.retry_handler = RetryHandler()

        # HTTP client with connection pooling
        max_connections = self.config.max_connections if self.config else 10
        max_keepalive = self.config.max_keepalive_connections if self.config else 5

        limits = httpx.Limits(
            max_keepalive_connections=max_keepalive,
            max_connections=max_connections,
        )

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=limits,
            headers={
                "User-Agent": "tailscale-mcp/2.0.0",
            },
        )

        logger.info(
            "Tailscale API client initialized",
            tailnet=self.tailnet,
            base_url=self.api_base_url,
        )

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Tailscale API with rate limiting and retry.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to tailnet URL)
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response from the API

        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If resource not found
            RateLimitExceededError: If rate limit exceeded
            TailscaleAPIError: If API request fails
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(kwargs.pop("headers", {}))

        async def _make_request() -> dict[str, Any]:
            """Inner function for retry logic."""
            await self.rate_limiter.acquire()

            try:
                logger.debug(
                    "Making API request",
                    method=method,
                    url=url,
                    endpoint=endpoint,
                )

                response = await self.client.request(
                    method, url, headers=headers, **kwargs
                )

                # Handle specific status codes
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API key or authentication failed"
                    )
                elif response.status_code == 404:
                    raise NotFoundError("Resource", endpoint)
                elif response.status_code == 429:
                    raise RateLimitExceededError("Rate limit exceeded")

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
                    response=e.response.text[:200],
                )
                raise TailscaleAPIError(
                    f"API request failed: {e.response.status_code} - {e.response.text[:200]}"
                ) from e
            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.error("Network error during API request", error=str(e))
                raise TailscaleAPIError(f"Network error: {e!s}") from e

        try:
            return await self.retry_handler.execute(_make_request)
        except (AuthenticationError, NotFoundError, RateLimitExceededError):
            # Don't retry auth/not found/rate limit errors
            raise
        except Exception as e:
            logger.error("Unexpected error during API request", error=str(e))
            raise TailscaleAPIError(f"Unexpected error: {e!s}") from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "TailscaleAPIClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    # Device operations
    async def list_devices(self) -> list[dict[str, Any]]:
        """List all devices in the tailnet.

        Returns:
            List of device information dictionaries
        """
        response = await self._request("GET", "/devices")
        devices = response.get("devices", [])
        logger.info("Devices retrieved from API", count=len(devices))
        return devices

    async def get_device(self, device_id: str) -> dict[str, Any]:
        """Get details for a specific device.

        Args:
            device_id: Device ID or stable ID

        Returns:
            Device information dictionary
        """
        response = await self._request("GET", f"/devices/{device_id}")
        logger.info("Device retrieved from API", device_id=device_id)
        return response

    async def update_device(
        self, device_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a device (e.g., rename, tags, authorized status).

        Args:
            device_id: Device ID or stable ID
            updates: Dictionary of updates to apply

        Returns:
            Updated device information
        """
        response = await self._request("POST", f"/devices/{device_id}", json=updates)
        logger.info("Device updated", device_id=device_id, updates=list(updates.keys()))
        return response

    async def delete_device(self, device_id: str) -> None:
        """Delete a device from the tailnet.

        Args:
            device_id: Device ID or stable ID
        """
        await self._request("DELETE", f"/devices/{device_id}")
        logger.info("Device deleted", device_id=device_id)

    # ACL Policy operations
    async def get_acl_policy(self) -> dict[str, Any]:
        """Get the current ACL policy.

        Returns:
            ACL policy dictionary
        """
        response = await self._request("GET", "/acl")
        logger.info("ACL policy retrieved")
        return response

    async def update_acl_policy(self, policy: dict[str, Any]) -> dict[str, Any]:
        """Update the ACL policy.

        Args:
            policy: New ACL policy dictionary

        Returns:
            Updated policy confirmation
        """
        response = await self._request("POST", "/acl", json=policy)
        logger.info("ACL policy updated")
        return response

    # DNS operations
    async def get_dns_config(self) -> dict[str, Any]:
        """Get DNS configuration.

        Returns:
            DNS configuration dictionary
        """
        response = await self._request("GET", "/dns/nameservers")
        logger.info("DNS configuration retrieved")
        return response

    async def update_dns_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Update DNS configuration.

        Args:
            config: DNS configuration dictionary

        Returns:
            Updated configuration confirmation
        """
        response = await self._request("POST", "/dns/nameservers", json=config)
        logger.info("DNS configuration updated")
        return response

    # Services (TailVIPs) operations - beta, subject to change
    async def list_services(self) -> list[Service]:
        """List Tailscale Services (TailVIPs) for the tailnet.

        Returns:
            List of Service models
        """
        data = await self._request("GET", "/services")
        raw_services = data.get("services", []) if isinstance(data, dict) else data
        services: list[Service] = [
            Service.from_api_response(s) for s in (raw_services or [])
        ]
        logger.info("Services retrieved from API", count=len(services))
        return services

    async def get_service(self, service_id: str) -> Service:
        """Get a single Service by ID."""
        data = await self._request("GET", f"/services/{service_id}")
        service = Service.from_api_response(data)
        logger.info("Service retrieved", service_id=service_id)
        return service

    async def create_service(self, payload: dict[str, Any]) -> Service:
        """Create a new Service.

        Args:
            payload: API-specific service creation payload
        """
        data = await self._request("POST", "/services", json=payload)
        service = Service.from_api_response(data)
        logger.info("Service created", service_id=service.id)
        return service

    async def update_service(self, service_id: str, payload: dict[str, Any]) -> Service:
        """Update an existing Service."""
        data = await self._request("POST", f"/services/{service_id}", json=payload)
        service = Service.from_api_response(data)
        logger.info("Service updated", service_id=service_id)
        return service

    async def delete_service(self, service_id: str) -> None:
        """Delete a Service by ID."""
        await self._request("DELETE", f"/services/{service_id}")
        logger.info("Service deleted", service_id=service_id)
