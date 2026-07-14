"""LM Link tool: Tailscale + LM Studio remote local LLM (Feb 2026).

Wraps the ``lms link`` CLI for programmatic LM Link management alongside
Tailscale readiness checks. Operations: info, readiness, enable, disable,
status, set_device_name, set_preferred_device.

Also provides a Prefab UI card (``@mcp.tool(app=True)``) for rich in-chat
visualization of LM Link peers and models.
"""

import asyncio
import json
import shutil
import time
from typing import Any

import structlog

from ._base import ToolContext
from ._helpers import build_auth_error_response, is_auth_error
from ._tool_types import LmLinkOperation
from .mcp_tool_names import GET_LM_LINK

logger = structlog.get_logger(__name__)

_TOOL_PROCESS_STARTED_AT = time.time()

LM_LINK_DOC = """
LM Link (Feb 2026) is a Tailscale + LM Studio partnership feature for secure remote
access to local LLMs. Your models run on one machine and are used from others over
Tailscale's encrypted mesh -- no public internet exposure.

How to use:
1. Install Tailscale on all devices and join the same tailnet.
2. On the machine that will host models: install LM Studio, load/serve a model.
3. In LM Studio: Add a remote machine (or run `lms login` then `lms link enable` in terminal).
4. Other devices in the tailnet then see that host's models as remote options in LM Studio.

Requirements: Tailscale installed and connected; LM Studio with LM Link enabled on the host.
Built on tsnet (Tailscale userspace); traffic is E2E encrypted, not visible to Tailscale or LM Studio backends.
"""


def _find_lms_binary() -> str | None:
    """Find the ``lms`` CLI binary on the system.

    Returns the path if found, None otherwise.
    """
    # 'lms' is the LM Studio CLI, shipped with the LM Studio app or the
    # standalone llmster package (curl install.sh).  It may or may not
    # be on PATH depending on the install method.
    lms_in_path = shutil.which("lms")
    if lms_in_path:
        return lms_in_path
    # Common Windows install paths
    candidates = [
        r"C:\Users\sandr\AppData\Local\Programs\lm-studio\lms.exe",
        r"C:\Program Files\lm-studio\lms.exe",
    ]
    import os
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


async def _run_lms(args: list[str], timeout: int = 30) -> dict[str, Any]:
    """Run ``lms <args>`` via async subprocess and return structured result.

    Returns a dict with ``ok``, ``stdout``, ``stderr``, ``exit_code``.
    Adds ``parsed`` (JSON) when the cmd produces parseable JSON output.
    """
    binary = _find_lms_binary()
    if binary is None:
        return {
            "ok": False,
            "error": "lms CLI not found — install LM Studio or llmster (curl -fsSL https://lmstudio.ai/install.sh | bash)",
            "error_type": "lms_not_found",
            "recovery": "Install LM Studio from https://lmstudio.ai/download or run `curl -fsSL https://lmstudio.ai/install.sh | bash` for the headless CLI.",
        }
    cmd = [binary, *args]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
        result: dict[str, Any] = {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }
        # Try to parse JSON output (used by `lms link status --json`)
        if stdout and proc.returncode == 0:
            try:
                result["parsed"] = json.loads(stdout)
            except json.JSONDecodeError:
                pass
        return result
    except TimeoutError:
        return {
            "ok": False,
            "error": f"lms command timed out after {timeout}s",
            "error_type": "timeout",
        }
    except FileNotFoundError:
        return {
            "ok": False,
            "error": "lms binary disappeared (race condition?) — retry",
            "error_type": "binary_missing",
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "error_type": "subprocess_error",
        }


def register_lm_link_tool(ctx: ToolContext) -> None:
    """Register get_lm_link (MCP name; LM Link / remote local LLM)."""

    @ctx.mcp.tool(name=GET_LM_LINK)
    async def tailscale_lm_link(
        operation: LmLinkOperation = "status",
        name: str | None = None,
        device: str | None = None,
    ) -> dict[str, Any]:
        """LM Link: manage remote local LLMs over Tailscale.

        LM Link (Tailscale + LM Studio, Feb 2026) lets you run models on a
        powerful remote machine and access them from other devices on your
        tailnet as if they were local — E2E encrypted, no public internet.

        Operations:
        - info: Return LM Link description and setup steps.
        - readiness: Check tailscale status and whether LM Link is likely ready.
        - status: Show live LM Link state — this device, connected peers, their
          loaded models. Calls ``lms link status --json``.
        - enable: Enable LM Link on this device (``lms link enable``).
        - disable: Disable LM Link on this device (``lms link disable``).
        - set_device_name: Rename this device on the link (``lms link set-device-name``).
        - set_preferred_device: Choose which remote device to prefer for model
          loading when the same model exists on multiple peers.

        ## Return Format
        ```json
        {"operation": "<op>", "ok": true, "message": "...", "data": {...}}
        ```

        ## Examples
        tailscale_lm_link(operation="status")
        tailscale_lm_link(operation="enable")
        tailscale_lm_link(operation="set_device_name", name="gpu-rig")
        tailscale_lm_link(operation="set_preferred_device", device="office-pc")
        """
        # -- info -----------------------------------------------------------
        if operation == "info":
            return {
                "operation": "info",
                "ok": True,
                "title": "LM Link - Remote local LLMs over Tailscale",
                "description": LM_LINK_DOC.strip(),
                "lms_cli_available": _find_lms_binary() is not None,
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

        # -- readiness ------------------------------------------------------
        if operation == "readiness":
            try:
                status = await ctx.monitor.get_network_status()
                lms_ok = _find_lms_binary() is not None
                return {
                    "operation": "readiness",
                    "ok": True,
                    "tailscale_ok": True,
                    "lms_installed": lms_ok,
                    "message": (
                        "Tailscale is reporting status. "
                        + (
                            "lms CLI found — ready for LM Link operations."
                            if lms_ok
                            else "LM Studio / lms CLI not found — install LM Studio for LM Link."
                        )
                    ),
                    "status_summary": status if isinstance(status, dict) else {"raw": str(status)},
                }
            except Exception as e:
                logger.warning("LM Link readiness check failed", error=str(e))
                if is_auth_error(e):
                    payload = build_auth_error_response(
                        "readiness", e, server_started_at=_TOOL_PROCESS_STARTED_AT
                    )
                    return {
                        "operation": "readiness",
                        "ok": False,
                        "tailscale_ok": False,
                        "error_type": "authentication",
                        **payload,
                        "message": (
                            "Tailscale API authentication failed — see "
                            "recovery_options for stale-credentials vs "
                            "invalid-key diagnosis."
                        ),
                    }
                return {
                    "operation": "readiness",
                    "ok": False,
                    "tailscale_ok": False,
                    "error": str(e),
                    "message": "Could not get Tailscale status. Install Tailscale and ensure this node is in the tailnet.",
                }

        # -- status ---------------------------------------------------------
        if operation == "status":
            result = await _run_lms(["link", "status", "--json"])
            if result["ok"] and "parsed" in result:
                data = result["parsed"]
                return {
                    "operation": "status",
                    "ok": True,
                    "message": f"LM Link status: {data.get('connection_state', 'unknown')}",
                    "data": data,
                    "device_name": data.get("device_name", "unknown"),
                    "connected": data.get("enabled", False),
                    "peers": data.get("peers", []),
                    "peer_count": len(data.get("peers", [])),
                }
            if not result["ok"]:
                # lms might not be logged in (lms login required)
                return {
                    "operation": "status",
                    "ok": False,
                    "error": result.get("error") or result.get("stderr") or "lms link status failed",
                    "error_type": result.get("error_type", "cli_error"),
                    "message": (
                        "Could not get LM Link status. Ensure lms is installed "
                        "and you are logged in: `lms login` then `lms link enable`."
                    ),
                    "raw": result,
                }
            return {
                "operation": "status",
                "ok": True,
                "message": "LM Link status returned but no parseable JSON",
                "raw_stdout": result.get("stdout", ""),
            }

        # -- enable ---------------------------------------------------------
        if operation == "enable":
            result = await _run_lms(["link", "enable"])
            if result["ok"]:
                return {
                    "operation": "enable",
                    "ok": True,
                    "message": "LM Link enabled. Run `status` to verify peer connections.",
                }
            return {
                "operation": "enable",
                "ok": False,
                "error": result.get("error") or result.get("stderr") or "Failed to enable LM Link",
                "error_type": result.get("error_type", "cli_error"),
                "message": "Make sure you are logged in: `lms login` first, then retry.",
                "raw": result,
            }

        # -- disable --------------------------------------------------------
        if operation == "disable":
            result = await _run_lms(["link", "disable"])
            if result["ok"]:
                return {
                    "operation": "disable",
                    "ok": True,
                    "message": "LM Link disabled. This device is no longer visible to peers.",
                }
            return {
                "operation": "disable",
                "ok": False,
                "error": result.get("error") or result.get("stderr") or "Failed to disable LM Link",
                "error_type": result.get("error_type", "cli_error"),
                "message": "LM Link may not have been enabled. Run `status` to check current state.",
                "raw": result,
            }

        # -- set_device_name ------------------------------------------------
        if operation == "set_device_name":
            if not name:
                return {
                    "operation": "set_device_name",
                    "ok": False,
                    "error": "name parameter is required",
                    "error_type": "missing_parameter",
                    "message": "Provide a name for this device on the LM Link (e.g., 'gpu-rig').",
                }
            result = await _run_lms(["link", "set-device-name", name])
            if result["ok"]:
                return {
                    "operation": "set_device_name",
                    "ok": True,
                    "name": name,
                    "message": f"Device name set to '{name}'.",
                }
            return {
                "operation": "set_device_name",
                "ok": False,
                "error": result.get("error") or result.get("stderr") or "Failed to set device name",
                "error_type": result.get("error_type", "cli_error"),
                "message": "Make sure LM Link is enabled and you are logged in.",
                "raw": result,
            }

        # -- set_preferred_device -------------------------------------------
        if operation == "set_preferred_device":
            if not device:
                return {
                    "operation": "set_preferred_device",
                    "ok": False,
                    "error": "device parameter is required",
                    "error_type": "missing_parameter",
                    "message": "Provide the name of the remote device to prefer (from `status` peer list).",
                }
            result = await _run_lms(["link", "set-preferred-device", device])
            if result["ok"]:
                return {
                    "operation": "set_preferred_device",
                    "ok": True,
                    "preferred_device": device,
                    "message": f"Preferred device set to '{device}'. Models will load from this device first.",
                }
            return {
                "operation": "set_preferred_device",
                "ok": False,
                "error": result.get("error") or result.get("stderr") or "Failed to set preferred device",
                "error_type": result.get("error_type", "cli_error"),
                "message": f"Check that '{device}' is a connected peer (run `status` first).",
                "raw": result,
            }

        # -- fallback -------------------------------------------------------
        return {
            "operation": operation,
            "ok": False,
            "error": f"Unknown operation: '{operation}'",
            "error_type": "invalid_operation",
            "valid_operations": [
                "info", "readiness", "status", "enable", "disable",
                "set_device_name", "set_preferred_device",
            ],
        }

    # -- Prefab UI card -------------------------------------------------------
    _prefab_registered = False
    try:
        from fastmcp.server.server import ToolResult
        from prefab_ui import PrefabApp
        from prefab_ui.components import Badge as PBadge
        from prefab_ui.components import Heading, Row

        _prefab_registered = True
    except ImportError:
        logger.warning("prefab-ui not installed — show_lm_link_card not registered")

    if _prefab_registered:

        @ctx.mcp.tool(app=True)
        async def show_lm_link_card() -> ToolResult:
            """Show LM Link peers and their loaded models as a rich Prefab card.

            Displays the current device's link state, connected peers, and
            the models each peer has loaded — all in a structured card
            suitable for in-chat viewing. Falls back to plain text when
            Prefab rendering is unavailable.

            ## Return Format
            ToolResult with PrefabApp card and plain-text fallback.

            ## Examples
            show_lm_link_card()
            """
            data = await tailscale_lm_link(operation="status")
            peers = data.get("peers", [])
            device = data.get("device_name", "unknown")
            enabled = data.get("connected", data.get("ok", False))

            with PrefabApp(title="LM Link") as app:
                Heading(f"Device: {device}")
                PBadge(
                    "Connected" if enabled else "Inactive",
                    variant="success" if enabled else "error",
                )

                if peers:
                    Heading(f"Peers ({len(peers)})", level=3)
                    for p in peers:
                        pname = p.get("device_name", p.get("name", "?"))
                        models = p.get("models", p.get("loaded_models", []))
                        pref = " [preferred]" if p.get("preferred") else ""
                        Row(
                            label=f"{pname}{pref}",
                            value=f"{len(models)} model(s)" if models else "no models",
                        )
                else:
                    if enabled:
                        Row(label="No peers connected", value="add a device in LM Studio")
                    else:
                        Row(label="LM Link inactive", value="enable via get_lm_link(operation='enable')")

            summary = (
                f"LM Link — {device}: {len(peers)} peer(s), "
                f"{'connected' if enabled else 'inactive'}"
            )
            return ToolResult(content=summary, structured_content=app)
