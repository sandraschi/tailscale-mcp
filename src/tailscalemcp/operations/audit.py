"""
Device audit operations service layer.

Provides device auditing, compliance checking, and inventory operations.
"""

from datetime import datetime, timedelta
from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError
from tailscalemcp.models.device import DeviceStatus

logger = structlog.get_logger(__name__)


class AuditOperations:
    """Service layer for device audit and compliance operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize audit operations.

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

    async def audit_devices(
        self,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform comprehensive device audit with compliance checks.

        Args:
            filters: Optional filters:
                - os: Filter by operating system
                - min_version: Minimum client version
                - require_authorized: Only authorized devices
                - require_online: Only online devices
                - tag_required: Devices must have these tags
                - tag_forbidden: Devices must not have these tags

        Returns:
            Audit report with statistics and compliance issues
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            # Apply filters
            if filters:
                if filters.get("os"):
                    all_devices = [
                        d for d in all_devices if d.os.lower() == filters["os"].lower()
                    ]
                if filters.get("require_authorized"):
                    all_devices = [d for d in all_devices if d.authorized]
                if filters.get("require_online"):
                    all_devices = [
                        d for d in all_devices if d.status == DeviceStatus.ONLINE
                    ]
                if filters.get("tag_required"):
                    required_tags = filters["tag_required"]
                    if isinstance(required_tags, str):
                        required_tags = [required_tags]
                    all_devices = [
                        d
                        for d in all_devices
                        if all(tag in d.tags for tag in required_tags)
                    ]
                if filters.get("tag_forbidden"):
                    forbidden_tags = filters["tag_forbidden"]
                    if isinstance(forbidden_tags, str):
                        forbidden_tags = [forbidden_tags]
                    all_devices = [
                        d
                        for d in all_devices
                        if not any(tag in d.tags for tag in forbidden_tags)
                    ]

            # Audit checks
            issues: list[dict[str, Any]] = []
            statistics: dict[str, Any] = {
                "total_devices": len(all_devices),
                "online": 0,
                "offline": 0,
                "unauthorized": 0,
                "expired_keys": 0,
                "outdated_clients": 0,
                "no_tags": 0,
                "by_os": {},
            }

            min_version = filters.get("min_version") if filters else None
            current_time = datetime.now(datetime.now().astimezone().tzinfo)

            for device in all_devices:
                # Count statuses
                if device.status == DeviceStatus.ONLINE:
                    statistics["online"] += 1
                elif device.status == DeviceStatus.OFFLINE:
                    statistics["offline"] += 1

                if not device.authorized:
                    statistics["unauthorized"] += 1
                    issues.append(
                        {
                            "type": "unauthorized",
                            "device_id": device.id,
                            "device_name": device.name,
                            "severity": "high",
                            "message": f"Device {device.name} is not authorized",
                        }
                    )

                # Check key expiry
                if device.expires and device.expires < current_time:
                    statistics["expired_keys"] += 1
                    issues.append(
                        {
                            "type": "expired_key",
                            "device_id": device.id,
                            "device_name": device.name,
                            "severity": "high",
                            "message": f"Device {device.name} has expired key",
                            "expired_at": device.expires.isoformat(),
                        }
                    )

                # Check client version (simplified - would need version comparison logic)
                if (
                    min_version
                    and device.client_version
                    and device.client_version < min_version
                ):
                    statistics["outdated_clients"] += 1
                    issues.append(
                        {
                            "type": "outdated_client",
                            "device_id": device.id,
                            "device_name": device.name,
                            "severity": "medium",
                            "message": f"Device {device.name} has outdated client version",
                            "current_version": device.client_version,
                            "min_version": min_version,
                        }
                    )

                # Check for devices without tags
                if not device.tags:
                    statistics["no_tags"] += 1
                    issues.append(
                        {
                            "type": "no_tags",
                            "device_id": device.id,
                            "device_name": device.name,
                            "severity": "low",
                            "message": f"Device {device.name} has no tags",
                        }
                    )

                # Count by OS
                os_name = device.os
                statistics["by_os"][os_name] = statistics["by_os"].get(os_name, 0) + 1

            # Find stale devices (not seen in 30 days)
            stale_threshold = current_time - timedelta(days=30)
            stale_devices = [
                d for d in all_devices if d.last_seen and d.last_seen < stale_threshold
            ]

            for device in stale_devices:
                issues.append(
                    {
                        "type": "stale_device",
                        "device_id": device.id,
                        "device_name": device.name,
                        "severity": "medium",
                        "message": f"Device {device.name} has not been seen in 30+ days",
                        "last_seen": device.last_seen.isoformat()
                        if device.last_seen
                        else None,
                    }
                )

            result = {
                "statistics": statistics,
                "issues": issues,
                "issue_count": len(issues),
                "stale_devices_count": len(stale_devices),
                "audit_timestamp": current_time.isoformat(),
            }

            logger.info(
                "Device audit completed",
                total_devices=statistics["total_devices"],
                issue_count=len(issues),
            )
            return result

        except Exception as e:
            logger.error("Error performing device audit", error=str(e))
            raise TailscaleMCPError(f"Failed to audit devices: {e}") from e

    async def check_control_plane_connectivity(
        self, hours_threshold: int = 24
    ) -> dict[str, Any]:
        """Check which devices are connected to control plane.

        Args:
            hours_threshold: Alert if device not seen in this many hours

        Returns:
            Connectivity report
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            threshold_time = datetime.now(
                datetime.now().astimezone().tzinfo
            ) - timedelta(hours=hours_threshold)

            connected: list[dict[str, Any]] = []
            disconnected: list[dict[str, Any]] = []

            for device in all_devices:
                device_info = {
                    "device_id": device.id,
                    "device_name": device.name,
                    "connected_to_control": device.connected_to_control,
                    "last_seen": device.last_seen.isoformat()
                    if device.last_seen
                    else None,
                    "status": device.status.value,
                }

                if device.connected_to_control:
                    connected.append(device_info)
                else:
                    disconnected.append(device_info)

                # Check if last seen exceeds threshold
                if device.last_seen and device.last_seen < threshold_time:
                    device_info["alert"] = f"Not seen in {hours_threshold}+ hours"

            result = {
                "connected_count": len(connected),
                "disconnected_count": len(disconnected),
                "connected_devices": connected,
                "disconnected_devices": disconnected,
                "threshold_hours": hours_threshold,
                "check_timestamp": datetime.now(
                    datetime.now().astimezone().tzinfo
                ).isoformat(),
            }

            logger.info(
                "Control plane connectivity checked",
                connected=len(connected),
                disconnected=len(disconnected),
            )
            return result

        except Exception as e:
            logger.error("Error checking control plane connectivity", error=str(e))
            raise TailscaleMCPError(f"Failed to check connectivity: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
