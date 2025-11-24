"""Tailscale Integration tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_integration_tool(ctx: ToolContext) -> None:
    """Register the tailscale_integration tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_integration(
        operation: str,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
        webhook_events: list[str] | None = None,
        integration_type: str | None = None,
        api_endpoint: str | None = None,
        api_key: str | None = None,
        slack_channel: str | None = None,
        discord_webhook: str | None = None,
        pagerduty_key: str | None = None,
        datadog_api_key: str | None = None,
        test_connection: bool = False,
        webhook_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            if operation == "webhook_create":
                if not webhook_url or not webhook_events:
                    raise TailscaleMCPError(
                        "webhook_url and webhook_events are required for webhook_create operation"
                    )
                result = await ctx.device_manager.create_webhook(
                    webhook_url, webhook_secret, webhook_events
                )
                return {
                    "operation": "webhook_create",
                    "webhook_url": webhook_url,
                    "webhook_events": webhook_events,
                    "webhook_id": result.get("webhook_id"),
                    "result": result,
                }

            elif operation == "webhook_test":
                if not webhook_id:
                    raise TailscaleMCPError(
                        "webhook_id is required for webhook_test operation"
                    )
                result = await ctx.device_manager.test_webhook(webhook_id)
                return {
                    "operation": "webhook_test",
                    "webhook_id": webhook_id,
                    "result": result,
                }

            elif operation == "webhook_list":
                webhooks = await ctx.device_manager.list_webhooks()
                return {
                    "operation": "webhook_list",
                    "webhooks": webhooks,
                    "count": len(webhooks),
                }

            elif operation == "webhook_delete":
                if not webhook_id:
                    raise TailscaleMCPError(
                        "webhook_id is required for webhook_delete operation"
                    )
                result = await ctx.device_manager.delete_webhook(webhook_id)
                return {
                    "operation": "webhook_delete",
                    "webhook_id": webhook_id,
                    "result": result,
                }

            elif operation == "slack":
                if not slack_channel:
                    raise TailscaleMCPError(
                        "slack_channel is required for slack operation"
                    )
                result = await ctx.device_manager.integrate_slack(
                    slack_channel, api_key
                )
                return {
                    "operation": "slack",
                    "slack_channel": slack_channel,
                    "result": result,
                }

            elif operation == "discord":
                if not discord_webhook:
                    raise TailscaleMCPError(
                        "discord_webhook is required for discord operation"
                    )
                result = await ctx.device_manager.integrate_discord(discord_webhook)
                return {
                    "operation": "discord",
                    "discord_webhook": discord_webhook,
                    "result": result,
                }

            elif operation == "pagerduty":
                if not pagerduty_key:
                    raise TailscaleMCPError(
                        "pagerduty_key is required for pagerduty operation"
                    )
                result = await ctx.device_manager.integrate_pagerduty(pagerduty_key)
                return {
                    "operation": "pagerduty",
                    "pagerduty_key": pagerduty_key,
                    "result": result,
                }

            elif operation == "datadog":
                if not datadog_api_key:
                    raise TailscaleMCPError(
                        "datadog_api_key is required for datadog operation"
                    )
                result = await ctx.device_manager.integrate_datadog(
                    datadog_api_key, api_endpoint
                )
                return {
                    "operation": "datadog",
                    "datadog_api_key": datadog_api_key,
                    "api_endpoint": api_endpoint,
                    "result": result,
                }

            elif operation == "test":
                if not integration_type:
                    raise TailscaleMCPError(
                        "integration_type is required for test operation"
                    )
                result = await ctx.device_manager.test_integration(
                    integration_type, api_key, test_connection
                )
                return {
                    "operation": "test",
                    "integration_type": integration_type,
                    "test_connection": test_connection,
                    "result": result,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_integration operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(
                f"Failed to perform integration operation: {e}"
            ) from e
