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
from .exceptions import TailscaleMCPError

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

        # Initialize API client for real Tailscale API calls
        self.api_client = TailscaleAPIClient(api_key=api_key, tailnet=tailnet)

        # Configurable timeout for determining if a device is online
        # Default: 1 hour - balances catching offline devices with reasonable active time
        self.online_timeout_seconds = os.getenv("TAILSCALE_ONLINE_TIMEOUT_SECONDS", "3600")
        try:
            self.online_timeout_seconds = int(self.online_timeout_seconds)
        except ValueError:
            self.online_timeout_seconds = 3600  # Default to 1 hour

        logger.info("Advanced device manager initialized", tailnet=tailnet)


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
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")

            device = self.devices[device_id]
            device.authorized = authorize

            logger.info(
                "Device authorization updated",
                device_id=device_id,
                device_name=device.name,
                authorized=authorize,
                reason=reason,
            )

            return {
                "device_id": device_id,
                "device_name": device.name,
                "authorized": authorize,
                "reason": reason,
                "timestamp": time.time(),
                "message": f"Device {device.name} {'authorized' if authorize else 'revoked'}",
            }

        except Exception as e:
            logger.error("Error updating device authorization", error=str(e))
            raise TailscaleMCPError(f"Failed to update device authorization: {e}") from e

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
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")

            device = self.devices[device_id]
            old_name = device.name
            device.name = new_name

            if update_hostname:
                device.hostname = new_name

            logger.info(
                "Device renamed",
                device_id=device_id,
                old_name=old_name,
                new_name=new_name,
            )

            return {
                "device_id": device_id,
                "old_name": old_name,
                "new_name": new_name,
                "hostname_updated": update_hostname,
                "timestamp": time.time(),
                "message": f"Device renamed from {old_name} to {new_name}",
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
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")

            device = self.devices[device_id]
            old_tags = device.tags.copy()

            if operation == "add":
                for tag in tags:
                    if tag not in device.tags:
                        device.tags.append(tag)
                        # Update tag registry
                        if tag not in self.device_tags:
                            self.device_tags[tag] = DeviceTag(
                                tag=tag, devices=[device_id], created_at=time.time()
                            )
                        else:
                            if device_id not in self.device_tags[tag].devices:
                                self.device_tags[tag].devices.append(device_id)

            elif operation == "remove":
                for tag in tags:
                    if tag in device.tags:
                        device.tags.remove(tag)
                        # Update tag registry
                        if tag in self.device_tags and device_id in self.device_tags[tag].devices:
                            self.device_tags[tag].devices.remove(device_id)

            elif operation == "replace":
                device.tags = tags
                # Update all tag registries
                for tag in old_tags:
                    if (
                        tag in self.device_tags
                        and device_id in self.device_tags[tag].devices
                    ):
                        self.device_tags[tag].devices.remove(device_id)
                for tag in tags:
                    if tag not in self.device_tags:
                        self.device_tags[tag] = DeviceTag(
                            tag=tag, devices=[device_id], created_at=time.time()
                        )
                    else:
                        if device_id not in self.device_tags[tag].devices:
                            self.device_tags[tag].devices.append(device_id)

            logger.info(
                "Device tags updated",
                device_id=device_id,
                device_name=device.name,
                operation=operation,
                old_tags=old_tags,
                new_tags=device.tags,
            )

            return {
                "device_id": device_id,
                "device_name": device.name,
                "operation": operation,
                "old_tags": old_tags,
                "new_tags": device.tags,
                "timestamp": time.time(),
                "message": f"Tags {operation}ed for device {device.name}",
            }

        except Exception as e:
            logger.error("Error updating device tags", error=str(e))
            raise TailscaleMCPError(f"Failed to update device tags: {e}") from e

    async def enable_ssh_access(
        self, device_id: str, public_key: str, key_name: str | None = None
    ) -> dict[str, Any]:
        """Enable SSH access for a device.

        Args:
            device_id: Device ID to enable SSH for
            public_key: SSH public key
            key_name: Optional name for the key

        Returns:
            SSH access result
        """
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")

            device = self.devices[device_id]
            device.ssh_enabled = True

            # Create SSH key record
            key_id = f"{device_id}_{int(time.time())}"
            ssh_key = SSHKey(
                key_id=key_id,
                public_key=public_key,
                device_id=device_id,
                created_at=time.time(),
            )

            self.ssh_keys[key_id] = ssh_key

            logger.info(
                "SSH access enabled",
                device_id=device_id,
                device_name=device.name,
                key_id=key_id,
            )

            return {
                "device_id": device_id,
                "device_name": device.name,
                "ssh_enabled": True,
                "key_id": key_id,
                "timestamp": time.time(),
                "message": f"SSH access enabled for device {device.name}",
            }

        except Exception as e:
            logger.error("Error enabling SSH access", error=str(e))
            raise TailscaleMCPError(f"Failed to enable SSH access: {e}") from e

    async def disable_ssh_access(self, device_id: str) -> dict[str, Any]:
        """Disable SSH access for a device.

        Args:
            device_id: Device ID to disable SSH for

        Returns:
            SSH disable result
        """
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")

            device = self.devices[device_id]
            device.ssh_enabled = False

            # Remove SSH keys for this device
            keys_to_remove = [
                key_id
                for key_id, key in self.ssh_keys.items()
                if key.device_id == device_id
            ]
            for key_id in keys_to_remove:
                del self.ssh_keys[key_id]

            logger.info(
                "SSH access disabled", device_id=device_id, device_name=device.name
            )

            return {
                "device_id": device_id,
                "device_name": device.name,
                "ssh_enabled": False,
                "removed_keys": len(keys_to_remove),
                "timestamp": time.time(),
                "message": f"SSH access disabled for device {device.name}",
            }

        except Exception as e:
            logger.error("Error disabling SSH access", error=str(e))
            raise TailscaleMCPError(f"Failed to disable SSH access: {e}") from e

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
            # Make real API call to Tailscale
            api_devices = await self.api_client.list_devices()

            devices_list = []
            current_time = time.time()

            for api_device in api_devices:
                # Map API response to our format
                device_id = api_device.get("id", "")

                # Parse lastSeen timestamp
                last_seen_raw = api_device.get("lastSeen")
                if isinstance(last_seen_raw, str):
                    from datetime import datetime
                    try:
                        last_seen_ts = datetime.fromisoformat(last_seen_raw.replace("Z", "+00:00")).timestamp()
                    except Exception:
                        last_seen_ts = current_time
                else:
                    last_seen_ts = last_seen_raw if last_seen_raw else current_time

                # Determine online status based on connectedToControl and lastSeen
                # This is a compromise: connectedToControl is known to be unreliable for iOS devices
                # that remain "connected" in the background even when off
                connected_to_control = api_device.get("connectedToControl", False)

                # Calculate time since last seen
                time_since_seen = current_time - last_seen_ts if last_seen_ts else float("inf")

                # Use configurable timeout (default: 1 hour)
                # Devices that haven't been seen within this timeframe are considered offline
                # regardless of connectedToControl status. This helps with iOS devices that
                # report connectedToControl=True when off
                recently_active = time_since_seen < self.online_timeout_seconds

                # Device is online if connected AND recently active
                is_online = connected_to_control and recently_active

                # Apply online filter
                if online_only and not is_online:
                    continue

                # Apply tag filtering
                if filter_tags:
                    device_tags = api_device.get("tags", [])
                    matching_tags = [tag for tag in filter_tags if tag in device_tags]
                    if not matching_tags:
                        continue

                # Extract device information from API response
                addresses = api_device.get("addresses", [])

                device_data = {
                    "device_id": device_id,
                    "name": api_device.get("name", "unknown"),
                    "hostname": api_device.get("hostname", "unknown"),
                    "os": api_device.get("os", "unknown"),
                    "ip_addresses": addresses,
                    "status": "online" if is_online else "offline",
                    "online": is_online,
                    "last_seen": last_seen_ts,
                    "time_since_seen": current_time - last_seen_ts if last_seen_ts else None,
                    "authorized": api_device.get("authorized", True),
                    "tags": api_device.get("tags", []),
                    "ssh_enabled": False,  # Would need separate API call
                    "is_exit_node": api_device.get("isExitNode", False),
                    "is_subnet_router": len(api_device.get("routes", [])) > 0,
                    "advertised_routes": api_device.get("routes", []),
                    "client_version": api_device.get("clientVersion", "unknown"),
                    "user": api_device.get("user", ""),
                    "machine_key": api_device.get("machineKey", ""),
                    "update_available": api_device.get("updateAvailable", False),
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
        """List devices with a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of devices with the tag
        """
        try:
            if tag not in self.device_tags:
                return []

            tagged_devices = []
            for device_id in self.device_tags[tag].devices:
                if device_id in self.devices:
                    device = self.devices[device_id]
                    tagged_devices.append(
                        {
                            "device_id": device.device_id,
                            "name": device.name,
                            "hostname": device.hostname,
                            "status": device.status,
                            "authorized": device.authorized,
                            "tags": device.tags,
                            "last_seen": device.last_seen,
                        }
                    )

            logger.info(
                "Devices listed by tag", tag=tag, device_count=len(tagged_devices)
            )

            return tagged_devices

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
            total_devices = len(self.devices)
            authorized_devices = sum(1 for d in self.devices.values() if d.authorized)
            online_devices = sum(
                1 for d in self.devices.values() if d.status == "online"
            )
            ssh_enabled_devices = sum(1 for d in self.devices.values() if d.ssh_enabled)
            exit_nodes = sum(1 for d in self.devices.values() if d.is_exit_node)
            subnet_routers = sum(1 for d in self.devices.values() if d.is_subnet_router)

            # OS distribution
            os_distribution = {}
            for device in self.devices.values():
                os_distribution[device.os] = os_distribution.get(device.os, 0) + 1

            # Tag usage
            tag_usage = {}
            for device in self.devices.values():
                for tag in device.tags:
                    tag_usage[tag] = tag_usage.get(tag, 0) + 1

            # Client version distribution
            version_distribution = {}
            for device in self.devices.values():
                version_distribution[device.client_version] = (
                    version_distribution.get(device.client_version, 0) + 1
                )

            return {
                "total_devices": total_devices,
                "authorized_devices": authorized_devices,
                "online_devices": online_devices,
                "ssh_enabled_devices": ssh_enabled_devices,
                "exit_nodes": exit_nodes,
                "subnet_routers": subnet_routers,
                "authorization_rate": (authorized_devices / total_devices * 100)
                if total_devices > 0
                else 0,
                "uptime_percentage": (online_devices / total_devices * 100)
                if total_devices > 0
                else 0,
                "os_distribution": os_distribution,
                "tag_usage": tag_usage,
                "version_distribution": version_distribution,
                "device_groups": len(self.device_groups),
                "ssh_keys": len(self.ssh_keys),
            }

        except Exception as e:
            logger.error("Error getting device statistics", error=str(e))
            raise TailscaleMCPError(f"Failed to get device statistics: {e}") from e

    async def search_devices(
        self, query: str, search_fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Search devices by various fields.

        Args:
            query: Search query
            search_fields: Fields to search in (default: name, hostname, tags)

        Returns:
            List of matching devices
        """
        try:
            if not search_fields:
                search_fields = ["name", "hostname", "tags"]

            matching_devices = []
            query_lower = query.lower()

            for device in self.devices.values():
                match = False

                if (
                    ("name" in search_fields and query_lower in device.name.lower())
                    or (
                        "hostname" in search_fields
                        and query_lower in device.hostname.lower()
                    )
                    or (
                        "tags" in search_fields
                        and any(query_lower in tag.lower() for tag in device.tags)
                    )
                    or ("os" in search_fields and query_lower in device.os.lower())
                    or (
                        "status" in search_fields
                        and query_lower in device.status.lower()
                    )
                ):
                    match = True

                if match:
                    matching_devices.append(
                        {
                            "device_id": device.device_id,
                            "name": device.name,
                            "hostname": device.hostname,
                            "os": device.os,
                            "status": device.status,
                            "authorized": device.authorized,
                            "tags": device.tags,
                            "last_seen": device.last_seen,
                        }
                    )

            logger.info(
                "Device search completed",
                query=query,
                search_fields=search_fields,
                results_count=len(matching_devices),
            )

            return matching_devices

        except Exception as e:
            logger.error("Error searching devices", error=str(e))
            raise TailscaleMCPError(f"Failed to search devices: {e}") from e
