"""LM Link tool: Tailscale + LM Studio remote local LLM (Feb 2026)."""

from typing import Any

import structlog

from ._base import ToolContext
from ._tool_types import LmLinkOperation
from .mcp_tool_names import GET_LM_LINK

logger = structlog.get_logger(__name__)

LM_LINK_DOC = """
LM Link (Feb 2026) is a Tailscale + LM Studio partnership feature for secure remote
access to local LLMs. Your models run on one machine and are used from others over
Tailscale's encrypted mesh—no public internet exposure.

How to use:
1. Install Tailscale on all devices and join the same tailnet.
2. On the machine that will host models: install LM Studio, load/serve a model.
3. In LM Studio: Add a remote machine (or run `lms login` then `lms link enable` in terminal).
4. Other devices in the tailnet then see that host's models as remote options in LM Studio.

Requirements: Tailscale installed and connected; LM Studio with LM Link enabled on the host.
Built on tsnet (Tailscale userspace); traffic is E2E encrypted, not visible to Tailscale or LM Studio backends.
"""


def register_lm_link_tool(ctx: ToolContext) -> None:
    """Register get_lm_link (MCP name; LM Link / remote local LLM)."""

    @ctx.mcp.tool(name=GET_LM_LINK)
    async def tailscale_lm_link(
        operation: LmLinkOperation = "info",
    ) -> dict[str, Any]:
        """LM Link: Tailscale + LM Studio remote local LLM (Feb 2026).

        Get setup instructions and optional tailnet readiness for LM Link.
        LM Link lets you access LLMs on remote devices (over Tailscale) as if local—
        E2E encrypted, zero-config across firewalls.

        Operations:
        - info: Return LM Link description and setup steps.
        - readiness: Check tailscale status (this node) and return whether the tailnet
          is likely ready for LM Link (Tailscale connected; LM Studio setup is per-device).
        """
        if operation == "info":
            return {
                "operation": "info",
                "title": "LM Link - Remote local LLMs over Tailscale",
                "description": LM_LINK_DOC.strip(),
                "links": {
                    "tailscale_blog": "https://tailscale.com/blog/lm-link-remote-llm-access",
                    "lm_studio_docs": "https://lmstudio.ai/docs/lmlink",
                    "get_started": "https://link.lmstudio.ai/",
                },
                "steps": [
                    "Install Tailscale on all devices; join same tailnet.",
                    "On the model host: install LM Studio, load and serve a model.",
                    "In LM Studio: Add a remote machine (or: lms login, lms link enable).",
                    "Other devices see the host's models as remote in LM Studio.",
                ],
            }
        if operation == "readiness":
            try:
                status = await ctx.monitor.get_network_status()
                return {
                    "operation": "readiness",
                    "tailscale_ok": True,
                    "message": "Tailscale is reporting status; ensure LM Studio is installed and LM Link enabled on the model host.",
                    "status_summary": status
                    if isinstance(status, dict)
                    else {"raw": str(status)},
                }
            except Exception as e:
                logger.warning("LM Link readiness check failed", error=str(e))
                return {
                    "operation": "readiness",
                    "tailscale_ok": False,
                    "error": str(e),
                    "message": "Could not get Tailscale status. Install Tailscale and ensure this node is in the tailnet.",
                }
        return {
            "operation": operation,
            "error": "Unknown operation. Use 'info' or 'readiness'.",
        }
