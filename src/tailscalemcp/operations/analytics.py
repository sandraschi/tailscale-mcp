"""
Analytics operations service layer.

Provides network analytics and usage statistics.
"""

from datetime import datetime, timedelta
from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class AnalyticsOperations:
    """Service layer for analytics and statistics operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize analytics operations.

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

    async def get_usage_analytics(self, days: int = 30) -> dict[str, Any]:
        """Get network usage analytics for the specified time period.

        Args:
            days: Number of days to analyze (default: 30)

        Returns:
            Usage analytics report
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            cutoff_date = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(
                days=days
            )

            # Analyze device activity
            active_devices = []
            inactive_devices = []

            for device in all_devices:
                device_info = {
                    "device_id": device.id,
                    "device_name": device.name,
                    "last_seen": device.last_seen.isoformat()
                    if device.last_seen
                    else None,
                    "status": device.status.value,
                }

                if device.last_seen and device.last_seen >= cutoff_date:
                    active_devices.append(device_info)
                else:
                    inactive_devices.append(device_info)

            # Calculate statistics
            total_devices = len(all_devices)
            online_count = sum(1 for d in all_devices if d.status.value == "online")
            authorized_count = sum(1 for d in all_devices if d.authorized)

            analytics = {
                "period_days": days,
                "total_devices": total_devices,
                "active_devices_count": len(active_devices),
                "inactive_devices_count": len(inactive_devices),
                "online_devices_count": online_count,
                "authorized_devices_count": authorized_count,
                "active_devices": active_devices[:10],  # Limit for brevity
                "inactive_devices": inactive_devices[:10],
                "activity_rate": (
                    len(active_devices) / total_devices if total_devices > 0 else 0
                ),
                "analysis_timestamp": datetime.now(
                    datetime.now().astimezone().tzinfo
                ).isoformat(),
            }

            logger.info(
                "Usage analytics retrieved",
                total_devices=total_devices,
                active=len(active_devices),
            )
            return analytics

        except Exception as e:
            logger.error("Error getting usage analytics", error=str(e))
            raise TailscaleMCPError(f"Failed to get usage analytics: {e}") from e

    async def get_device_activity_trends(self, days: int = 7) -> dict[str, Any]:
        """Get device activity trends over time.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            Activity trends report
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            # Group devices by activity periods
            now = datetime.now(datetime.now().astimezone().tzinfo)
            trends: dict[str, int] = {
                "last_hour": 0,
                "last_24_hours": 0,
                "last_7_days": 0,
                "last_30_days": 0,
                "older": 0,
            }

            for device in all_devices:
                if not device.last_seen:
                    trends["older"] += 1
                    continue

                time_diff = now - device.last_seen
                if time_diff < timedelta(hours=1):
                    trends["last_hour"] += 1
                elif time_diff < timedelta(hours=24):
                    trends["last_24_hours"] += 1
                elif time_diff < timedelta(days=7):
                    trends["last_7_days"] += 1
                elif time_diff < timedelta(days=30):
                    trends["last_30_days"] += 1
                else:
                    trends["older"] += 1

            result = {
                "period_days": days,
                "activity_trends": trends,
                "total_devices": len(all_devices),
                "analysis_timestamp": now.isoformat(),
            }

            logger.info("Device activity trends retrieved")
            return result

        except Exception as e:
            logger.error("Error getting activity trends", error=str(e))
            raise TailscaleMCPError(f"Failed to get activity trends: {e}") from e

    async def get_network_statistics(self) -> dict[str, Any]:
        """Get overall network statistics.

        Returns:
            Network statistics report
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            stats = {
                "total_devices": len(all_devices),
                "online_devices": sum(
                    1 for d in all_devices if d.status.value == "online"
                ),
                "offline_devices": sum(
                    1 for d in all_devices if d.status.value == "offline"
                ),
                "unauthorized_devices": sum(1 for d in all_devices if not d.authorized),
                "devices_by_os": {},
                "devices_with_tags": sum(1 for d in all_devices if d.tags),
                "devices_without_tags": sum(1 for d in all_devices if not d.tags),
            }

            # Count by OS
            for device in all_devices:
                os_name = device.os
                stats["devices_by_os"][os_name] = (
                    stats["devices_by_os"].get(os_name, 0) + 1
                )

            logger.info("Network statistics retrieved", total=stats["total_devices"])
            return stats

        except Exception as e:
            logger.error("Error getting network statistics", error=str(e))
            raise TailscaleMCPError(f"Failed to get network statistics: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
