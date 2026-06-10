"""Tailscale Device tool module."""

import re
from typing import Annotated, Any

import structlog
from pydantic import Field

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._tool_types import DeviceOperation
from .mcp_tool_names import MANAGE_TAILNET_DEVICES

logger = structlog.get_logger(__name__)


def register_device_tool(ctx: ToolContext) -> None:
    """Register manage_tailnet_devices (MCP name).

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool(name=MANAGE_TAILNET_DEVICES)
    async def tailscale_device(
        operation: DeviceOperation,
        device_id: str | None = None,
        name: str | None = None,
        tags: list[str] | None = None,
        authorize: bool | None = None,
        reason: str | None = None,
        online_only: bool = False,
        filter_tags: list[str] | None = None,
        search_query: str | None = None,
        search_fields: Annotated[
            list[str] | None,
            Field(
                description=(
                    "For operation='search': fields to match against (e.g. name, hostname, tags, id). "
                    "Default in the API layer is name, hostname, tags when omitted."
                ),
            ),
        ] = None,
        enable_exit_node: bool = False,
        advertise_routes: list[str] | None = None,
        enable_subnet_router: bool = False,
        subnets: list[str] | None = None,
        user_email: str | None = None,
        auth_key_name: str | None = None,
        auth_key_expiry: str | None = None,
        auth_key_reusable: bool = False,
        auth_key_ephemeral: bool = False,
        auth_key_preauthorized: bool = False,
        auth_key_tags: list[str] | None = None,
        user_type: Annotated[
            str | None,
            Field(
                description="For user_list: filter by Tailscale user type (e.g. member, shared)."
            ),
        ] = None,
        user_role_filter: Annotated[
            str | None,
            Field(description="For user_list: filter by role (e.g. admin)."),
        ] = None,
    ) -> dict[str, Any]:
        """LIST_GET_MANAGE_DEVICES — Tailscale devices, users, auth keys (Admin API).

        PORTMANTEAU PATTERN RATIONALE: One domain tool with an ``operation`` enum avoids dozens
        of separate tool names while keeping the MCP tool list small (fleet SOTA pattern).

        **Returns (always includes ``operation``):**
        - ``list``: ``devices``, ``count``, ``summary``, ``filters_applied``, optional ``suggestion``
        - ``get``: ``device``, ``device_id``
        - ``authorize``: ``result``, ``device_id``, ``authorized``
        - ``rename``: ``result``, ``device_id``, ``new_name``
        - ``tag``: ``result``, ``device_id``, ``tags``
        - ``delete``: ``result``, ``device_id``
        - ``search``: ``results``, ``query``, ``count``
        - ``stats``: ``statistics``
        - ``exit_node`` / ``subnet_router``: ``result``, ``device_id``, routes/subnets as applicable
        - ``user_*``: ``users`` or ``result`` (list/get only — create/update/delete not in Admin API)
        - ``auth_key_*``: ``keys`` or ``result``

        **Errors:** Missing required fields or API failures raise ``TailscaleMCPError`` with a
        concrete message. Retry transient HTTP errors; fix ACL/API key scope for 403.

        **Recovery:** On ``Unknown operation``, use only values from the ``operation`` schema enum.
        """
        try:
            if operation == "list":
                devices = await ctx.device_manager.list_devices(
                    online_only=online_only, filter_tags=filter_tags or []
                )

                # Conversational response with context
                online_count = sum(1 for d in devices if d.get("online", False))
                filter_desc = []
                if online_only:
                    filter_desc.append("online only")
                if filter_tags:
                    filter_desc.append(f"with tags: {', '.join(filter_tags)}")

                response = {
                    "operation": "list",
                    "devices": devices,
                    "count": len(devices),
                    "summary": f"Found {len(devices)} device{'s' if len(devices) != 1 else ''} "
                    f"({online_count} online, {len(devices) - online_count} offline)"
                    f"{f' filtered by {", ".join(filter_desc)}' if filter_desc else ''}",
                    "filters_applied": {
                        "online_only": online_only,
                        "filter_tags": filter_tags or [],
                    },
                }

                # Add conversational suggestions
                if len(devices) == 0:
                    response["suggestion"] = (
                        "No devices found. Try removing filters or check your Tailscale API credentials."
                    )
                elif online_count == 0:
                    response["suggestion"] = (
                        "All devices are offline. Check network connectivity."
                    )
                elif len(devices) > 10:
                    response["suggestion"] = (
                        "Large tailnet. Use filter_tags or search_query to narrow."
                    )

                return response

            elif operation == "get":
                if not device_id:
                    raise TailscaleMCPError("device_id is required for get operation")
                device = await ctx.device_manager.get_device(device_id)
                return {
                    "operation": "get",
                    "device": device,
                    "device_id": device_id,
                }

            elif operation == "authorize":
                if not device_id:
                    raise TailscaleMCPError(
                        "device_id is required for authorize operation"
                    )
                if authorize is None:
                    raise TailscaleMCPError("authorize parameter is required")
                result = await ctx.device_manager.update_device_authorization(
                    device_id, authorize, reason
                )
                return {
                    "operation": "authorize",
                    "result": result,
                    "device_id": device_id,
                    "authorized": authorize,
                }

            elif operation == "rename":
                if not device_id or not name:
                    raise TailscaleMCPError(
                        "device_id and name are required for rename operation"
                    )
                result = await ctx.device_manager.rename_device(device_id, name)
                return {
                    "operation": "rename",
                    "result": result,
                    "device_id": device_id,
                    "new_name": name,
                }

            elif operation == "tag":
                if not device_id or not tags:
                    raise TailscaleMCPError(
                        "device_id and tags are required for tag operation"
                    )
                result = await ctx.device_manager.tag_device(device_id, tags, "add")
                return {
                    "operation": "tag",
                    "result": result,
                    "device_id": device_id,
                    "tags": tags,
                }

            elif operation == "delete":
                if not device_id:
                    raise TailscaleMCPError(
                        "device_id is required for delete operation"
                    )
                await ctx.api_client.delete_device(device_id)
                return {
                    "operation": "delete",
                    "device_id": device_id,
                    "result": f"Device {device_id} deleted.",
                }

            elif operation == "search":
                if not search_query:
                    raise TailscaleMCPError(
                        "search_query is required for search operation"
                    )
                results = await ctx.device_manager.search_devices(
                    search_query, search_fields
                )
                return {
                    "operation": "search",
                    "results": results,
                    "query": search_query,
                    "count": len(results),
                }

            elif operation == "stats":
                stats = await ctx.device_manager.get_device_statistics()
                return {
                    "operation": "stats",
                    "statistics": stats,
                }

            elif operation == "exit_node":
                if not device_id:
                    raise TailscaleMCPError(
                        "device_id is required for exit_node operation"
                    )
                if enable_exit_node:
                    result = await ctx.device_manager.enable_exit_node(
                        device_id, advertise_routes or ["0.0.0.0/0"]
                    )
                    return {
                        "operation": "exit_node_enable",
                        "result": result,
                        "device_id": device_id,
                        "advertise_routes": advertise_routes,
                    }
                else:
                    result = await ctx.device_manager.disable_exit_node(device_id)
                    return {
                        "operation": "exit_node_disable",
                        "result": result,
                        "device_id": device_id,
                    }

            elif operation == "subnet_router":
                if not device_id:
                    raise TailscaleMCPError(
                        "device_id is required for subnet_router operation"
                    )
                if enable_subnet_router:
                    if not subnets:
                        raise TailscaleMCPError(
                            "subnets are required for enabling subnet router"
                        )
                    result = await ctx.device_manager.enable_subnet_router(
                        device_id, subnets
                    )
                    return {
                        "operation": "subnet_router_enable",
                        "result": result,
                        "device_id": device_id,
                        "subnets": subnets,
                    }
                else:
                    result = await ctx.device_manager.disable_subnet_router(device_id)
                    return {
                        "operation": "subnet_router_disable",
                        "result": result,
                        "device_id": device_id,
                    }

            elif operation == "user_list":
                users = await ctx.device_manager.list_users(
                    user_type=user_type, role=user_role_filter
                )
                return {
                    "operation": "user_list",
                    "users": users,
                    "count": len(users),
                    "filters": {"user_type": user_type, "role": user_role_filter},
                }

            elif operation == "user_details":
                if not user_email:
                    raise TailscaleMCPError(
                        "user_email is required for user_details (value is the user id UUID from user_list)"
                    )
                result = await ctx.device_manager.get_user_details(user_email)
                return {
                    "operation": "user_details",
                    "result": result,
                    "user_id": user_email,
                }

            elif operation == "auth_key_list":
                if ctx.key_ops is None:
                    raise TailscaleMCPError("Key operations not available")
                keys = await ctx.key_ops.list_auth_keys()
                return {
                    "operation": "auth_key_list",
                    "keys": keys,
                    "count": len(keys),
                }

            elif operation == "auth_key_create":
                if ctx.key_ops is None:
                    raise TailscaleMCPError("Key operations not available")
                capabilities: dict[str, Any] = {
                    "devices": {
                        "create": {
                            "reusable": auth_key_reusable,
                            "ephemeral": auth_key_ephemeral,
                            "preauthorized": auth_key_preauthorized,
                            "tags": auth_key_tags or [],
                        }
                    }
                }
                expires_seconds = None
                if auth_key_expiry:
                    match = re.match(r"(\d+)", auth_key_expiry)
                    if match:
                        expires_seconds = int(match.group(1))
                result = await ctx.key_ops.create_auth_key(
                    capabilities=capabilities,
                    expires_seconds=expires_seconds,
                    reusable=auth_key_reusable,
                )
                return {
                    "operation": "auth_key_create",
                    "result": result,
                }

            elif operation == "auth_key_revoke":
                if ctx.key_ops is None:
                    raise TailscaleMCPError("Key operations not available")
                if not auth_key_name:
                    raise TailscaleMCPError(
                        "auth_key_name is required for auth_key_revoke operation"
                    )
                await ctx.key_ops.revoke_auth_key(auth_key_name)
                return {
                    "operation": "auth_key_revoke",
                    "result": f"Auth key {auth_key_name} revoked.",
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_device operation", operation=operation, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to perform device operation: {e}") from e
