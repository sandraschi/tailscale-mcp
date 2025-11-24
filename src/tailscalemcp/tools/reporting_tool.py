"""Tailscale Reporting tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_reporting_tool(ctx: ToolContext) -> None:
    """Register the tailscale_reporting tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_reporting(
        operation: str,
        report_type: str = "usage",
        report_format: str = "json",
        date_range: str = "30d",
        include_charts: bool = True,
        custom_fields: list[str] | None = None,
        schedule_cron: str | None = None,
        email_recipients: list[str] | None = None,
        export_path: str | None = None,
        template_name: str | None = None,
        analytics_depth: str = "standard",
        security_focus: bool = False,
        user_behavior: bool = False,  # noqa: ARG001
    ) -> dict[str, Any]:
        try:
            if operation == "generate":
                report = await ctx.monitor.generate_usage_report(
                    report_type, date_range, include_charts
                )
                return {
                    "operation": "generate",
                    "report_type": report_type,
                    "date_range": date_range,
                    "report": report,
                }

            elif operation == "usage":
                usage_report = await ctx.monitor.generate_usage_report(
                    "usage", date_range, include_charts
                )
                return {
                    "operation": "usage",
                    "date_range": date_range,
                    "report": usage_report,
                }

            elif operation == "custom":
                if not custom_fields:
                    raise TailscaleMCPError(
                        "custom_fields is required for custom operation"
                    )
                custom_report = await ctx.monitor.create_custom_report(
                    custom_fields, date_range, report_format
                )
                return {
                    "operation": "custom",
                    "custom_fields": custom_fields,
                    "date_range": date_range,
                    "format": report_format,
                    "report": custom_report,
                }

            elif operation == "schedule":
                if not schedule_cron:
                    raise TailscaleMCPError(
                        "schedule_cron is required for schedule operation"
                    )
                result = await ctx.monitor.schedule_reports(
                    schedule_cron, email_recipients
                )
                return {
                    "operation": "schedule",
                    "schedule_cron": schedule_cron,
                    "email_recipients": email_recipients,
                    "result": result,
                }

            elif operation == "export":
                if not export_path:
                    raise TailscaleMCPError(
                        "export_path is required for export operation"
                    )
                result = await ctx.monitor.export_reports(export_path, report_format)
                return {
                    "operation": "export",
                    "export_path": export_path,
                    "format": report_format,
                    "result": result,
                }

            elif operation == "analytics":
                analytics_results = await ctx.monitor.network_analytics(
                    analytics_depth, date_range
                )
                return {
                    "operation": "analytics",
                    "depth": analytics_depth,
                    "date_range": date_range,
                    "results": analytics_results,
                }

            elif operation == "behavior":
                behavior_results = await ctx.monitor.user_behavior_analysis(date_range)
                return {
                    "operation": "behavior",
                    "date_range": date_range,
                    "results": behavior_results,
                }

            elif operation == "security":
                security_results = await ctx.monitor.security_metrics(
                    date_range, security_focus
                )
                return {
                    "operation": "security",
                    "date_range": date_range,
                    "security_focus": security_focus,
                    "results": security_results,
                }

            elif operation == "template":
                if not template_name:
                    raise TailscaleMCPError(
                        "template_name is required for template operation"
                    )
                template = await ctx.monitor.get_report_template(template_name)
                return {
                    "operation": "template",
                    "template_name": template_name,
                    "template": template,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_reporting operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(
                f"Failed to perform reporting operation: {e}"
            ) from e
