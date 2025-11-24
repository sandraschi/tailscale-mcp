"""Tailscale Funnel tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_funnel_tool(ctx: ToolContext) -> None:
    """Register the tailscale_funnel tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_funnel(
        operation: str,
        port: int | None = None,
        allow_tcp: bool = True,
        allow_tls: bool = True,
    ) -> dict[str, Any]:
        """Comprehensive Funnel operations for exposing local services to the public internet.

        This portmanteau tool provides complete Tailscale Funnel functionality for securely
        exposing local services to the public internet via HTTPS with automatic TLS certificates.
        Funnel enables you to share local development servers, web applications, or APIs
        without complex port forwarding or manual certificate management.

        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 5 separate tools (one per operation), this tool consolidates related
        Funnel operations into a single interface. This design:
        - Prevents tool explosion (5 tools → 1 tool) while maintaining full functionality
        - Improves discoverability by grouping related operations together
        - Reduces cognitive load when working with Funnel tasks
        - Enables atomic batch operations across multiple Funnel actions
        - Follows FastMCP 2.12+ best practices for feature-rich MCP servers

        The 'operation' parameter determines which specific action to perform, while other parameters
        are operation-specific. This pattern is used throughout the Tailscale MCP server for all
        major feature areas (device, network, file, security, etc.).

        Use this tool to enable Funnel for local services, disable Funnel, check Funnel status,
        list active Funnels, and get certificate information. All operations use the Tailscale CLI
        with proper error handling and status reporting.

        SUPPORTED OPERATIONS:

        Funnel Management:
        - funnel_enable: Enable Funnel for a specific port.
          Exposes a local service on the specified port to the public internet via HTTPS.
          Returns a public URL that can be accessed from anywhere.

        - funnel_disable: Disable Funnel for a port or all ports.
          Stops exposing the service to the public internet.

        - funnel_status: Get current Funnel status.
          Returns information about all active Funnel services.

        - funnel_list: List all active Funnel services.
          Shows all ports currently exposed via Funnel with their public URLs.

        - funnel_certificate_info: Get certificate information for a Funnel service.
          Returns TLS certificate details for a specific Funnel service.

        Prerequisites:
            - Tailscale CLI must be installed and accessible
            - Tailscale version 1.38.3 or later required
            - Funnel must be enabled in your tailnet's access control policy
            - The device must have the 'funnel' node attribute in ACL policy

        Parameters:
            operation: Operation to perform. MUST be one of:
                - 'funnel_enable': Enable Funnel for a port
                - 'funnel_disable': Disable Funnel
                - 'funnel_status': Get Funnel status
                - 'funnel_list': List active Funnels
                - 'funnel_certificate_info': Get certificate info

            port: Port number (1-65535). Required for: funnel_enable, funnel_disable, funnel_certificate_info.
                Example: 8080, 3000, 8000

            allow_tcp: Allow TCP connections. Used by: funnel_enable operation. Default: True

            allow_tls: Allow TLS connections. Used by: funnel_enable operation. Default: True

        Returns:
            Dictionary containing operation results. Structure varies by operation.

        Examples:
            Enable Funnel for port 8080:
                result = await tailscale_funnel(operation='funnel_enable', port=8080)

            Disable Funnel:
                result = await tailscale_funnel(operation='funnel_disable', port=8080)

            Get status:
                result = await tailscale_funnel(operation='funnel_status')

        Errors:
            Common errors and solutions:
            - Tailscale CLI not found: Install Tailscale CLI
            - Funnel not enabled in ACL: Add 'funnel' node attribute to ACL policy
            - Invalid port: Port must be between 1 and 65535

        See Also:
            - tailscale_device: For device management
            - tailscale_network: For DNS and network configuration
        """
        try:
            if not ctx.funnel_manager:
                raise TailscaleMCPError(
                    "Funnel manager not initialized. Funnel support requires Tailscale CLI."
                )

            # Set storage on manager if available (FastMCP 2.13+)
            if hasattr(ctx.mcp, "storage") and ctx.mcp.storage:
                ctx.funnel_manager.mcp_storage = ctx.mcp.storage

            if operation == "funnel_enable":
                if port is None:
                    raise TailscaleMCPError(
                        "port is required for funnel_enable operation"
                    )
                result = await ctx.funnel_manager.enable_funnel(
                    port=port, allow_tcp=allow_tcp, allow_tls=allow_tls
                )
                return {
                    "operation": "funnel_enable",
                    **result,
                }

            elif operation == "funnel_disable":
                result = await ctx.funnel_manager.disable_funnel(port=port)
                return {
                    "operation": "funnel_disable",
                    **result,
                }

            elif operation == "funnel_status":
                result = await ctx.funnel_manager.get_funnel_status()
                return {
                    "operation": "funnel_status",
                    **result,
                }

            elif operation == "funnel_list":
                funnels = await ctx.funnel_manager.list_funnels()
                return {
                    "operation": "funnel_list",
                    "funnels": funnels,
                    "count": len(funnels),
                }

            elif operation == "funnel_certificate_info":
                if port is None:
                    raise TailscaleMCPError(
                        "port is required for funnel_certificate_info operation"
                    )
                result = await ctx.funnel_manager.get_certificate_info(port=port)
                return {
                    "operation": "funnel_certificate_info",
                    **result,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_funnel operation", operation=operation, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to perform Funnel operation: {e}") from e
