"""New Tailscale Admin API features: invites, posture, device keys, logging, webhooks, settings, contacts."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext
from ._tool_types import (
    ContactOperation,
    DeviceInviteOperation,
    DeviceKeyOperation,
    LoggingOperation,
    PostureAttributeOperation,
    TailnetSettingsOperation,
    UserInviteOperation,
    WebhookOperation,
)
from .mcp_tool_names import (
    MANAGE_DEVICE_KEYS,
    MANAGE_POSTURE_ATTRIBUTES,
    MANAGE_TAILNET_CONTACTS,
    MANAGE_TAILNET_INVITES,
    MANAGE_TAILNET_LOGGING,
    MANAGE_TAILNET_SETTINGS,
    MANAGE_TAILNET_WEBHOOKS,
)

logger = structlog.get_logger(__name__)


def register_new_api_tools(ctx: ToolContext) -> None:
    """Register all new Tailscale API domain tools."""

    @ctx.mcp.tool(name=MANAGE_TAILNET_INVITES)
    async def tailnet_invites(
        operation: DeviceInviteOperation | UserInviteOperation,
        invite_type: str = "device",
        device_id: str | None = None,
        invite_id: str | None = None,
        invite_url: str | None = None,
        multi_use: bool | None = None,
        allow_exit_node: bool | None = None,
        email: str | None = None,
        role: str | None = None,
    ) -> dict[str, Any]:
        """MANAGE_TAILNET_INVITES — Device and user invite operations.

        Operations (invite_type='device'): list, create, get, delete, resend, accept
        Operations (invite_type='user'): list, create, get, delete, resend

        Invite management for sharing devices and inviting users to the tailnet.
        """
        try:
            if invite_type == "device":
                op = DeviceInviteOperation(operation)  # type: ignore[valid-type]
                if op == "list":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for list")
                    invites = await ctx.api_client.list_device_invites(device_id)
                    return {"operation": "list", "invite_type": "device", "invites": invites, "count": len(invites)}
                elif op == "create":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for create")
                    payload: list[dict[str, Any]] = [{}]
                    if multi_use is not None:
                        payload[0]["multiUse"] = multi_use
                    if allow_exit_node is not None:
                        payload[0]["allowExitNode"] = allow_exit_node
                    if email:
                        payload[0]["email"] = email
                    invites = await ctx.api_client.create_device_invites(device_id, payload)
                    return {"operation": "create", "invite_type": "device", "invites": invites}
                elif op == "get":
                    if not invite_id:
                        raise TailscaleMCPError("invite_id is required for get")
                    invite = await ctx.api_client.get_device_invite(invite_id)
                    return {"operation": "get", "invite_type": "device", "invite": invite}
                elif op == "delete":
                    if not invite_id:
                        raise TailscaleMCPError("invite_id is required for delete")
                    await ctx.api_client.delete_device_invite(invite_id)
                    return {"operation": "delete", "invite_type": "device", "success": True}
                elif op == "resend":
                    if not invite_id:
                        raise TailscaleMCPError("invite_id is required for resend")
                    await ctx.api_client.resend_device_invite(invite_id)
                    return {"operation": "resend", "invite_type": "device", "success": True}
                elif op == "accept":
                    if not invite_url:
                        raise TailscaleMCPError("invite_url is required for accept")
                    result = await ctx.api_client.accept_device_invite(invite_url)
                    return {"operation": "accept", "invite_type": "device", "result": result}
            else:
                op = UserInviteOperation(operation)  # type: ignore[valid-type]
                if op == "list":
                    invites = await ctx.api_client.list_user_invites()
                    return {"operation": "list", "invite_type": "user", "invites": invites, "count": len(invites)}
                elif op == "create":
                    payload = [{"role": role or "member"}]
                    if email:
                        payload[0]["email"] = email
                    invites = await ctx.api_client.create_user_invites(payload)
                    return {"operation": "create", "invite_type": "user", "invites": invites}
                elif op == "get":
                    if not invite_id:
                        raise TailscaleMCPError("invite_id is required for get")
                    invite = await ctx.api_client.get_user_invite(invite_id)
                    return {"operation": "get", "invite_type": "user", "invite": invite}
                elif op == "delete":
                    if not invite_id:
                        raise TailscaleMCPError("invite_id is required for delete")
                    await ctx.api_client.delete_user_invite(invite_id)
                    return {"operation": "delete", "invite_type": "user", "success": True}
                elif op == "resend":
                    if not invite_id:
                        raise TailscaleMCPError("invite_id is required for resend")
                    await ctx.api_client.resend_user_invite(invite_id)
                    return {"operation": "resend", "invite_type": "user", "success": True}
                raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_invites", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Invite operation failed: {e}") from e

    @ctx.mcp.tool(name=MANAGE_POSTURE_ATTRIBUTES)
    async def tailnet_posture_attributes(
        operation: PostureAttributeOperation,
        device_id: str | None = None,
        attribute_key: str | None = None,
        value: Any = None,
        expiry: str | None = None,
        comment: str | None = None,
        nodes: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MANAGE_POSTURE_ATTRIBUTES — Device posture attribute operations.

        Operations: get, set, delete, batch_update

        Manage custom posture attributes on devices for device posture policies.
        """
        try:
            if operation == "get":
                if not device_id:
                    raise TailscaleMCPError("device_id is required for get")
                attrs = await ctx.api_client.get_device_posture_attributes(device_id)
                return {"operation": "get", "device_id": device_id, "attributes": attrs}
            elif operation == "set":
                if not device_id or not attribute_key:
                    raise TailscaleMCPError("device_id and attribute_key are required for set")
                result = await ctx.api_client.set_custom_device_posture_attribute(device_id, attribute_key, value, expiry, comment)
                return {"operation": "set", "device_id": device_id, "attribute_key": attribute_key, "result": result}
            elif operation == "delete":
                if not device_id or not attribute_key:
                    raise TailscaleMCPError("device_id and attribute_key are required for delete")
                await ctx.api_client.delete_custom_device_posture_attribute(device_id, attribute_key)
                return {"operation": "delete", "device_id": device_id, "attribute_key": attribute_key, "success": True}
            elif operation == "batch_update":
                if not nodes:
                    raise TailscaleMCPError("nodes is required for batch_update")
                await ctx.api_client.batch_update_device_posture_attributes(nodes, comment)
                return {"operation": "batch_update", "success": True}
            raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_posture_attributes", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Posture attribute operation failed: {e}") from e

    @ctx.mcp.tool(name=MANAGE_DEVICE_KEYS)
    async def tailnet_device_keys(
        operation: DeviceKeyOperation,
        device_id: str | None = None,
        key_expiry_disabled: bool | None = None,
        ipv4: str | None = None,
    ) -> dict[str, Any]:
        """MANAGE_DEVICE_KEYS — Device key and IP management operations.

        Operations: expire, update_key_expiry, set_ip

        Expire node keys (forces re-auth), toggle key expiry, set device IPv4.
        """
        try:
            if operation == "expire":
                if not device_id:
                    raise TailscaleMCPError("device_id is required for expire")
                await ctx.api_client.expire_device_key(device_id)
                return {"operation": "expire", "device_id": device_id, "success": True}
            elif operation == "update_key_expiry":
                if not device_id or key_expiry_disabled is None:
                    raise TailscaleMCPError("device_id and key_expiry_disabled are required")
                await ctx.api_client.update_device_key(device_id, key_expiry_disabled)
                return {
                    "operation": "update_key_expiry", "device_id": device_id,
                    "key_expiry_disabled": key_expiry_disabled, "success": True,
                }
            elif operation == "set_ip":
                if not device_id or not ipv4:
                    raise TailscaleMCPError("device_id and ipv4 are required for set_ip")
                await ctx.api_client.set_device_ip(device_id, ipv4)
                return {"operation": "set_ip", "device_id": device_id, "ipv4": ipv4, "success": True}
            raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_device_keys", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Device key operation failed: {e}") from e

    @ctx.mcp.tool(name=MANAGE_TAILNET_LOGGING)
    async def tailnet_logging(
        operation: LoggingOperation,
        log_type: str | None = None,
        start: str | None = None,
        end: str | None = None,
        actor: str | None = None,
        target: str | None = None,
        event: str | None = None,
        stream_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MANAGE_TAILNET_LOGGING — Audit logs, flow logs, log streaming.

        Operations: configuration_audit_logs, network_flow_logs, stream_status, stream_config_get, stream_config_set

        Access configuration audit logs, network flow logs, and configure log streaming.
        """
        try:
            if operation == "configuration_audit_logs":
                logs = await ctx.api_client.list_configuration_audit_logs(
                    start=start, end=end, actor=actor, target=target, event=event
                )
                return {"operation": "configuration_audit_logs", "logs": logs, "count": len(logs)}
            elif operation == "network_flow_logs":
                logs = await ctx.api_client.list_network_flow_logs(start=start, end=end)
                return {"operation": "network_flow_logs", "logs": logs, "count": len(logs)}
            elif operation == "stream_status":
                if not log_type:
                    raise TailscaleMCPError("log_type is required (e.g. 'configuration', 'network')")
                status = await ctx.api_client.get_log_streaming_status(log_type)
                return {"operation": "stream_status", "log_type": log_type, "status": status}
            elif operation == "stream_config_get":
                if not log_type:
                    raise TailscaleMCPError("log_type is required")
                config = await ctx.api_client.get_log_streaming_configuration(log_type)
                return {"operation": "stream_config_get", "log_type": log_type, "config": config}
            elif operation == "stream_config_set":
                if not log_type or not stream_config:
                    raise TailscaleMCPError("log_type and stream_config are required")
                result = await ctx.api_client.set_log_streaming_configuration(log_type, stream_config)
                return {"operation": "stream_config_set", "log_type": log_type, "result": result}
            raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_logging", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Logging operation failed: {e}") from e

    @ctx.mcp.tool(name=MANAGE_TAILNET_WEBHOOKS)
    async def tailnet_webhooks(
        operation: WebhookOperation,
        webhook_id: str | None = None,
        endpoint_url: str | None = None,
        provider_type: str | None = None,
        secret: str | None = None,
        subscriptions: list[str] | None = None,
        updates: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MANAGE_TAILNET_WEBHOOKS — Native Tailscale webhook management.

        Operations: list, create, get, update, delete, rotate_secret

        Manage webhook endpoints that receive Tailscale events.
        """
        try:
            if operation == "list":
                hooks = await ctx.api_client.list_webhooks()
                return {"operation": "list", "webhooks": hooks, "count": len(hooks)}
            elif operation == "create":
                if not endpoint_url or not provider_type:
                    raise TailscaleMCPError("endpoint_url and provider_type are required")
                hook = await ctx.api_client.create_webhook(endpoint_url, provider_type, secret=secret, subscriptions=subscriptions)
                return {"operation": "create", "webhook": hook}
            elif operation == "get":
                if not webhook_id:
                    raise TailscaleMCPError("webhook_id is required")
                hook = await ctx.api_client.get_webhook(webhook_id)
                return {"operation": "get", "webhook": hook}
            elif operation == "update":
                if not webhook_id or not updates:
                    raise TailscaleMCPError("webhook_id and updates are required")
                hook = await ctx.api_client.update_webhook(webhook_id, updates)
                return {"operation": "update", "webhook": hook}
            elif operation == "delete":
                if not webhook_id:
                    raise TailscaleMCPError("webhook_id is required")
                await ctx.api_client.delete_webhook(webhook_id)
                return {"operation": "delete", "success": True}
            elif operation == "rotate_secret":
                if not webhook_id:
                    raise TailscaleMCPError("webhook_id is required")
                result = await ctx.api_client.rotate_webhook_secret(webhook_id)
                return {"operation": "rotate_secret", "result": result}
            raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_webhooks", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Webhook operation failed: {e}") from e

    @ctx.mcp.tool(name=MANAGE_TAILNET_SETTINGS)
    async def tailnet_settings(
        operation: TailnetSettingsOperation,
        settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MANAGE_TAILNET_SETTINGS — General tailnet settings management.

        Operations: get, update

        View and modify tailnet-wide settings.
        """
        try:
            if operation == "get":
                s = await ctx.api_client.get_tailnet_settings()
                return {"operation": "get", "settings": s}
            elif operation == "update":
                if not settings:
                    raise TailscaleMCPError("settings payload is required for update")
                result = await ctx.api_client.update_tailnet_settings(settings)
                return {"operation": "update", "result": result}
            raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_settings", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Settings operation failed: {e}") from e

    @ctx.mcp.tool(name=MANAGE_TAILNET_CONTACTS)
    async def tailnet_contacts(
        operation: ContactOperation,
        contacts: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MANAGE_TAILNET_CONTACTS — Contact preference management.

        Operations: get, update

        Manage contact preferences for tailnet notifications.
        """
        try:
            if operation == "get":
                prefs = await ctx.api_client.get_contact_preferences()
                return {"operation": "get", "contacts": prefs}
            elif operation == "update":
                if not contacts:
                    raise TailscaleMCPError("contacts payload is required for update")
                result = await ctx.api_client.update_contact_preferences(contacts)
                return {"operation": "update", "result": result}
            raise TailscaleMCPError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error("Error in tailnet_contacts", operation=operation, error=str(e))
            raise TailscaleMCPError(f"Contact operation failed: {e}") from e

    logger.info("New API tools registered (invites, posture, device keys, logging, webhooks, settings, contacts)")

