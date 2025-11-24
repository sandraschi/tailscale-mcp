"""
Tag operations service layer.

Provides tag management and tag-based access control automation.
"""

from typing import Any

import structlog

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import NotFoundError, TailscaleMCPError

logger = structlog.get_logger(__name__)


class TagOperations:
    """Service layer for tag management operations."""

    def __init__(
        self,
        config: TailscaleConfig | None = None,
        api_key: str | None = None,
        tailnet: str | None = None,
    ):
        """Initialize tag operations.

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

    async def list_all_tags(self) -> list[str]:
        """List all unique tags used across all devices.

        Returns:
            List of unique tag strings

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            tags: set[str] = set()
            for device in all_devices:
                tags.update(device.tags)

            tag_list = sorted(tags)
            logger.info("All tags listed", tag_count=len(tag_list))
            return tag_list

        except Exception as e:
            logger.error("Error listing tags", error=str(e))
            raise TailscaleMCPError(f"Failed to list tags: {e}") from e

    async def get_devices_by_tag(self, tag: str) -> list[dict[str, Any]]:
        """Get all devices that have a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of device information dictionaries with the tag

        Raises:
            TailscaleMCPError: If API call fails
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            matching_devices = [d for d in all_devices if tag in d.tags]

            result = [
                {
                    "device_id": d.id,
                    "device_name": d.name,
                    "tags": d.tags,
                    "status": d.status.value,
                    "authorized": d.authorized,
                }
                for d in matching_devices
            ]

            logger.info("Devices by tag retrieved", tag=tag, count=len(result))
            return result

        except Exception as e:
            logger.error("Error getting devices by tag", tag=tag, error=str(e))
            raise TailscaleMCPError(f"Failed to get devices by tag: {e}") from e

    async def batch_update_tags(
        self,
        device_ids: list[str],
        tags: list[str],
        operation: str = "add",
    ) -> dict[str, Any]:
        """Batch update tags on multiple devices.

        Args:
            device_ids: List of device IDs to update
            tags: Tags to add/remove/replace
            operation: Operation type - "add", "remove", or "replace"

        Returns:
            Result summary with success/failure counts

        Raises:
            TailscaleMCPError: If batch operation fails
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)

            success_count = 0
            failed_count = 0
            errors: list[dict[str, Any]] = []

            for device_id in device_ids:
                try:
                    await device_ops.tag_device(device_id, tags, operation)
                    success_count += 1
                except NotFoundError as e:
                    failed_count += 1
                    errors.append({"device_id": device_id, "error": str(e)})
                except Exception as e:
                    failed_count += 1
                    errors.append({"device_id": device_id, "error": str(e)})

            result = {
                "total": len(device_ids),
                "success": success_count,
                "failed": failed_count,
                "errors": errors,
            }

            logger.info(
                "Batch tag update completed",
                total=len(device_ids),
                success=success_count,
                failed=failed_count,
            )
            return result

        except Exception as e:
            logger.error("Error in batch tag update", error=str(e))
            raise TailscaleMCPError(f"Failed to batch update tags: {e}") from e

    async def validate_tag_naming(self, tag: str) -> dict[str, Any]:
        """Validate tag naming conventions.

        Args:
            tag: Tag to validate

        Returns:
            Validation result with status and messages
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Tailscale tags must start with "tag:"
        if not tag.startswith("tag:"):
            errors.append('Tags must start with "tag:"')

        # Check length
        if len(tag) > 64:
            errors.append("Tag exceeds maximum length of 64 characters")

        # Check for valid characters
        if not all(c.isalnum() or c in ["-", "_", ":"] for c in tag[4:]):
            errors.append(
                "Tag contains invalid characters. Only alphanumeric, '-', and '_' allowed after 'tag:'"
            )

        # Check for reserved names
        reserved = ["tag:autogroup", "tag:api"]
        for reserved_tag in reserved:
            if tag.lower().startswith(reserved_tag):
                warnings.append(f"Tag may conflict with reserved tag: {reserved_tag}")

        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

        logger.debug("Tag validated", tag=tag, valid=result["valid"])
        return result

    async def audit_tag_usage(self) -> dict[str, Any]:
        """Audit tag usage across all devices.

        Returns:
            Tag usage report with statistics
        """
        try:
            from tailscalemcp.operations.devices import DeviceOperations

            device_ops = DeviceOperations(self.config)
            all_devices = await device_ops.list_devices()

            tag_stats: dict[str, dict[str, Any]] = {}

            for device in all_devices:
                for tag in device.tags:
                    if tag not in tag_stats:
                        tag_stats[tag] = {
                            "tag": tag,
                            "device_count": 0,
                            "devices": [],
                        }
                    tag_stats[tag]["device_count"] += 1
                    tag_stats[tag]["devices"].append(
                        {
                            "device_id": device.id,
                            "device_name": device.name,
                        }
                    )

            # Sort by usage
            sorted_tags = sorted(
                tag_stats.items(), key=lambda x: x[1]["device_count"], reverse=True
            )

            result = {
                "total_unique_tags": len(tag_stats),
                "tag_statistics": [stats for _, stats in sorted_tags],
                "unused_tags": [],
            }

            logger.info("Tag usage audit completed", unique_tags=len(tag_stats))
            return result

        except Exception as e:
            logger.error("Error auditing tag usage", error=str(e))
            raise TailscaleMCPError(f"Failed to audit tag usage: {e}") from e

    async def close(self) -> None:
        """Close the API client connection."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
