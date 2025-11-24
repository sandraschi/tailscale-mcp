"""Tailscale Monitor tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_monitor_tool(ctx: ToolContext) -> None:
    """Register the tailscale_monitor tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_monitor(
        operation: str,
        grafana_url: str | None = None,
        api_key: str | None = None,
        dashboard_type: str = "comprehensive",
        filename: str | None = None,
        include_panels: bool = True,  # noqa: ARG001
        include_variables: bool = True,  # noqa: ARG001
    ) -> dict[str, Any]:
        try:
            if operation == "status":
                status = await ctx.monitor.get_network_status()
                return {
                    "operation": "status",
                    "status": status,
                }

            elif operation == "metrics":
                metrics = await ctx.monitor.collect_metrics()
                return {
                    "operation": "metrics",
                    "metrics": metrics,
                }

            elif operation == "prometheus":
                prometheus_metrics = await ctx.monitor.get_prometheus_metrics()
                return {
                    "operation": "prometheus",
                    "metrics": prometheus_metrics,
                }

            elif operation == "topology":
                topology = await ctx.monitor.generate_network_topology()
                return {
                    "operation": "topology",
                    "topology": topology,
                }

            elif operation == "health":
                health_report = await ctx.monitor.get_network_health_report()
                return {
                    "operation": "health",
                    "health_report": health_report,
                }

            elif operation == "dashboard":
                if not grafana_url or not api_key:
                    raise TailscaleMCPError(
                        "grafana_url and api_key are required for dashboard operation"
                    )
                dashboard_config = await ctx.monitor.create_grafana_dashboard(
                    grafana_url, api_key
                )
                return {
                    "operation": "dashboard_create",
                    "dashboard": dashboard_config,
                    "grafana_url": grafana_url,
                }

            elif operation == "export":
                if not filename:
                    raise TailscaleMCPError("filename is required for export operation")
                if dashboard_type == "comprehensive":
                    dashboard_config = (
                        ctx.grafana_dashboard.create_comprehensive_dashboard()
                    )
                elif dashboard_type == "topology":
                    dashboard_config = (
                        ctx.grafana_dashboard.create_network_topology_dashboard()
                    )
                elif dashboard_type == "security":
                    dashboard_config = ctx.grafana_dashboard.create_security_dashboard()
                else:
                    raise TailscaleMCPError(f"Unknown dashboard type: {dashboard_type}")

                ctx.grafana_dashboard.export_dashboard(dashboard_config, filename)
                return {
                    "operation": "export",
                    "filename": filename,
                    "dashboard_type": dashboard_type,
                    "exported": True,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_monitor operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to perform monitor operation: {e}") from e
