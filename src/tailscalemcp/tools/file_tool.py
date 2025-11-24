"""Tailscale File tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_file_tool(ctx: ToolContext) -> None:
    """Register the tailscale_file tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_file(
        operation: str,
        file_path: str | None = None,
        recipient_device: str | None = None,
        sender_device: str | None = None,
        expire_hours: int = 24,
        transfer_id: str | None = None,
        save_path: str | None = None,
        status_filter: str | None = None,
    ) -> dict[str, Any]:
        try:
            if operation == "send":
                if not file_path or not recipient_device:
                    raise TailscaleMCPError(
                        "file_path and recipient_device are required for send operation"
                    )
                result = await ctx.taildrop_manager.send_file(
                    file_path, recipient_device, sender_device, expire_hours
                )
                return {
                    "operation": "send",
                    "result": result,
                    "file_path": file_path,
                    "recipient_device": recipient_device,
                    "expire_hours": expire_hours,
                }

            elif operation == "receive":
                # transfer_id is optional when using CLI (receives all pending files)
                result = await ctx.taildrop_manager.receive_file(
                    transfer_id, save_path, accept_all=False
                )
                return {
                    "operation": "receive",
                    "result": result,
                    "transfer_id": transfer_id,
                    "save_path": save_path,
                }

            elif operation == "list":
                transfers = await ctx.taildrop_manager.list_transfers(status_filter)
                return {
                    "operation": "list",
                    "transfers": transfers,
                    "count": len(transfers),
                    "status_filter": status_filter,
                }

            elif operation == "cancel":
                if not transfer_id:
                    raise TailscaleMCPError(
                        "transfer_id is required for cancel operation"
                    )
                result = await ctx.taildrop_manager.cancel_transfer(transfer_id)
                return {
                    "operation": "cancel",
                    "result": result,
                    "transfer_id": transfer_id,
                }

            elif operation == "status":
                if not transfer_id:
                    raise TailscaleMCPError(
                        "transfer_id is required for status operation"
                    )
                result = await ctx.taildrop_manager.get_transfer_status(transfer_id)
                return {
                    "operation": "status",
                    "result": result,
                    "transfer_id": transfer_id,
                }

            elif operation == "stats":
                stats = await ctx.taildrop_manager.get_taildrop_statistics()
                return {
                    "operation": "stats",
                    "statistics": stats,
                }

            elif operation == "cleanup":
                result = await ctx.taildrop_manager.cleanup_expired_transfers()
                return {
                    "operation": "cleanup",
                    "result": result,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_file operation", operation=operation, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to perform file operation: {e}") from e
