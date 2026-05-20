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
                "User-Agent": "tailscale-mcp/2.0.2",
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

    # Users (Admin API v2 — see tailscale.com/api, tag users)
    async def list_users(
        self,
        user_type: str | None = None,
        role: str | None = None,
    ) -> list[dict[str, Any]]:
        """List tailnet users. Optional filters: type=member|shared, role=..."""
        params: dict[str, str] = {}
        if user_type:
            params["type"] = user_type
        if role:
            params["role"] = role
        response = await self._request(
            "GET", "/users", params=params if params else None
        )
        users = response.get("users", [])
        logger.info("Users retrieved from API", count=len(users))
        return users if isinstance(users, list) else []

    async def get_user(self, user_id: str) -> dict[str, Any]:
        """Get a single user by ID (UUID from list_users)."""
        data = await self._request("GET", f"/users/{user_id}")
        logger.info("User retrieved from API", user_id=user_id)
        return data

    # --- Device invites ---
    async def list_device_invites(self, device_id: str) -> list[dict[str, Any]]:
        """List all share invites for a device."""
        data = await self._request("GET", f"/devices/{device_id}/device-invites")
        invites = data if isinstance(data, list) else []
        logger.info("Device invites retrieved", device_id=device_id, count=len(invites))
        return invites

    async def create_device_invites(
        self, device_id: str, invites: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create share invites for a device."""
        data = await self._request("POST", f"/devices/{device_id}/device-invites", json=invites)
        result = data if isinstance(data, list) else []
        logger.info("Device invites created", device_id=device_id, count=len(result))
        return result

    async def get_device_invite(self, invite_id: str) -> dict[str, Any]:
        """Get a specific device invite."""
        return await self._request("GET", f"/device-invites/{invite_id}")

    async def delete_device_invite(self, invite_id: str) -> None:
        """Delete a device invite."""
        await self._request("DELETE", f"/device-invites/{invite_id}")
        logger.info("Device invite deleted", invite_id=invite_id)

    async def resend_device_invite(self, invite_id: str) -> None:
        """Resend a device invite email."""
        await self._request("POST", f"/device-invites/{invite_id}/resend")
        logger.info("Device invite resent", invite_id=invite_id)

    async def accept_device_invite(self, invite: str) -> dict[str, Any]:
        """Accept a device share invite by URL or code."""
        return await self._request("POST", "/device-invites/-/accept", json={"invite": invite})

    # --- User invites ---
    async def list_user_invites(self, tailnet: str | None = None) -> list[dict[str, Any]]:
        """List all open user invites to the tailnet."""
        t = tailnet or self.tailnet
        data = await self._request("GET", f"/tailnet/{t}/user-invites")
        invites = data if isinstance(data, list) else []
        logger.info("User invites retrieved", count=len(invites))
        return invites

    async def create_user_invites(
        self, invites: list[dict[str, Any]], tailnet: str | None = None
    ) -> list[dict[str, Any]]:
        """Create user invites to the tailnet."""
        t = tailnet or self.tailnet
        data = await self._request("POST", f"/tailnet/{t}/user-invites", json=invites)
        result = data if isinstance(data, list) else []
        logger.info("User invites created", count=len(result))
        return result

    async def get_user_invite(self, invite_id: str) -> dict[str, Any]:
        """Get a specific user invite."""
        return await self._request("GET", f"/user-invites/{invite_id}")

    async def delete_user_invite(self, invite_id: str) -> None:
        """Delete a user invite."""
        await self._request("DELETE", f"/user-invites/{invite_id}")
        logger.info("User invite deleted", invite_id=invite_id)

    async def resend_user_invite(self, invite_id: str) -> None:
        """Resend a user invite email."""
        await self._request("POST", f"/user-invites/{invite_id}/resend")
        logger.info("User invite resent", invite_id=invite_id)

    # --- Device posture attributes ---
    async def get_device_posture_attributes(self, device_id: str) -> dict[str, Any]:
        """Get all posture attributes for a device."""
        return await self._request("GET", f"/devices/{device_id}/attributes")

    async def set_custom_device_posture_attribute(
        self, device_id: str, attribute_key: str, value: Any, expiry: str | None = None, comment: str | None = None
    ) -> dict[str, Any]:
        """Set a custom posture attribute on a device."""
        body: dict[str, Any] = {"value": value}
        if expiry:
            body["expiry"] = expiry
        if comment:
            body["comment"] = comment
        return await self._request("POST", f"/devices/{device_id}/attributes/{attribute_key}", json=body)

    async def delete_custom_device_posture_attribute(self, device_id: str, attribute_key: str) -> None:
        """Delete a custom posture attribute from a device."""
        await self._request("DELETE", f"/devices/{device_id}/attributes/{attribute_key}")
        logger.info("Device posture attribute deleted", device_id=device_id, key=attribute_key)

    async def batch_update_device_posture_attributes(
        self, nodes: dict[str, Any], comment: str | None = None, tailnet: str | None = None
    ) -> None:
        """Batch update custom posture attributes across devices."""
        t = tailnet or self.tailnet
        body: dict[str, Any] = {"nodes": nodes}
        if comment:
            body["comment"] = comment
        await self._request("PATCH", f"/tailnet/{t}/device-attributes", json=body)
        logger.info("Batch posture attributes updated")

    # --- Device key management ---
    async def expire_device_key(self, device_id: str) -> None:
        """Expire a device's node key (forces re-authentication)."""
        await self._request("POST", f"/devices/{device_id}/expire")
        logger.info("Device key expired", device_id=device_id)

    async def update_device_key(self, device_id: str, key_expiry_disabled: bool) -> None:
        """Update device key expiry settings."""
        await self._request(
            "POST", f"/devices/{device_id}/key",
            json={"keyExpiryDisabled": key_expiry_disabled},
        )
        logger.info("Device key updated", device_id=device_id, key_expiry_disabled=key_expiry_disabled)

    async def set_device_ip(self, device_id: str, ipv4: str) -> None:
        """Set a device's IPv4 address."""
        await self._request("POST", f"/devices/{device_id}/ip", json={"ipv4": ipv4})
        logger.info("Device IP set", device_id=device_id, ipv4=ipv4)

    # --- Logging ---
    async def list_configuration_audit_logs(
        self,
        tailnet: str | None = None,
        start: str | None = None,
        end: str | None = None,
        actor: str | None = None,
        target: str | None = None,
        event: str | None = None,
    ) -> list[dict[str, Any]]:
        """List configuration audit logs for a tailnet."""
        t = tailnet or self.tailnet
        params: dict[str, str] = {}
        if start: params["start"] = start
        if end: params["end"] = end
        if actor: params["actor"] = actor
        if target: params["target"] = target
        if event: params["event"] = event
        data = await self._request("GET", f"/tailnet/{t}/logging/configuration", params=params or None)
        logs = data.get("logs", []) if isinstance(data, dict) else []
        logger.info("Configuration audit logs retrieved", count=len(logs))
        return logs

    async def list_network_flow_logs(
        self,
        tailnet: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict[str, Any]]:
        """List network flow logs for a tailnet."""
        t = tailnet or self.tailnet
        params: dict[str, str] = {}
        if start: params["start"] = start
        if end: params["end"] = end
        data = await self._request("GET", f"/tailnet/{t}/logging/network", params=params or None)
        logs = data.get("logs", []) if isinstance(data, dict) else []
        logger.info("Network flow logs retrieved", count=len(logs))
        return logs

    async def get_log_streaming_status(self, log_type: str, tailnet: str | None = None) -> dict[str, Any]:
        """Get log streaming status for a log type."""
        t = tailnet or self.tailnet
        return await self._request("GET", f"/tailnet/{t}/logging/{log_type}/stream/status")

    async def get_log_streaming_configuration(self, log_type: str, tailnet: str | None = None) -> dict[str, Any]:
        """Get log streaming configuration for a log type."""
        t = tailnet or self.tailnet
        return await self._request("GET", f"/tailnet/{t}/logging/{log_type}/stream")

    async def set_log_streaming_configuration(
        self, log_type: str, config: dict[str, Any], tailnet: str | None = None
    ) -> dict[str, Any]:
        """Set log streaming configuration for a log type."""
        t = tailnet or self.tailnet
        return await self._request("PUT", f"/tailnet/{t}/logging/{log_type}/stream", json=config)

    # --- Webhooks ---
    async def list_webhooks(self, tailnet: str | None = None) -> list[dict[str, Any]]:
        """List all webhook endpoints for a tailnet."""
        t = tailnet or self.tailnet
        data = await self._request("GET", f"/tailnet/{t}/webhooks")
        hooks = data.get("webhooks", []) if isinstance(data, dict) else []
        logger.info("Webhooks retrieved", count=len(hooks))
        return hooks

    async def create_webhook(
        self, endpoint_url: str, provider_type: str, tailnet: str | None = None,
        secret: str | None = None, subscriptions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a webhook endpoint."""
        t = tailnet or self.tailnet
        body: dict[str, Any] = {"endpointUrl": endpoint_url, "providerType": provider_type}
        if secret:
            body["secret"] = secret
        if subscriptions:
            body["subscriptions"] = subscriptions
        return await self._request("POST", f"/tailnet/{t}/webhooks", json=body)

    async def get_webhook(self, webhook_id: str, tailnet: str | None = None) -> dict[str, Any]:
        """Get a specific webhook."""
        t = tailnet or self.tailnet
        return await self._request("GET", f"/tailnet/{t}/webhooks/{webhook_id}")

    async def update_webhook(
        self, webhook_id: str, updates: dict[str, Any], tailnet: str | None = None
    ) -> dict[str, Any]:
        """Update a webhook."""
        t = tailnet or self.tailnet
        return await self._request("PATCH", f"/tailnet/{t}/webhooks/{webhook_id}", json=updates)

    async def delete_webhook(self, webhook_id: str, tailnet: str | None = None) -> None:
        """Delete a webhook."""
        t = tailnet or self.tailnet
        await self._request("DELETE", f"/tailnet/{t}/webhooks/{webhook_id}")
        logger.info("Webhook deleted", webhook_id=webhook_id)

    async def rotate_webhook_secret(self, webhook_id: str, tailnet: str | None = None) -> dict[str, Any]:
        """Rotate a webhook's secret."""
        t = tailnet or self.tailnet
        return await self._request("POST", f"/tailnet/{t}/webhooks/{webhook_id}/rotate")

    # --- Tailnet settings ---
    async def get_tailnet_settings(self, tailnet: str | None = None) -> dict[str, Any]:
        """Get tailnet settings."""
        t = tailnet or self.tailnet
        return await self._request("GET", f"/tailnet/{t}/tailnet-settings")

    async def update_tailnet_settings(self, settings: dict[str, Any], tailnet: str | None = None) -> dict[str, Any]:
        """Update tailnet settings."""
        t = tailnet or self.tailnet
        return await self._request("PATCH", f"/tailnet/{t}/tailnet-settings", json=settings)

    # --- Contacts ---
    async def get_contact_preferences(self, tailnet: str | None = None) -> dict[str, Any]:
        """Get contact preferences for a tailnet."""
        t = tailnet or self.tailnet
        return await self._request("GET", f"/tailnet/{t}/contacts")

    async def update_contact_preferences(self, contacts: dict[str, Any], tailnet: str | None = None) -> dict[str, Any]:
        """Update contact preferences."""
        t = tailnet or self.tailnet
        return await self._request("PUT", f"/tailnet/{t}/contacts", json=contacts)
