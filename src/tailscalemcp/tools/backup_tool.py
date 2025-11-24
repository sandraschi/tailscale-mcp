"""Tailscale Backup tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_backup_tool(ctx: ToolContext) -> None:
    """Register the tailscale_backup tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_backup(
        operation: str,
        backup_name: str | None = None,
        backup_type: str = "full",
        include_devices: bool = True,
        include_policies: bool = True,
        include_users: bool = True,
        restore_point: str | None = None,  # noqa: ARG001
        backup_id: str | None = None,
        schedule_cron: str | None = None,
        retention_days: int = 30,
        compression: bool = True,
        encryption: bool = True,
        test_restore: bool = False,
    ) -> dict[str, Any]:
        try:
            if operation == "backup_create":
                if not backup_name:
                    raise TailscaleMCPError(
                        "backup_name is required for backup_create operation"
                    )
                result = await ctx.device_manager.create_backup(
                    backup_name,
                    backup_type,
                    include_devices,
                    include_policies,
                    include_users,
                    compression,
                    encryption,
                )
                return {
                    "operation": "backup_create",
                    "backup_name": backup_name,
                    "backup_type": backup_type,
                    "backup_id": result.get("backup_id"),
                    "result": result,
                }

            elif operation == "backup_restore":
                if not backup_id:
                    raise TailscaleMCPError(
                        "backup_id is required for backup_restore operation"
                    )
                result = await ctx.device_manager.restore_backup(
                    backup_id, test_restore
                )
                return {
                    "operation": "backup_restore",
                    "backup_id": backup_id,
                    "test_restore": test_restore,
                    "result": result,
                }

            elif operation == "backup_schedule":
                if not schedule_cron:
                    raise TailscaleMCPError(
                        "schedule_cron is required for backup_schedule operation"
                    )
                result = await ctx.device_manager.schedule_backups(
                    schedule_cron, retention_days
                )
                return {
                    "operation": "backup_schedule",
                    "schedule_cron": schedule_cron,
                    "retention_days": retention_days,
                    "result": result,
                }

            elif operation == "backup_list":
                backups = await ctx.device_manager.list_backups()
                return {
                    "operation": "backup_list",
                    "backups": backups,
                    "count": len(backups),
                }

            elif operation == "backup_delete":
                if not backup_id:
                    raise TailscaleMCPError(
                        "backup_id is required for backup_delete operation"
                    )
                result = await ctx.device_manager.delete_backup(backup_id)
                return {
                    "operation": "backup_delete",
                    "backup_id": backup_id,
                    "result": result,
                }

            elif operation == "backup_test":
                if not backup_id:
                    raise TailscaleMCPError(
                        "backup_id is required for backup_test operation"
                    )
                result = await ctx.device_manager.test_backup_integrity(backup_id)
                return {
                    "operation": "backup_test",
                    "backup_id": backup_id,
                    "result": result,
                }

            elif operation == "restore_test":
                if not backup_id:
                    raise TailscaleMCPError(
                        "backup_id is required for restore_test operation"
                    )
                result = await ctx.device_manager.test_restore_procedure(backup_id)
                return {
                    "operation": "restore_test",
                    "backup_id": backup_id,
                    "result": result,
                }

            elif operation == "recovery_plan":
                result = await ctx.device_manager.create_recovery_plan()
                return {
                    "operation": "recovery_plan",
                    "result": result,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_backup operation", operation=operation, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to perform backup operation: {e}") from e
