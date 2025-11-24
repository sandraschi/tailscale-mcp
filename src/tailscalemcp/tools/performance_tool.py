"""Tailscale Performance tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_performance_tool(ctx: ToolContext) -> None:
    """Register the tailscale_performance tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_performance(
        operation: str,
        device_id: str | None = None,
        measure_duration: int = 60,
        bandwidth_test: bool = False,  # noqa: ARG001
        latency_test: bool = False,  # noqa: ARG001
        route_optimization: bool = False,
        baseline_name: str | None = None,
        baseline_duration: int = 300,
        capacity_period: str = "30d",
        scaling_factor: float = 1.2,
        performance_threshold: float = 0.8,
    ) -> dict[str, Any]:
        try:
            if operation == "latency":
                latency_results = await ctx.monitor.measure_latency(
                    device_id, measure_duration
                )
                return {
                    "operation": "latency",
                    "device_id": device_id,
                    "duration": measure_duration,
                    "results": latency_results,
                }

            elif operation == "bandwidth":
                bandwidth_results = await ctx.monitor.bandwidth_analysis(
                    device_id, measure_duration
                )
                return {
                    "operation": "bandwidth",
                    "device_id": device_id,
                    "duration": measure_duration,
                    "results": bandwidth_results,
                }

            elif operation == "optimize":
                optimization_results = await ctx.monitor.optimize_routing(
                    route_optimization
                )
                return {
                    "operation": "optimize",
                    "route_optimization": route_optimization,
                    "results": optimization_results,
                }

            elif operation == "baseline":
                if not baseline_name:
                    raise TailscaleMCPError(
                        "baseline_name is required for baseline operation"
                    )
                baseline_results = await ctx.monitor.performance_baseline(
                    baseline_name, baseline_duration
                )
                return {
                    "operation": "baseline",
                    "baseline_name": baseline_name,
                    "duration": baseline_duration,
                    "results": baseline_results,
                }

            elif operation == "capacity":
                capacity_results = await ctx.monitor.predict_capacity(
                    capacity_period, scaling_factor
                )
                return {
                    "operation": "capacity",
                    "period": capacity_period,
                    "scaling_factor": scaling_factor,
                    "results": capacity_results,
                }

            elif operation == "utilization":
                utilization_results = await ctx.monitor.resource_utilization(device_id)
                return {
                    "operation": "utilization",
                    "device_id": device_id,
                    "results": utilization_results,
                }

            elif operation == "scaling":
                scaling_recommendations = await ctx.monitor.scaling_recommendations(
                    scaling_factor
                )
                return {
                    "operation": "scaling",
                    "scaling_factor": scaling_factor,
                    "recommendations": scaling_recommendations,
                }

            elif operation == "threshold":
                threshold_results = await ctx.monitor.set_performance_threshold(
                    performance_threshold
                )
                return {
                    "operation": "threshold",
                    "threshold": performance_threshold,
                    "results": threshold_results,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_performance operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(
                f"Failed to perform performance operation: {e}"
            ) from e
