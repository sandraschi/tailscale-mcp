"""
Advanced Device Management Module

Provides comprehensive device management capabilities including authorization,
SSH access, device tagging, and advanced configuration management.
"""

import os
import time
from typing import Any

import structlog
from pydantic import BaseModel, Field

from .api_client import TailscaleAPIClient
from .config import TailscaleConfig
from .exceptions import TailscaleMCPError
from .models.device import DeviceStatus
from .operations.devices import DeviceOperations

logger = structlog.get_logger(__name__)


class DeviceInfo(BaseModel):
    """Device information model."""

    device_id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Device name")
    hostname: str = Field(..., description="Device hostname")
    os: str = Field(..., description="Operating system")
    ip_addresses: list[str] = Field(..., description="Device IP addresses")
    status: str = Field(..., description="Device status")
    last_seen: float = Field(..., description="Last seen timestamp")
    authorized: bool = Field(..., description="Authorization status")
    tags: list[str] = Field(default_factory=list, description="Device tags")
    ssh_enabled: bool = Field(default=False, description="SSH access enabled")
    is_exit_node: bool = Field(default=False, description="Is exit node")
    is_subnet_router: bool = Field(default=False, description="Is subnet router")
    advertised_routes: list[str] = Field(
        default_factory=list, description="Advertised routes"
    )
    client_version: str = Field(..., description="Tailscale client version")


class SSHKey(BaseModel):
    """SSH key information model."""

    key_id: str = Field(..., description="SSH key identifier")
    public_key: str = Field(..., description="Public key content")
    device_id: str = Field(..., description="Associated device ID")
    created_at: float = Field(..., description="Key creation timestamp")
    last_used: float | None = Field(None, description="Last usage timestamp")
    authorized: bool = Field(default=True, description="Key authorization status")


class DeviceTag(BaseModel):
    """Device tag model."""

    tag: str = Field(..., description="Tag name")
    devices: list[str] = Field(
        default_factory=list, description="Device IDs with this tag"
    )
    created_at: float = Field(..., description="Tag creation timestamp")
    description: str | None = Field(None, description="Tag description")


class AdvancedDeviceManager:
    """Advanced device management with comprehensive features."""

    def __init__(self, api_key: str | None = None, tailnet: str | None = None):
        """Initialize advanced device manager.

        Args:
            api_key: Tailscale API key
            tailnet: Tailnet name
        """
        self.api_key = api_key
        self.tailnet = tailnet
        self.devices: dict[str, DeviceInfo] = {}
        self.ssh_keys: dict[str, SSHKey] = {}
        self.device_tags: dict[str, DeviceTag] = {}
        self.device_groups: dict[str, list[str]] = {}

        # Initialize operations layer for real Tailscale API calls
        config = TailscaleConfig(
            tailscale_api_key=api_key or "",
            tailscale_tailnet=tailnet or "",
        )
        self.device_operations = DeviceOperations(config=config)

        # Keep API client for backward compatibility (will be removed gradually)
        self.api_client = TailscaleAPIClient(api_key=api_key, tailnet=tailnet)

        # Configurable timeout for determining if a device is online
        # Default: 1 hour - balances catching offline devices with reasonable active time
        self.online_timeout_seconds = os.getenv(
            "TAILSCALE_ONLINE_TIMEOUT_SECONDS", "3600"
        )
        try:
            self.online_timeout_seconds = int(self.online_timeout_seconds)
        except ValueError:
            self.online_timeout_seconds = 3600  # Default to 1 hour

        logger.info("Advanced device manager initialized", tailnet=tailnet)

    # -----------------------
    # Unsupported Admin API endpoints (explicit)
    # -----------------------
    async def list_users(self) -> list[dict[str, Any]]:
        """List users in the tailnet (not supported via Admin API).

        Raises:
            TailscaleMCPError: Always; not supported.
        """
        raise TailscaleMCPError(
            "Listing users is not supported via the Tailscale Admin API."
        )

    async def create_user(
        self,
        user_email: str,
        user_role: str | None = None,
        user_permissions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create user (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Creating users is not supported via the Tailscale Admin API."
        )

    async def update_user(
        self,
        user_email: str,
        user_role: str | None = None,
        user_permissions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update user (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Updating users is not supported via the Tailscale Admin API."
        )

    async def delete_user(self, user_email: str) -> dict[str, Any]:
        """Delete user (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Deleting users is not supported via the Tailscale Admin API."
        )

    async def get_user_details(self, user_email: str) -> dict[str, Any]:
        """Get user details (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Getting user details is not supported via the Tailscale Admin API."
        )

    async def auth_key_list(self) -> list[dict[str, Any]]:
        """List auth keys (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Listing authentication keys is not supported via the Tailscale Admin API."
        )

    async def auth_key_create(
        self,
        auth_key_name: str | None = None,
        auth_key_expiry: str | None = None,
        auth_key_reusable: bool | None = None,
        auth_key_ephemeral: bool | None = None,
        auth_key_preauthorized: bool | None = None,
        auth_key_tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create auth key (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Creating authentication keys is not supported via the Tailscale Admin API."
        )

    async def auth_key_revoke(self, auth_key_name: str) -> dict[str, Any]:
        """Revoke auth key (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Revoking authentication keys is not supported via the Tailscale Admin API."
        )

    async def auth_key_rotate(self) -> dict[str, Any]:
        """Rotate expired keys (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Rotating authentication keys is not supported via the Tailscale Admin API."
        )

    async def get_device(self, device_id: str) -> dict[str, Any]:
        """Get device details using real Tailscale API.

        Args:
            device_id: Device ID

        Returns:
            Device information dictionary
        """
        try:
            # Use operations layer
            device = await self.device_operations.get_device(device_id)

            # Convert to dict format expected by tools
            return {
                "device_id": device.id,
                "name": device.name,
                "hostname": device.hostname,
                "os": device.os,
                "ip_addresses": [device.ipv4] if device.ipv4 else [],
                "authorized": device.authorized,
                "tags": device.tags,
                "is_exit_node": False,  # Extract from API if available
                "routes": [],  # Extract from API if available
                "client_version": device.client_version or "unknown",
                "user": "",  # Not available in Device model
                "status": device.status.value,
            }
        except Exception as e:
            logger.error("Error getting device", device_id=device_id, error=str(e))
            raise TailscaleMCPError(f"Failed to get device: {e}") from e

    async def update_device_authorization(
        self, device_id: str, authorize: bool, reason: str | None = None
    ) -> dict[str, Any]:
        """Alias for authorize_device for compatibility with tools."""
        return await self.authorize_device(device_id, authorize, reason)

    async def enable_exit_node(
        self, device_id: str, advertise_routes: list[str] | None = None
    ) -> dict[str, Any]:
        """Enable exit node on a device (best-effort via Admin API).

        Args:
            device_id: Device ID
            advertise_routes: Routes to advertise (e.g., ["0.0.0.0/0"])

        Returns:
            Update result
        """
        try:
            payload: dict[str, Any] = {"isExitNode": True}
            if advertise_routes is not None:
                payload["routes"] = advertise_routes
            result = await self.api_client.update_device(device_id, payload)
            logger.info(
                "Exit node enabled", device_id=device_id, routes=advertise_routes
            )
            return {"device_id": device_id, "result": result}
        except Exception as e:
            logger.error("Error enabling exit node", device_id=device_id, error=str(e))
            raise TailscaleMCPError(f"Failed to enable exit node: {e}") from e

    async def disable_exit_node(self, device_id: str) -> dict[str, Any]:
        """Disable exit node on a device."""
        try:
            result = await self.api_client.update_device(
                device_id, {"isExitNode": False}
            )
            logger.info("Exit node disabled", device_id=device_id)
            return {"device_id": device_id, "result": result}
        except Exception as e:
            logger.error("Error disabling exit node", device_id=device_id, error=str(e))
            raise TailscaleMCPError(f"Failed to disable exit node: {e}") from e

    async def enable_subnet_router(
        self, device_id: str, subnets: list[str]
    ) -> dict[str, Any]:
        """Enable subnet routing by advertising routes on a device."""
        try:
            result = await self.api_client.update_device(device_id, {"routes": subnets})
            logger.info("Subnet router enabled", device_id=device_id, subnets=subnets)
            return {"device_id": device_id, "result": result}
        except Exception as e:
            logger.error(
                "Error enabling subnet router", device_id=device_id, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to enable subnet router: {e}") from e

    async def disable_subnet_router(self, device_id: str) -> dict[str, Any]:
        """Disable subnet routing by clearing advertised routes."""
        try:
            result = await self.api_client.update_device(device_id, {"routes": []})
            logger.info("Subnet router disabled", device_id=device_id)
            return {"device_id": device_id, "result": result}
        except Exception as e:
            logger.error(
                "Error disabling subnet router", device_id=device_id, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to disable subnet router: {e}") from e

    async def authorize_device(
        self, device_id: str, authorize: bool = True, reason: str | None = None
    ) -> dict[str, Any]:
        """Authorize or revoke device authorization.

        Args:
            device_id: Device ID to authorize/revoke
            authorize: Whether to authorize (True) or revoke (False)
            reason: Optional reason for authorization change

        Returns:
            Authorization result
        """
        try:
            # Use operations layer
            device = await self.device_operations.authorize_device(
                device_id, authorize, reason
            )

            logger.info(
                "Device authorization updated",
                device_id=device_id,
                authorized=authorize,
                reason=reason,
            )

            return {
                "device_id": device_id,
                "authorized": device.authorized,
                "reason": reason,
                "timestamp": time.time(),
                "result": device.to_dict(),
            }

        except Exception as e:
            logger.error("Error updating device authorization", error=str(e))
            raise TailscaleMCPError(
                f"Failed to update device authorization: {e}"
            ) from e

    async def rename_device(
        self, device_id: str, new_name: str, update_hostname: bool = False
    ) -> dict[str, Any]:
        """Rename a device.

        Args:
            device_id: Device ID to rename
            new_name: New device name
            update_hostname: Whether to also update hostname

        Returns:
            Rename result
        """
        try:
            # Use operations layer
            device = await self.device_operations.rename_device(device_id, new_name)

            logger.info(
                "Device renamed",
                device_id=device_id,
                new_name=new_name,
                update_hostname=update_hostname,
            )

            return {
                "device_id": device_id,
                "new_name": device.name,
                "hostname_updated": update_hostname,
                "timestamp": time.time(),
                "result": device.to_dict(),
            }

        except Exception as e:
            logger.error("Error renaming device", error=str(e))
            raise TailscaleMCPError(f"Failed to rename device: {e}") from e

    async def tag_device(
        self, device_id: str, tags: list[str], operation: str = "add"
    ) -> dict[str, Any]:
        """Add or remove tags from a device.

        Args:
            device_id: Device ID to tag
            tags: List of tags to add/remove
            operation: Operation type (add, remove, replace)

        Returns:
            Tagging result
        """
        try:
            # Use operations layer
            device = await self.device_operations.tag_device(device_id, tags, operation)

            logger.info(
                "Device tags updated",
                device_id=device_id,
                operation=operation,
                tags=device.tags,
            )

            return {
                "device_id": device_id,
                "tags": device.tags,
                "operation": operation,
                "timestamp": time.time(),
                "result": device.to_dict(),
            }

        except Exception as e:
            logger.error("Error updating device tags", error=str(e))
            raise TailscaleMCPError(f"Failed to update device tags: {e}") from e

    async def enable_ssh_access(
        self, device_id: str, public_key: str, key_name: str | None = None
    ) -> dict[str, Any]:
        """Enable SSH access for a device (not supported via Admin API).

        Raises:
            TailscaleMCPError: Always; not supported by public Admin API.
        """
        raise TailscaleMCPError(
            "Enabling SSH access is not supported via the Tailscale Admin API."
        )

    async def disable_ssh_access(self, device_id: str) -> dict[str, Any]:
        """Disable SSH access (not supported via Admin API)."""
        raise TailscaleMCPError(
            "Disabling SSH access is not supported via the Tailscale Admin API."
        )

    async def list_devices(
        self,
        online_only: bool = False,
        filter_tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """List all devices with optional filtering using real Tailscale API.

        Args:
            online_only: Only return online devices
            filter_tags: Filter devices by tags

        Returns:
            List of device information from real Tailscale API
        """
        try:
            # Use operations layer
            devices = await self.device_operations.list_devices(
                online_only=online_only,
                filter_tags=filter_tags or [],
            )

            # Convert Device models to dict format expected by tools
            devices_list = []
            current_time = time.time()

            for device in devices:
                # Convert Device model to dict
                last_seen_ts = (
                    device.last_seen.timestamp() if device.last_seen else current_time
                )
                is_online = device.status == DeviceStatus.ONLINE

                device_data = {
                    "device_id": device.id,
                    "name": device.name,
                    "hostname": device.hostname,
                    "os": device.os,
                    "ip_addresses": [device.ipv4] if device.ipv4 else [],
                    "status": device.status.value,
                    "online": is_online,
                    "last_seen": last_seen_ts,
                    "time_since_seen": current_time - last_seen_ts
                    if device.last_seen
                    else None,
                    "authorized": device.authorized,
                    "tags": device.tags,
                    "ssh_enabled": False,  # Would need separate API call
                    "is_exit_node": False,  # Extract from API if available
                    "is_subnet_router": False,  # Extract from API if available
                    "advertised_routes": [],  # Extract from API if available
                    "client_version": device.client_version or "unknown",
                    "user": "",  # Not available in Device model
                    "machine_key": device.machine_key or "",
                    "update_available": False,  # Would need separate API call
                }
                devices_list.append(device_data)

            logger.info(
                "Devices listed from real API",
                total_devices=len(devices_list),
                online_only=online_only,
                filter_tags=filter_tags or [],
            )

            return devices_list

        except Exception as e:
            logger.error("Error listing devices from API", error=str(e))
            raise TailscaleMCPError(f"Failed to list devices: {e}") from e

    async def list_devices_by_tag(self, tag: str) -> list[dict[str, Any]]:
        """List devices with a specific tag using live API filter.

        Args:
            tag: Tag to filter by

        Returns:
            List of devices with the tag
        """
        try:
            devices = await self.list_devices(online_only=False, filter_tags=[tag])
            logger.info("Devices listed by tag", tag=tag, device_count=len(devices))
            return devices

        except Exception as e:
            logger.error("Error listing devices by tag", error=str(e))
            raise TailscaleMCPError(f"Failed to list devices by tag: {e}") from e

    async def create_device_group(
        self, group_name: str, device_ids: list[str], description: str | None = None
    ) -> dict[str, Any]:
        """Create a device group.

        Args:
            group_name: Name of the device group
            device_ids: List of device IDs to include
            description: Optional group description

        Returns:
            Group creation result
        """
        try:
            # Validate device IDs
            valid_devices = []
            for device_id in device_ids:
                if device_id in self.devices:
                    valid_devices.append(device_id)
                else:
                    logger.warning("Invalid device ID in group", device_id=device_id)

            self.device_groups[group_name] = valid_devices

            logger.info(
                "Device group created",
                group_name=group_name,
                device_count=len(valid_devices),
                description=description,
            )

            return {
                "group_name": group_name,
                "device_ids": valid_devices,
                "device_count": len(valid_devices),
                "description": description,
                "timestamp": time.time(),
                "message": f"Device group {group_name} created with {len(valid_devices)} devices",
            }

        except Exception as e:
            logger.error("Error creating device group", error=str(e))
            raise TailscaleMCPError(f"Failed to create device group: {e}") from e

    async def get_device_statistics(self) -> dict[str, Any]:
        """Get comprehensive device statistics.

        Returns:
            Device statistics summary
        """
        try:
            api_devices = await self.api_client.list_devices()
            total_devices = len(api_devices)

            authorized_devices = sum(
                1 for d in api_devices if d.get("authorized", True)
            )
            connected = sum(
                1 for d in api_devices if d.get("connectedToControl", False)
            )
            exit_nodes = sum(1 for d in api_devices if d.get("isExitNode", False))
            subnet_routers = sum(1 for d in api_devices if len(d.get("routes", [])) > 0)

            # OS distribution
            os_distribution: dict[str, int] = {}
            for d in api_devices:
                os_name = d.get("os", "unknown")
                os_distribution[os_name] = os_distribution.get(os_name, 0) + 1

            # Tag usage
            tag_usage: dict[str, int] = {}
            for d in api_devices:
                for tag in d.get("tags", []) or []:
                    tag_usage[tag] = tag_usage.get(tag, 0) + 1

            # Client version distribution
            version_distribution: dict[str, int] = {}
            for d in api_devices:
                ver = d.get("clientVersion", "unknown")
                version_distribution[ver] = version_distribution.get(ver, 0) + 1

            return {
                "total_devices": total_devices,
                "authorized_devices": authorized_devices,
                "online_devices": connected,
                "exit_nodes": exit_nodes,
                "subnet_routers": subnet_routers,
                "authorization_rate": (authorized_devices / total_devices * 100)
                if total_devices
                else 0,
                "uptime_percentage": (connected / total_devices * 100)
                if total_devices
                else 0,
                "os_distribution": os_distribution,
                "tag_usage": tag_usage,
                "version_distribution": version_distribution,
            }

        except Exception as e:
            logger.error("Error getting device statistics", error=str(e))
            raise TailscaleMCPError(f"Failed to get device statistics: {e}") from e

    async def search_devices(
        self, query: str, search_fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Search devices by various fields using live API list + filter.

        Args:
            query: Search query
            search_fields: Fields to search in (default: name, hostname, tags)

        Returns:
            List of matching devices
        """
        try:
            # Use operations layer
            devices = await self.device_operations.search_devices(query, search_fields)

            # Convert Device models to dict format
            results: list[dict[str, Any]] = []
            current_time = time.time()

            for device in devices:
                last_seen_ts = (
                    device.last_seen.timestamp() if device.last_seen else current_time
                )
                is_online = device.status == DeviceStatus.ONLINE

                device_dict = {
                    "device_id": device.id,
                    "name": device.name,
                    "hostname": device.hostname,
                    "os": device.os,
                    "tags": device.tags,
                    "status": device.status.value,
                    "online": is_online,
                    "last_seen": last_seen_ts,
                    "authorized": device.authorized,
                    "ip_addresses": [device.ipv4] if device.ipv4 else [],
                }
                results.append(device_dict)

            logger.info(
                "Devices searched",
                query=query,
                search_fields=search_fields,
                matches=len(results),
            )

            return results

        except Exception as e:
            logger.error("Error searching devices", query=query, error=str(e))
            raise TailscaleMCPError(f"Failed to search devices: {e}") from e
