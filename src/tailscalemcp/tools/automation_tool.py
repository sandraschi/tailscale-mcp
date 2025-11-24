"""Tailscale Automation tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_automation_tool(ctx: ToolContext) -> None:
    """Register the tailscale_automation tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_automation(
        operation: str,
        workflow_name: str | None = None,
        workflow_steps: list[dict[str, Any]] | None = None,
        schedule_cron: str | None = None,
        script_content: str | None = None,
        script_language: str = "python",
        template_name: str | None = None,
        batch_operations: list[dict[str, Any]] | None = None,
        dry_run: bool = False,
        execute_now: bool = False,
        workflow_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            if operation == "workflow_create":
                if not workflow_name or not workflow_steps:
                    raise TailscaleMCPError(
                        "workflow_name and workflow_steps are required for workflow_create operation"
                    )
                result = await ctx.device_manager.create_workflow(
                    workflow_name, workflow_steps
                )
                return {
                    "operation": "workflow_create",
                    "workflow_name": workflow_name,
                    "workflow_id": result.get("workflow_id"),
                    "steps_count": len(workflow_steps),
                    "result": result,
                }

            elif operation == "workflow_execute":
                if not workflow_id:
                    raise TailscaleMCPError(
                        "workflow_id is required for workflow_execute operation"
                    )
                result = await ctx.device_manager.execute_workflow(
                    workflow_id, execute_now
                )
                return {
                    "operation": "workflow_execute",
                    "workflow_id": workflow_id,
                    "execute_now": execute_now,
                    "result": result,
                }

            elif operation == "workflow_schedule":
                if not workflow_id or not schedule_cron:
                    raise TailscaleMCPError(
                        "workflow_id and schedule_cron are required for workflow_schedule operation"
                    )
                result = await ctx.device_manager.schedule_workflow(
                    workflow_id, schedule_cron
                )
                return {
                    "operation": "workflow_schedule",
                    "workflow_id": workflow_id,
                    "schedule_cron": schedule_cron,
                    "result": result,
                }

            elif operation == "workflow_list":
                workflows = await ctx.device_manager.list_workflows()
                return {
                    "operation": "workflow_list",
                    "workflows": workflows,
                    "count": len(workflows),
                }

            elif operation == "workflow_delete":
                if not workflow_id:
                    raise TailscaleMCPError(
                        "workflow_id is required for workflow_delete operation"
                    )
                result = await ctx.device_manager.delete_workflow(workflow_id)
                return {
                    "operation": "workflow_delete",
                    "workflow_id": workflow_id,
                    "result": result,
                }

            elif operation == "script_execute":
                if not script_content:
                    raise TailscaleMCPError(
                        "script_content is required for script_execute operation"
                    )
                result = await ctx.device_manager.execute_script(
                    script_content, script_language, dry_run
                )
                return {
                    "operation": "script_execute",
                    "script_language": script_language,
                    "dry_run": dry_run,
                    "result": result,
                }

            elif operation == "script_template":
                if not template_name:
                    raise TailscaleMCPError(
                        "template_name is required for script_template operation"
                    )
                template = await ctx.device_manager.get_script_template(template_name)
                return {
                    "operation": "script_template",
                    "template_name": template_name,
                    "template": template,
                }

            elif operation == "batch":
                if not batch_operations:
                    raise TailscaleMCPError(
                        "batch_operations is required for batch operation"
                    )
                result = await ctx.device_manager.batch_operations(
                    batch_operations, dry_run
                )
                return {
                    "operation": "batch",
                    "operations_count": len(batch_operations),
                    "dry_run": dry_run,
                    "result": result,
                }

            elif operation == "dry_run":
                if not batch_operations:
                    raise TailscaleMCPError(
                        "batch_operations is required for dry_run operation"
                    )
                preview = await ctx.device_manager.preview_operations(batch_operations)
                return {
                    "operation": "dry_run",
                    "preview": preview,
                    "operations_count": len(batch_operations),
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_automation operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(
                f"Failed to perform automation operation: {e}"
            ) from e
