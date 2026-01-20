"""Tailscale Device tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_device_tool(ctx: ToolContext) -> None:
    """Register the tailscale_device tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_device(
        operation: str,
        device_id: str | None = None,
        name: str | None = None,
        tags: list[str] | None = None,
        authorize: bool | None = None,
        reason: str | None = None,
        public_key: str | None = None,
        key_name: str | None = None,
        online_only: bool = False,
        filter_tags: list[str] | None = None,
        search_query: str | None = None,
        search_fields: list[str] | None = None,
        enable_exit_node: bool = False,
        advertise_routes: list[str] | None = None,
        enable_subnet_router: bool = False,
        subnets: list[str] | None = None,
        # User management parameters
        user_email: str | None = None,
        user_role: str | None = None,
        user_permissions: list[str] | None = None,
        auth_key_name: str | None = None,
        auth_key_expiry: str | None = None,
        auth_key_reusable: bool = False,
        auth_key_ephemeral: bool = False,
        auth_key_preauthorized: bool = False,
        auth_key_tags: list[str] | None = None,
    ) -> dict[str, Any]:
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
                              f"{f' filtered by {', '.join(filter_desc)}' if filter_desc else ''}",
                    "filters_applied": {
                        "online_only": online_only,
                        "filter_tags": filter_tags or [],
                    },
                }

                # Add conversational suggestions
                if len(devices) == 0:
                    response["suggestion"] = "No devices found. Try removing filters or check your Tailscale API credentials."
                elif online_count == 0:
                    response["suggestion"] = "All devices are offline. Check network connectivity or use tailscale_status for more details."
                elif len(devices) > 10:
                    response["suggestion"] = f"That's a large tailnet! Consider using filter_tags or search_query to narrow results. Try: tailscale_device(operation='list', filter_tags=['tag:name'])"

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

            elif operation == "ssh":
                if not device_id:
                    raise TailscaleMCPError("device_id is required for SSH operation")
                if public_key:
                    result = await ctx.device_manager.enable_ssh_access(
                        device_id, public_key, key_name
                    )
                    return {
                        "operation": "ssh_enable",
                        "result": result,
                        "device_id": device_id,
                    }
                else:
                    result = await ctx.device_manager.disable_ssh_access(device_id)
                    return {
                        "operation": "ssh_disable",
                        "result": result,
                        "device_id": device_id,
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
                users = await ctx.device_manager.list_users()
                return {
                    "operation": "user_list",
                    "users": users,
                    "count": len(users),
                }

            elif operation == "user_create":
                if not user_email:
                    raise TailscaleMCPError(
                        "user_email is required for user_create operation"
                    )
                result = await ctx.device_manager.create_user(
                    user_email, user_role, user_permissions
                )
                return {
                    "operation": "user_create",
                    "result": result,
                    "user_email": user_email,
                    "user_role": user_role,
                }

            elif operation == "user_update":
                if not user_email:
                    raise TailscaleMCPError(
                        "user_email is required for user_update operation"
                    )
                result = await ctx.device_manager.update_user(
                    user_email, user_role, user_permissions
                )
                return {
                    "operation": "user_update",
                    "result": result,
                    "user_email": user_email,
                }

            elif operation == "user_delete":
                if not user_email:
                    raise TailscaleMCPError(
                        "user_email is required for user_delete operation"
                    )
                result = await ctx.device_manager.delete_user(user_email)
                return {
                    "operation": "user_delete",
                    "result": result,
                    "user_email": user_email,
                }

            elif operation == "user_details":
                if not user_email:
                    raise TailscaleMCPError(
                        "user_email is required for user_details operation"
                    )
                result = await ctx.device_manager.get_user_details(user_email)
                return {
                    "operation": "user_details",
                    "result": result,
                    "user_email": user_email,
                }

            elif operation == "auth_key_list":
                keys = await ctx.device_manager.list_auth_keys()
                return {
                    "operation": "auth_key_list",
                    "keys": keys,
                    "count": len(keys),
                }

            elif operation == "auth_key_create":
                if not auth_key_name:
                    raise TailscaleMCPError(
                        "auth_key_name is required for auth_key_create operation"
                    )
                result = await ctx.device_manager.create_auth_key(
                    auth_key_name,
                    auth_key_expiry,
                    auth_key_reusable,
                    auth_key_ephemeral,
                    auth_key_preauthorized,
                    auth_key_tags,
                )
                return {
                    "operation": "auth_key_create",
                    "result": result,
                    "auth_key_name": auth_key_name,
                }

            elif operation == "auth_key_revoke":
                if not auth_key_name:
                    raise TailscaleMCPError(
                        "auth_key_name is required for auth_key_revoke operation"
                    )
                result = await ctx.device_manager.revoke_auth_key(auth_key_name)
                return {
                    "operation": "auth_key_revoke",
                    "result": result,
                    "auth_key_name": auth_key_name,
                }

            elif operation == "auth_key_rotate":
                result = await ctx.device_manager.rotate_auth_keys()
                return {
                    "operation": "auth_key_rotate",
                    "result": result,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_device operation", operation=operation, error=str(e)
            )
            raise TailscaleMCPError(f"Failed to perform device operation: {e}") from e
