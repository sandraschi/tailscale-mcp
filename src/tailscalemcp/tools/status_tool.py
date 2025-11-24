"""Tailscale Status tool module."""

import time
from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._helpers import generate_status_info

logger = structlog.get_logger(__name__)


def register_status_tool(ctx: ToolContext) -> None:
    """Register the tailscale_status tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_status(
        component: str | None = None,
        detail_level: str = "basic",
        include_metrics: bool = True,
        include_health: bool = True,
        include_performance: bool = False,
        device_filter: str | None = None,
        time_range: str = "1h",
        include_mermaid_diagram: bool = False,
    ) -> dict[str, Any]:
        """Comprehensive system status and health monitoring.

        This tool provides detailed status information:
        - overview: Overall system status
        - devices: Device status and health
        - network: Network connectivity and performance
        - services: Service status (API, monitoring, etc.)
        - metrics: Key performance metrics
        - alerts: Current alerts and issues
        - health: Overall health assessment
        - mcp_server: MCP server capabilities (tools, prompts, resources)
        - mermaid_diagram: Optional Mermaid diagram of tailnet topology (devices, connections, funnels)

        The mcp_server section includes:
        - tools: Count and list of available tools
        - prompts: Count and list of available prompts (with details at advanced/diagnostic levels)
        - resources: Count and list of available resources and resource templates (with details at advanced/diagnostic levels)

        The mermaid_diagram (when include_mermaid_diagram=True) shows:
        - All devices in the tailnet (online/offline status with color coding)
        - Exit nodes and subnet routers (highlighted with special borders)
        - Active Funnels (if any, shown in separate subgraph)
        - Device tags and roles
        - Visual topology of the network (simplified mesh connections)
        - Legend explaining node colors and styles

        Args:
            component: Component to check (overview, devices, network, services, metrics, alerts, health)
            detail_level: Detail level (basic, intermediate, advanced, diagnostic)
            include_metrics: Whether to include performance metrics
            include_health: Whether to include health assessments
            include_performance: Whether to include detailed performance data
            device_filter: Filter devices by status or tags
            time_range: Time range for metrics (1h, 6h, 24h, 7d)
            include_mermaid_diagram: Whether to include Mermaid diagram of tailnet topology (default: False)

        Returns:
            Comprehensive status information with health indicators and optional Mermaid diagram.
            If include_mermaid_diagram=True, the status dict includes a 'mermaid_diagram' field
            containing the Mermaid code that can be rendered in Markdown viewers.

        Raises:
            TailscaleMCPError: If status check fails

        Examples:
            # Basic status check
            tailscale_status()

            # Status with Mermaid diagram
            tailscale_status(include_mermaid_diagram=True)

            # Advanced status with diagram
            tailscale_status(
                detail_level="advanced",
                include_metrics=True,
                include_performance=True,
                include_mermaid_diagram=True
            )

        Notes:
            The Mermaid diagram shows:
            - 🟢 Green nodes: Online devices
            - 🔴 Pink nodes: Offline devices
            - Red border: Exit nodes
            - Teal border: Subnet routers
            - Gold nodes: Active Funnels
            - Device names, tags, and status indicators
        """
        try:
            status_info = await generate_status_info(
                ctx.mcp,
                ctx.device_manager,
                ctx.monitor,
                component,
                detail_level,
                include_metrics,
                include_health,
                include_performance,
                device_filter,
                time_range,
                include_mermaid=include_mermaid_diagram,
                funnel_manager=ctx.funnel_manager,
            )
            return {
                "component": component or "overview",
                "detail_level": detail_level,
                "timestamp": time.time(),
                "status": status_info,
            }

        except Exception as e:
            logger.error(
                "Error generating status information", component=component, error=str(e)
            )
            raise TailscaleMCPError(
                f"Failed to generate status information: {e}"
            ) from e
