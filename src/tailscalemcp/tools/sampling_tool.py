"""SEP-1577 agentic workflows: sampling with tools (no mock tool paths)."""

import logging
from typing import Any

import structlog
from fastmcp import Context

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)
_log = logging.getLogger(__name__)


def _success(
    summary: str,
    result: dict[str, Any],
    *,
    iterations: int,
    executed_tools: list[str],
) -> dict[str, Any]:
    return {
        "success": True,
        "operation": "tailscale_agentic_workflow",
        "summary": summary,
        "result": result,
        "iterations": iterations,
        "executed_tools": executed_tools,
        "recommendations": [
            "Review tool outputs and repeat with a narrower prompt if needed.",
            "Use tailscale_status(component='mcp_server') to list available tool names.",
        ],
    }


def _error(
    message: str,
    *,
    error_code: str,
    recovery_options: list[str],
) -> dict[str, Any]:
    return {
        "success": False,
        "operation": "tailscale_agentic_workflow",
        "error": message,
        "error_code": error_code,
        "recovery_options": recovery_options,
    }


def register_sampling_tool(ctx: ToolContext) -> None:
    """Register tailscale_agentic_workflow and tailscale_sampling (alias)."""

    mcp = ctx.mcp

    async def _run_agentic(
        workflow_prompt: str,
        available_tools: list[str],
        max_iterations: int,
        context: Context | None,
    ) -> dict[str, Any]:
        if not workflow_prompt or not workflow_prompt.strip():
            return _error(
                "workflow_prompt is required",
                error_code="MISSING_WORKFLOW_PROMPT",
                recovery_options=["Provide a clear goal for the agentic workflow."],
            )
        if not available_tools:
            return _error(
                "available_tools cannot be empty",
                error_code="EMPTY_TOOLS_LIST",
                recovery_options=[
                    "Include at least one registered tool name, e.g. tailscale_device, tailscale_status."
                ],
            )
        if context is None or not hasattr(context, "sample_step"):
            return _error(
                "Sampling context not available (needs FastMCP 3.1+ with sampling support)",
                error_code="SAMPLING_UNAVAILABLE",
                recovery_options=[
                    "Use an MCP client that supports sampling with tools",
                    "Configure TAILSCALE_SAMPLING_* for server-side Ollama/OpenAI-compatible HTTP",
                    "Set TAILSCALE_SAMPLING_USE_CLIENT_LLM=1 if the host provides sampling",
                ],
            )

        all_tools = await mcp.list_tools()
        name_to_tool = {t.name: t for t in all_tools if hasattr(t, "name")}
        tools_for_sampling = [
            name_to_tool[n] for n in available_tools if n in name_to_tool
        ]
        missing = [n for n in available_tools if n not in name_to_tool]
        if missing:
            _log.warning("Agentic workflow: tools not registered: %s", missing)
        if not tools_for_sampling:
            return _error(
                f"None of available_tools matched registered tools. Missing: {missing}. "
                f"Registered include: {list(name_to_tool.keys())[:40]}...",
                error_code="TOOLS_NOT_FOUND",
                recovery_options=[
                    "Call tailscale_status(component='mcp_server') for the full tool list."
                ],
            )

        system_prompt = (
            "You are a Tailscale network assistant. Use the provided MCP tools to accomplish the "
            "user's goal against the Tailscale Admin API. Be concise; cite device IDs and facts from "
            "tool results. After finishing tool use, summarize outcomes and next steps."
        )
        messages: list = [{"role": "user", "content": workflow_prompt}]
        executed: list[str] = []
        iterations = 0
        step: Any = None

        while iterations < max_iterations:
            iterations += 1
            _log.info("Tailscale agentic step %s/%s", iterations, max_iterations)
            step = await context.sample_step(
                messages,
                system_prompt=system_prompt,
                tools=tools_for_sampling,
                execute_tools=True,
                max_tokens=4096,
            )
            if hasattr(step, "history") and step.history:
                messages = list(step.history)
            if hasattr(step, "tool_calls") and step.tool_calls:
                for tc in step.tool_calls:
                    name = getattr(tc, "name", None) or getattr(
                        tc, "tool_name", str(tc)
                    )
                    if name:
                        executed.append(str(name))
            is_tool = getattr(step, "is_tool_use", True)
            if not is_tool:
                final_text = getattr(step, "text", "") or ""
                return _success(
                    f"Completed in {iterations} round(s).",
                    result={
                        "final_output": final_text,
                        "iterations": iterations,
                        "executed_tools": list(dict.fromkeys(executed)),
                    },
                    iterations=iterations,
                    executed_tools=list(dict.fromkeys(executed)),
                )

        final_out = ""
        if step is not None:
            final_out = getattr(step, "text", "") or ""
        return _success(
            f"Stopped after {max_iterations} iterations (limit).",
            result={
                "final_output": final_out or "(max iterations reached)",
                "iterations": iterations,
                "executed_tools": list(dict.fromkeys(executed)),
            },
            iterations=iterations,
            executed_tools=list(dict.fromkeys(executed)),
        )

    @mcp.tool()
    async def tailscale_agentic_workflow(
        workflow_prompt: str,
        available_tools: list[str],
        max_iterations: int = 5,
        context: Context | None = None,
    ) -> dict[str, Any]:
        """Run multi-step Tailscale workflows via SEP-1577 (sampling with tools).

        Uses ``context.sample_step`` in a loop: the model chooses tools, results are
        applied, until the model returns a final text answer or ``max_iterations`` is hit.

        Requires FastMCP 3.1+ with sampling support. Server-side LLM: set
        ``TAILSCALE_SAMPLING_BASE_URL`` (default Ollama ``http://127.0.0.1:11434/v1``) and
        ``TAILSCALE_SAMPLING_MODEL``, or set ``TAILSCALE_SAMPLING_USE_CLIENT_LLM=1`` for
        host-provided sampling.

        Args:
            workflow_prompt: What you want done (natural language).
            available_tools: Registered tool names the model may call (e.g. tailscale_device, tailscale_status).
            max_iterations: Maximum LLM/tool rounds (default 5).

        Returns:
            Dict with success, result (final_output, iterations, executed_tools), or error.
        """
        try:
            return await _run_agentic(
                workflow_prompt, available_tools, max_iterations, context
            )
        except Exception as e:
            logger.exception("tailscale_agentic_workflow failed")
            raise TailscaleMCPError(f"Agentic workflow failed: {e}") from e

    @mcp.tool()
    async def tailscale_sampling(
        workflow_prompt: str,
        available_tools: list[str],
        max_iterations: int = 5,
        context: Context | None = None,
    ) -> dict[str, Any]:
        """Deprecated alias for ``tailscale_agentic_workflow`` (same parameters)."""
        return await tailscale_agentic_workflow(
            workflow_prompt, available_tools, max_iterations, context
        )
