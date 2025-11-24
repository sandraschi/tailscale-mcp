"""Tailscale Help tool module."""

import time
from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._helpers import generate_help_content

logger = structlog.get_logger(__name__)


def register_help_tool(ctx: ToolContext) -> None:
    """Register the tailscale_help tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_help(
        topic: str | None = None,
        level: str = "basic",
        category: str | None = None,
        operation: str | None = None,
        include_examples: bool = True,
    ) -> dict[str, Any]:
        try:
            help_content = await generate_help_content(
                topic, level, category, operation, include_examples
            )
            return {
                "topic": topic or "overview",
                "level": level,
                "category": category,
                "operation": operation,
                "content": help_content,
                "generated_at": time.time(),
            }

        except Exception as e:
            logger.error("Error generating help content", topic=topic, error=str(e))
            raise TailscaleMCPError(f"Failed to generate help content: {e}") from e
