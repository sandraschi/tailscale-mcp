"""Partner tailnets / people & sharing — portmanteau tool."""

from collections import defaultdict
from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._tool_types import PartnerTailnetsOperation
from .mcp_tool_names import SUMMARIZE_PARTNER_TAILNETS

logger = structlog.get_logger(__name__)


def _group_devices_by_login(
    devices: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    by_login: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for d in devices:
        login = (d.get("user") or "").strip() or "(unknown)"
        slim = {
            "id": d.get("id") or d.get("device_id"),
            "name": d.get("name"),
            "hostname": d.get("hostname"),
            "online": d.get("online"),
            "os": d.get("os"),
        }
        by_login[login].append(slim)
    return dict(sorted(by_login.items(), key=lambda x: x[0].lower()))


def register_partner_tailnets_tool(ctx: ToolContext) -> None:
    """Register summarize_partner_tailnets (MCP name)."""

    @ctx.mcp.tool(name=SUMMARIZE_PARTNER_TAILNETS)
    async def tailscale_partner_tailnets(
        operation: PartnerTailnetsOperation,
        user_type: str | None = None,
        role: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """PARTNER_TAILNETS — People, membership, and tailnet-shared users in one place.

        PORTMANTEAU PATTERN RATIONALE: Answers “who is on my tailnet?”, “who came from
        shared tailnets?”, and “which devices belong to which login?” without juggling
        three different tools.

        Uses Tailscale Admin API ``GET /users`` (``type=member|shared`` filters) plus
        device grouping by node ``user`` when the API returns it.

        Args:
            operation: One of: ``summary``, ``users_list``, ``user_get``, ``devices_by_login``.
            user_type: For ``users_list``: optional ``member`` or ``shared``.
            role: For ``users_list``: optional API role filter (e.g. ``admin``).
            user_id: For ``user_get``: user UUID from ``users_list`` (not email).

        Returns:
            Dict with success, structured sections, counts, and recommendations.
        """
        try:
            if operation == "summary":
                users: list[dict[str, Any]] = []
                users_error: str | None = None
                try:
                    users = await ctx.device_manager.list_users()
                except Exception as e:
                    users_error = str(e)
                    logger.warning(
                        "partner_tailnets summary: users API failed", error=users_error
                    )

                devices = await ctx.device_manager.list_devices()
                by_login = _group_devices_by_login(devices)

                members = [
                    u for u in users if (u.get("type") or "").lower() == "member"
                ]
                shared = [u for u in users if (u.get("type") or "").lower() == "shared"]
                unknown_type = [
                    u
                    for u in users
                    if (u.get("type") or "").lower() not in ("member", "shared")
                ]

                logins_from_devices = set(by_login.keys()) - {"(unknown)"}
                logins_from_users = {
                    u.get("loginName") or "" for u in users if u.get("loginName")
                }
                only_in_devices = logins_from_devices - logins_from_users
                only_in_users = logins_from_users - logins_from_devices

                recs: list[str] = []
                if users_error:
                    recs.append(
                        "Users API failed — check API key scopes and tailnet admin role; "
                        "device grouping still shows node owners when present."
                    )
                if unknown_type:
                    recs.append(
                        f"{len(unknown_type)} user(s) have nonstandard type values; "
                        "see raw `users`."
                    )
                if "(unknown)" in by_login and len(by_login["(unknown)"]) > 0:
                    recs.append(
                        "Some devices have no `user` field in the API response; "
                        "upgrade tailscaled or verify API version."
                    )
                if only_in_devices:
                    recs.append(
                        "Logins seen on devices but not in /users list (often normal for "
                        f"tagged servers): {', '.join(sorted(only_in_devices)[:8])}"
                        + ("…" if len(only_in_devices) > 8 else "")
                    )
                if only_in_users:
                    recs.append(
                        "Users in /users with no devices yet: "
                        + ", ".join(sorted(only_in_users)[:8])
                        + ("…" if len(only_in_users) > 8 else "")
                    )

                return {
                    "success": True,
                    "operation": "summary",
                    "tailnet": ctx.device_manager.tailnet,
                    "users": users,
                    "users_api_error": users_error,
                    "counts": {
                        "users_total": len(users),
                        "users_member": len(members),
                        "users_shared": len(shared),
                        "devices": len(devices),
                        "distinct_device_logins": len(by_login),
                    },
                    "members": members,
                    "shared_tailnet_users": shared,
                    "devices_by_login": by_login,
                    "analysis": {
                        "logins_only_on_devices": sorted(only_in_devices),
                        "users_without_matching_device_login": sorted(only_in_users),
                    },
                    "recommendations": recs
                    or [
                        "Use `users_list` with user_type=`shared` to focus tailnet-shared users.",
                        "Cross-check pending invites in the admin console (not always exposed via API).",
                    ],
                }

            if operation == "users_list":
                users = await ctx.device_manager.list_users(
                    user_type=user_type, role=role
                )
                return {
                    "success": True,
                    "operation": "users_list",
                    "users": users,
                    "count": len(users),
                    "filters": {"user_type": user_type, "role": role},
                }

            if operation == "user_get":
                if not user_id or not str(user_id).strip():
                    raise TailscaleMCPError(
                        "user_id is required for user_get (UUID from users_list)"
                    )
                user = await ctx.device_manager.get_user_details(str(user_id).strip())
                return {
                    "success": True,
                    "operation": "user_get",
                    "user": user,
                }

            if operation == "devices_by_login":
                devices = await ctx.device_manager.list_devices()
                by_login = _group_devices_by_login(devices)
                return {
                    "success": True,
                    "operation": "devices_by_login",
                    "devices_by_login": by_login,
                    "device_count": len(devices),
                }

            raise TailscaleMCPError(
                f"Unknown operation: {operation!r}. "
                "Use summary, users_list, user_get, or devices_by_login."
            )

        except TailscaleMCPError:
            raise
        except Exception as e:
            logger.exception("tailscale_partner_tailnets failed")
            raise TailscaleMCPError(f"partner_tailnets failed: {e}") from e
