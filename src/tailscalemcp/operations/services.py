"""
Service operations for Tailscale Services (TailVIPs).

Provides service management operations using the Tailscale API client.
"""

from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import NotFoundError, TailscaleMCPError
from tailscalemcp.models.service import Service

logger = structlog.get_logger(__name__)


class ServiceOperations:
    """Service layer for Tailscale Services (TailVIPs) operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize service operations.

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

    async def list_services(self) -> list[Service]:
        """List all Tailscale Services (TailVIPs) in the tailnet.

        Returns:
            List of Service models

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            services = await self.client.list_services()
            logger.info("Services retrieved", count=len(services))
            return services

        except Exception as e:
            logger.error("Error listing services", error=str(e))
            raise TailscaleMCPError(f"Failed to list services: {e}") from e

    async def get_service(self, service_id: str) -> Service:
        """Get service details by ID.

        Args:
            service_id: Service ID

        Returns:
            Service model

        Raises:
            NotFoundError: If service not found
            TailscaleMCPError: If API call fails
        """
        try:
            service = await self.client.get_service(service_id)
            logger.info("Service retrieved", service_id=service_id, name=service.name)
            return service

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Error getting service", service_id=service_id, error=str(e))
            raise TailscaleMCPError(f"Failed to get service: {e}") from e

    async def create_service(self, service_payload: dict[str, Any]) -> Service:
        """Create a new Tailscale Service (TailVIP).

        Args:
            service_payload: Service creation payload with:
                - name: str (required) - Service name
                - tailvipIPv4: str (optional) - TailVIP IPv4 address
                - tailvipIPv6: str (optional) - TailVIP IPv6 address
                - magicDNS: str (optional) - MagicDNS name
                - endpoints: list[dict] (optional) - Service endpoints
                    - deviceId: str (required)
                    - port: int (required)
                    - protocol: str (required, "tcp" or "udp")
                - tags: list[str] (optional) - Service tags

        Returns:
            Created Service model

        Raises:
            TailscaleMCPError: If API call fails or validation fails
        """
        try:
            # Validate required fields
            if "name" not in service_payload or not service_payload["name"]:
                raise ValueError("Service name is required")

            service = await self.client.create_service(service_payload)
            logger.info("Service created", service_id=service.id, name=service.name)
            return service

        except Exception as e:
            logger.error(
                "Error creating service",
                name=service_payload.get("name"),
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to create service: {e}") from e

    async def update_service(
        self, service_id: str, service_payload: dict[str, Any]
    ) -> Service:
        """Update an existing Tailscale Service (TailVIP).

        Args:
            service_id: Service ID
            service_payload: Partial service update payload
                - name: str (optional) - Service name
                - tailvipIPv4: str (optional) - TailVIP IPv4 address
                - tailvipIPv6: str (optional) - TailVIP IPv6 address
                - magicDNS: str (optional) - MagicDNS name
                - endpoints: list[dict] (optional) - Service endpoints
                - tags: list[str] (optional) - Service tags

        Returns:
            Updated Service model

        Raises:
            NotFoundError: If service not found
            TailscaleMCPError: If API call fails
        """
        try:
            service = await self.client.update_service(service_id, service_payload)
            logger.info(
                "Service updated",
                service_id=service_id,
                updates=list(service_payload.keys()),
            )
            return service

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Error updating service",
                service_id=service_id,
                updates=list(service_payload.keys()),
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to update service: {e}") from e

    async def delete_service(self, service_id: str) -> None:
        """Delete a Tailscale Service (TailVIP).

        Args:
            service_id: Service ID

        Raises:
            NotFoundError: If service not found
            TailscaleMCPError: If API call fails
        """
        try:
            await self.client.delete_service(service_id)
            logger.info("Service deleted", service_id=service_id)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Error deleting service", service_id=service_id, error=str(e))
            raise TailscaleMCPError(f"Failed to delete service: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
