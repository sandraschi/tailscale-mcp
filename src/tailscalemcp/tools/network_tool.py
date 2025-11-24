"""Tailscale Network tool module."""

from typing import Any

import structlog

from tailscalemcp.exceptions import TailscaleMCPError

from ._base import ToolContext

logger = structlog.get_logger(__name__)


def register_network_tool(ctx: ToolContext) -> None:
    """Register the tailscale_network tool.

    Args:
        ctx: Tool context with all managers and MCP instance
    """

    @ctx.mcp.tool()
    async def tailscale_network(
        operation: str,
        enabled: bool | None = None,
        override_local_dns: bool = False,
        name: str | None = None,
        record_type: str | None = None,
        value: str | None = None,
        ttl: int = 3600,
        hostname: str | None = None,
        use_cache: bool = True,
        domain: str | None = None,
        policy_name: str | None = None,
        rules: list[dict[str, Any]] | None = None,
        priority: int = 100,
        policy_id: str | None = None,  # noqa: ARG001
        # Services (TailVIPs)
        service_id: str | None = None,
        service_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            if operation == "dns_config":
                # Use NetworkOperations for real API calls
                config = await ctx.network_ops.get_dns_config()
                return {
                    "operation": "dns_config",
                    "configuration": config,
                }

            elif operation == "magic_dns":
                if enabled is None:
                    raise TailscaleMCPError(
                        "enabled parameter is required for magic_dns operation"
                    )
                result = await ctx.magic_dns_manager.configure_magic_dns(
                    enabled, override_local_dns
                )
                return {
                    "operation": "magic_dns",
                    "result": result,
                    "enabled": enabled,
                    "override_local_dns": override_local_dns,
                }

            elif operation == "dns_record":
                if not name or not record_type or not value:
                    raise TailscaleMCPError(
                        "name, record_type, and value are required for dns_record operation"
                    )
                result = await ctx.magic_dns_manager.add_dns_record(
                    name, record_type, value, ttl
                )
                return {
                    "operation": "dns_record_add",
                    "result": result,
                    "name": name,
                    "record_type": record_type,
                    "value": value,
                    "ttl": ttl,
                }

            elif operation == "resolve":
                if not hostname:
                    raise TailscaleMCPError(
                        "hostname is required for resolve operation"
                    )
                result = await ctx.magic_dns_manager.resolve_dns(
                    hostname, record_type or "A", use_cache
                )
                return {
                    "operation": "resolve",
                    "result": result,
                    "hostname": hostname,
                    "record_type": record_type or "A",
                }

            elif operation == "search_domain":
                if not domain:
                    raise TailscaleMCPError(
                        "domain is required for search_domain operation"
                    )
                if enabled:
                    result = await ctx.magic_dns_manager.add_search_domain(domain)
                    return {
                        "operation": "search_domain_add",
                        "result": result,
                        "domain": domain,
                    }
                else:
                    result = await ctx.magic_dns_manager.remove_search_domain(domain)
                    return {
                        "operation": "search_domain_remove",
                        "result": result,
                        "domain": domain,
                    }

            elif operation == "policy":
                if not policy_name or not rules:
                    raise TailscaleMCPError(
                        "policy_name and rules are required for policy operation"
                    )
                # Use NetworkOperations for DNS-related policies, PolicyOperations for ACL policies
                # For now, use NetworkOperations which has ACL policy methods
                # Note: This may need to be split into separate operations
                policy_dict = {
                    "Hosts": {},
                    "Users": {},
                    "Tags": {},
                    "ACLs": rules if isinstance(rules, list) else [],
                    "Groups": {},
                }
                result = await ctx.network_ops.update_acl_policy(policy_dict)
                return {
                    "operation": "policy_create",
                    "result": result,
                    "policy_name": policy_name,
                    "rules": rules,
                    "priority": priority,
                }

            elif operation == "stats":
                stats = await ctx.magic_dns_manager.get_dns_statistics()
                return {
                    "operation": "stats",
                    "statistics": stats,
                }

            elif operation == "cache":
                result = await ctx.magic_dns_manager.clear_dns_cache()
                return {
                    "operation": "cache_clear",
                    "result": result,
                }

            elif operation == "services_list":
                services = await ctx.service_ops.list_services()
                return {
                    "operation": "services_list",
                    "count": len(services),
                    "services": [s.to_dict() for s in services],
                }

            elif operation == "services_get":
                if not service_id:
                    raise TailscaleMCPError(
                        "service_id is required for services_get operation"
                    )
                service = await ctx.service_ops.get_service(service_id)
                return {
                    "operation": "services_get",
                    "service_id": service_id,
                    "service": service.to_dict(),
                }

            elif operation == "services_create":
                if not service_payload:
                    raise TailscaleMCPError(
                        "service_payload is required for services_create operation"
                    )
                service = await ctx.service_ops.create_service(service_payload)
                return {
                    "operation": "services_create",
                    "service": service.to_dict(),
                }

            elif operation == "services_update":
                if not service_id or not service_payload:
                    raise TailscaleMCPError(
                        "service_id and service_payload are required for services_update operation"
                    )
                service = await ctx.service_ops.update_service(
                    service_id, service_payload
                )
                return {
                    "operation": "services_update",
                    "service_id": service_id,
                    "service": service.to_dict(),
                }

            elif operation == "services_delete":
                if not service_id:
                    raise TailscaleMCPError(
                        "service_id is required for services_delete operation"
                    )
                await ctx.service_ops.delete_service(service_id)
                return {
                    "operation": "services_delete",
                    "service_id": service_id,
                    "deleted": True,
                }

            else:
                raise TailscaleMCPError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(
                "Error in tailscale_network operation",
                operation=operation,
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to perform network operation: {e}") from e
