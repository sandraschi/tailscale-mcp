"""Tailscale Help tool module."""

import time
from typing import Annotated, Any

import structlog
from pydantic import Field

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._helpers import generate_help_content
from ._tool_types import HelpLevel, HelpTopic
from .mcp_tool_names import GET_HELP

logger = structlog.get_logger(__name__)


def register_help_tool(ctx: ToolContext) -> None:
    """Register get_help (MCP name).

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool(name=GET_HELP)
    async def tailscale_help(
        topic: HelpTopic | None = None,
        level: HelpLevel = "basic",
        category: Annotated[
            str | None,
            Field(
                description=(
                    "Optional sub-filter for future help layouts; core content is selected by `topic`."
                ),
            ),
        ] = None,
        operation: Annotated[
            str | None,
            Field(
                description="When set, narrows help to a specific portmanteau `operation` name.",
            ),
        ] = None,
        include_examples: bool = True,
    ) -> dict[str, Any]:
        """STRUCTURED_HELP — Topics: overview, examples, best_practices, troubleshooting, funnel, sampling.

        **Returns:** ``topic``, ``level``, ``content`` (structured dict or overview), ``generated_at``.
        Unknown ``topic`` values produce ``content`` with ``error`` and ``available_topics``.

        **Errors:** ``TailscaleMCPError`` only on unexpected failure (not on unknown topic).
        """
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
