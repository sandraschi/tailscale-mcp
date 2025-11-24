"""
Device operations service layer.

Provides device management operations using the Tailscale API client.
"""

from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import NotFoundError, TailscaleMCPError
from tailscalemcp.models.device import Device, DeviceStatus

logger = structlog.get_logger(__name__)


class DeviceOperations:
    """Service layer for device operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize device operations.

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

    async def list_devices(
        self, online_only: bool = False, filter_tags: list[str] | None = None
    ) -> list[Device]:
        """List all devices in the tailnet.

        Args:
            online_only: Only return online devices
            filter_tags: Filter devices by tags (must have all specified tags)

        Returns:
            List of Device models

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            devices_data = await self.client.list_devices()
            devices = [Device.from_api_response(d) for d in devices_data]

            # Filter by online status
            if online_only:
                devices = [d for d in devices if d.status == DeviceStatus.ONLINE]

            # Filter by tags
            if filter_tags:
                devices = [
                    d for d in devices if all(tag in d.tags for tag in filter_tags)
                ]

            logger.info(
                "Devices retrieved",
                count=len(devices),
                online_only=online_only,
                filter_tags=filter_tags,
            )
            return devices

        except Exception as e:
            logger.error("Error listing devices", error=str(e))
            raise TailscaleMCPError(f"Failed to list devices: {e}") from e

    async def get_device(self, device_id: str) -> Device:
        """Get device details by ID.

        Args:
            device_id: Device ID or stable ID

        Returns:
            Device model

        Raises:
            NotFoundError: If device not found
            TailscaleMCPError: If API call fails
        """
        try:
            device_data = await self.client.get_device(device_id)
            device = Device.from_api_response(device_data)

            logger.info("Device retrieved", device_id=device_id, name=device.name)
            return device

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Error getting device", device_id=device_id, error=str(e))
            raise TailscaleMCPError(f"Failed to get device: {e}") from e

    async def update_device(self, device_id: str, updates: dict[str, Any]) -> Device:
        """Update device (rename, tags, authorization, etc.).

        Args:
            device_id: Device ID or stable ID
            updates: Dictionary of updates to apply
                - authorized: bool - Set authorization status
                - tags: list[str] - Update device tags
                - hostname: str - Update hostname
                - name: str - Update device name

        Returns:
            Updated Device model

        Raises:
            NotFoundError: If device not found
            TailscaleMCPError: If API call fails
        """
        try:
            updated_data = await self.client.update_device(device_id, updates)
            device = Device.from_api_response(updated_data)

            logger.info(
                "Device updated",
                device_id=device_id,
                updates=list(updates.keys()),
            )
            return device

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Error updating device",
                device_id=device_id,
                updates=list(updates.keys()),
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to update device: {e}") from e

    async def authorize_device(
        self, device_id: str, authorize: bool, reason: str | None = None
    ) -> Device:
        """Authorize or revoke device authorization.

        Args:
            device_id: Device ID or stable ID
            authorize: True to authorize, False to revoke
            reason: Optional reason for authorization change

        Returns:
            Updated Device model

        Raises:
            NotFoundError: If device not found
            TailscaleMCPError: If API call fails
        """
        updates = {"authorized": authorize}
        if reason:
            updates["authorizedReason"] = reason

        return await self.update_device(device_id, updates)

    async def rename_device(self, device_id: str, name: str) -> Device:
        """Rename a device.

        Args:
            device_id: Device ID or stable ID
            name: New device name

        Returns:
            Updated Device model

        Raises:
            NotFoundError: If device not found
            TailscaleMCPError: If API call fails
        """
        return await self.update_device(device_id, {"name": name})

    async def tag_device(
        self, device_id: str, tags: list[str], operation: str = "add"
    ) -> Device:
        """Update device tags.

        Args:
            device_id: Device ID or stable ID
            tags: Tags to add/remove/replace
            operation: Operation type - "add", "remove", or "replace"

        Returns:
            Updated Device model

        Raises:
            NotFoundError: If device not found
            TailscaleMCPError: If API call fails
        """
        # Get current device to see existing tags
        device = await self.get_device(device_id)

        if operation == "add":
            new_tags = list(set(device.tags + tags))
        elif operation == "remove":
            new_tags = [t for t in device.tags if t not in tags]
        elif operation == "replace":
            new_tags = tags
        else:
            raise ValueError(
                f"Invalid operation: {operation}. Use 'add', 'remove', or 'replace'"
            )

        return await self.update_device(device_id, {"tags": new_tags})

    async def delete_device(self, device_id: str) -> None:
        """Delete a device from the tailnet.

        Args:
            device_id: Device ID or stable ID

        Raises:
            NotFoundError: If device not found
            TailscaleMCPError: If API call fails
        """
        try:
            await self.client.delete_device(device_id)
            logger.info("Device deleted", device_id=device_id)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Error deleting device", device_id=device_id, error=str(e))
            raise TailscaleMCPError(f"Failed to delete device: {e}") from e

    async def search_devices(
        self, query: str, search_fields: list[str] | None = None
    ) -> list[Device]:
        """Search devices by name, tags, or other fields.

        Args:
            query: Search query string
            search_fields: Fields to search in (default: ["name", "hostname", "tags"])

        Returns:
            List of matching Device models

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            if search_fields is None:
                search_fields = ["name", "hostname", "tags"]

            # Get all devices and filter locally
            all_devices = await self.list_devices()

            matching_devices = []
            query_lower = query.lower()

            for device in all_devices:
                matched = False

                if ("name" in search_fields and query_lower in device.name.lower()) or (
                    "hostname" in search_fields
                    and query_lower in device.hostname.lower()
                ):
                    matched = True
                elif "tags" in search_fields:
                    for tag in device.tags:
                        if query_lower in tag.lower():
                            matched = True
                            break
                elif "os" in search_fields and query_lower in device.os.lower():
                    matched = True

                if matched:
                    matching_devices.append(device)

            logger.info(
                "Devices searched",
                query=query,
                search_fields=search_fields,
                matches=len(matching_devices),
            )
            return matching_devices

        except Exception as e:
            logger.error("Error searching devices", query=query, error=str(e))
            raise TailscaleMCPError(f"Failed to search devices: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
