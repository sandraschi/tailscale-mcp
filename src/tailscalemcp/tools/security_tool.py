"""Tailscale Security tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._tool_types import SecurityOperation
from .mcp_tool_names import RUN_TAILNET_SECURITY

logger = structlog.get_logger(__name__)


def register_security_tool(ctx: ToolContext) -> None:
    """Register run_tailnet_security (MCP name).

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool(name=RUN_TAILNET_SECURITY)
    async def tailscale_security(
        operation: SecurityOperation,
        device_id: str | None = None,
    ) -> dict[str, Any]:
        """AUDIT — Inspect devices for configuration issues (supported ops: audit).

        Tailscale's Admin API provides no security scanning, compliance,
        quarantine, alert, or threat detection endpoints. The ``audit``
        operation checks device posture against configured policies.

        **Returns:** Dict with ``operation`` and domain payloads.

        **Errors:** ``TailscaleMCPError`` on invalid args or backend failures.
        """
        try:
            if operation == "audit":
                filters = {}
                if device_id:
                    filters["device_id"] = device_id
                audit_results = await ctx.audit_ops.audit_devices(filters=filters)
                return {
                    "operation": "audit",
                    "device_id": device_id,
                    "results": audit_results,
                    "issue_count": audit_results.get("issue_count", 0),
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_security operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to perform security operation: {e}") from e
