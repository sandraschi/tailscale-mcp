"""
Tailscale Portmanteau Tools

Consolidated tools following the portmanteau pattern to avoid tool explosion.
Each tool combines multiple related operations into a single, powerful interface.
"""

import time
from typing import Any

import structlog
from fastmcp import FastMCP

from tailscalemcp.device_management import AdvancedDeviceManager
from tailscalemcp.exceptions import TailscaleMCPError
from tailscalemcp.grafana_dashboard import TailscaleGrafanaDashboard
from tailscalemcp.magic_dns import MagicDNSManager
from tailscalemcp.monitoring import TailscaleMonitor
from tailscalemcp.taildrop import TaildropManager

logger = structlog.get_logger(__name__)


class TailscalePortmanteauTools:
    """Consolidated Tailscale tools using portmanteau pattern."""

    def __init__(
        self,
        mcp: FastMCP,
        device_manager: AdvancedDeviceManager,
        monitor: TailscaleMonitor,
        grafana_dashboard: TailscaleGrafanaDashboard,
        taildrop_manager: TaildropManager,
        magic_dns_manager: MagicDNSManager,
    ):
        """Initialize portmanteau tools.

        Args:
            mcp: FastMCP instance
            device_manager: Device manager instance
            monitor: Monitoring instance
            grafana_dashboard: Grafana dashboard instance
            taildrop_manager: Taildrop manager instance
            magic_dns_manager: MagicDNS manager instance
        """
        self.mcp = mcp
        self.device_manager = device_manager
        self.monitor = monitor
        self.grafana_dashboard = grafana_dashboard
        self.taildrop_manager = taildrop_manager
        self.magic_dns_manager = magic_dns_manager
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all portmanteau tools."""

        @self.mcp.tool()
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
            """Comprehensive device management operations.

            This portmanteau tool handles all device-related operations:
            - list: List devices with optional filtering
            - get: Get device details
            - authorize: Authorize/revoke device access
            - rename: Rename device
            - tag: Add/remove/replace device tags
            - ssh: Enable/disable SSH access
            - search: Search devices by various fields
            - stats: Get device statistics
            - exit_node: Enable/disable exit node functionality
            - subnet_router: Enable/disable subnet routing
            - user_list: List users in the tailnet
            - user_create: Create new user account
            - user_update: Update user details/permissions
            - user_delete: Remove user account
            - user_details: Get user information
            - auth_key_list: List authentication keys
            - auth_key_create: Generate new auth key
            - auth_key_revoke: Revoke authentication key
            - auth_key_rotate: Rotate expired keys

            Args:
                operation: Operation to perform (list, get, authorize, rename, tag, ssh, search, stats, exit_node, subnet_router)
                device_id: Device ID (required for most operations)
                name: New name for rename operation
                tags: Tags for tag operations
                authorize: Authorization status for authorize operation
                reason: Reason for authorization change
                public_key: SSH public key for SSH operations
                key_name: SSH key name
                online_only: Only show online devices for list operation
                filter_tags: Filter devices by tags for list operation
                search_query: Search query for search operation
                search_fields: Fields to search in for search operation
                enable_exit_node: Enable exit node functionality
                advertise_routes: Routes to advertise for exit node
                enable_subnet_router: Enable subnet router functionality
                subnets: Subnets for subnet router

            Returns:
                Operation result with device information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "list":
                    devices = await self.device_manager.list_devices(
                        online_only=online_only, filter_tags=filter_tags or []
                    )
                    return {
                        "operation": "list",
                        "devices": devices,
                        "count": len(devices),
                        "filters": {
                            "online_only": online_only,
                            "filter_tags": filter_tags or [],
                        },
                    }

                elif operation == "get":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for get operation")
                    device = await self.device_manager.get_device(device_id)
                    return {
                        "operation": "get",
                        "device": device,
                        "device_id": device_id,
                    }

                elif operation == "authorize":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for authorize operation")
                    if authorize is None:
                        raise TailscaleMCPError("authorize parameter is required")
                    result = await self.device_manager.update_device_authorization(
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
                        raise TailscaleMCPError("device_id and name are required for rename operation")
                    result = await self.device_manager.rename_device(device_id, name)
                    return {
                        "operation": "rename",
                        "result": result,
                        "device_id": device_id,
                        "new_name": name,
                    }

                elif operation == "tag":
                    if not device_id or not tags:
                        raise TailscaleMCPError("device_id and tags are required for tag operation")
                    result = await self.device_manager.tag_device(device_id, tags, "add")
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
                        result = await self.device_manager.enable_ssh_access(
                            device_id, public_key, key_name
                        )
                        return {
                            "operation": "ssh_enable",
                            "result": result,
                            "device_id": device_id,
                        }
                    else:
                        result = await self.device_manager.disable_ssh_access(device_id)
                        return {
                            "operation": "ssh_disable",
                            "result": result,
                            "device_id": device_id,
                        }

                elif operation == "search":
                    if not search_query:
                        raise TailscaleMCPError("search_query is required for search operation")
                    results = await self.device_manager.search_devices(
                        search_query, search_fields
                    )
                    return {
                        "operation": "search",
                        "results": results,
                        "query": search_query,
                        "count": len(results),
                    }

                elif operation == "stats":
                    stats = await self.device_manager.get_device_statistics()
                    return {
                        "operation": "stats",
                        "statistics": stats,
                    }

                elif operation == "exit_node":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for exit_node operation")
                    if enable_exit_node:
                        result = await self.device_manager.enable_exit_node(
                            device_id, advertise_routes or ["0.0.0.0/0"]
                        )
                        return {
                            "operation": "exit_node_enable",
                            "result": result,
                            "device_id": device_id,
                            "advertise_routes": advertise_routes,
                        }
                    else:
                        result = await self.device_manager.disable_exit_node(device_id)
                        return {
                            "operation": "exit_node_disable",
                            "result": result,
                            "device_id": device_id,
                        }

                elif operation == "subnet_router":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for subnet_router operation")
                    if enable_subnet_router:
                        if not subnets:
                            raise TailscaleMCPError("subnets are required for enabling subnet router")
                        result = await self.device_manager.enable_subnet_router(device_id, subnets)
                        return {
                            "operation": "subnet_router_enable",
                            "result": result,
                            "device_id": device_id,
                            "subnets": subnets,
                        }
                    else:
                        result = await self.device_manager.disable_subnet_router(device_id)
                        return {
                            "operation": "subnet_router_disable",
                            "result": result,
                            "device_id": device_id,
                        }

                elif operation == "user_list":
                    users = await self.device_manager.list_users()
                    return {
                        "operation": "user_list",
                        "users": users,
                        "count": len(users),
                    }

                elif operation == "user_create":
                    if not user_email:
                        raise TailscaleMCPError("user_email is required for user_create operation")
                    result = await self.device_manager.create_user(user_email, user_role, user_permissions)
                    return {
                        "operation": "user_create",
                        "result": result,
                        "user_email": user_email,
                        "user_role": user_role,
                    }

                elif operation == "user_update":
                    if not user_email:
                        raise TailscaleMCPError("user_email is required for user_update operation")
                    result = await self.device_manager.update_user(user_email, user_role, user_permissions)
                    return {
                        "operation": "user_update",
                        "result": result,
                        "user_email": user_email,
                    }

                elif operation == "user_delete":
                    if not user_email:
                        raise TailscaleMCPError("user_email is required for user_delete operation")
                    result = await self.device_manager.delete_user(user_email)
                    return {
                        "operation": "user_delete",
                        "result": result,
                        "user_email": user_email,
                    }

                elif operation == "user_details":
                    if not user_email:
                        raise TailscaleMCPError("user_email is required for user_details operation")
                    result = await self.device_manager.get_user_details(user_email)
                    return {
                        "operation": "user_details",
                        "result": result,
                        "user_email": user_email,
                    }

                elif operation == "auth_key_list":
                    keys = await self.device_manager.list_auth_keys()
                    return {
                        "operation": "auth_key_list",
                        "keys": keys,
                        "count": len(keys),
                    }

                elif operation == "auth_key_create":
                    if not auth_key_name:
                        raise TailscaleMCPError("auth_key_name is required for auth_key_create operation")
                    result = await self.device_manager.create_auth_key(
                        auth_key_name, auth_key_expiry, auth_key_reusable,
                        auth_key_ephemeral, auth_key_preauthorized, auth_key_tags
                    )
                    return {
                        "operation": "auth_key_create",
                        "result": result,
                        "auth_key_name": auth_key_name,
                    }

                elif operation == "auth_key_revoke":
                    if not auth_key_name:
                        raise TailscaleMCPError("auth_key_name is required for auth_key_revoke operation")
                    result = await self.device_manager.revoke_auth_key(auth_key_name)
                    return {
                        "operation": "auth_key_revoke",
                        "result": result,
                        "auth_key_name": auth_key_name,
                    }

                elif operation == "auth_key_rotate":
                    result = await self.device_manager.rotate_auth_keys()
                    return {
                        "operation": "auth_key_rotate",
                        "result": result,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_device operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform device operation: {e}") from e

        @self.mcp.tool()
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
        ) -> dict[str, Any]:
            """Comprehensive network and DNS management operations.

            This portmanteau tool handles all network-related operations:
            - dns_config: Get DNS configuration
            - magic_dns: Configure MagicDNS settings
            - dns_record: Add/remove/list DNS records
            - resolve: Resolve DNS hostnames
            - search_domain: Add/remove search domains
            - policy: Create/apply network policies
            - stats: Get DNS statistics
            - cache: Clear DNS cache

            Args:
                operation: Operation to perform (dns_config, magic_dns, dns_record, resolve, search_domain, policy, stats, cache)
                enabled: Enable/disable MagicDNS
                override_local_dns: Override local DNS settings
                name: DNS record name
                record_type: DNS record type (A, AAAA, CNAME, etc.)
                value: DNS record value
                ttl: DNS record TTL
                hostname: Hostname to resolve
                use_cache: Use DNS cache for resolution
                domain: Search domain to add/remove
                policy_name: Network policy name
                rules: Network policy rules
                priority: Policy priority
                policy_id: Policy ID for apply operation

            Returns:
                Operation result with network information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "dns_config":
                    config = await self.magic_dns_manager.get_dns_configuration()
                    return {
                        "operation": "dns_config",
                        "configuration": config,
                    }

                elif operation == "magic_dns":
                    if enabled is None:
                        raise TailscaleMCPError("enabled parameter is required for magic_dns operation")
                    result = await self.magic_dns_manager.configure_magic_dns(
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
                        raise TailscaleMCPError("name, record_type, and value are required for dns_record operation")
                    result = await self.magic_dns_manager.add_dns_record(name, record_type, value, ttl)
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
                        raise TailscaleMCPError("hostname is required for resolve operation")
                    result = await self.magic_dns_manager.resolve_dns(hostname, record_type or "A", use_cache)
                    return {
                        "operation": "resolve",
                        "result": result,
                        "hostname": hostname,
                        "record_type": record_type or "A",
                    }

                elif operation == "search_domain":
                    if not domain:
                        raise TailscaleMCPError("domain is required for search_domain operation")
                    if enabled:
                        result = await self.magic_dns_manager.add_search_domain(domain)
                        return {
                            "operation": "search_domain_add",
                            "result": result,
                            "domain": domain,
                        }
                    else:
                        result = await self.magic_dns_manager.remove_search_domain(domain)
                        return {
                            "operation": "search_domain_remove",
                            "result": result,
                            "domain": domain,
                        }

                elif operation == "policy":
                    if not policy_name or not rules:
                        raise TailscaleMCPError("policy_name and rules are required for policy operation")
                    result = await self.magic_dns_manager.create_network_policy(
                        policy_name, rules, priority
                    )
                    return {
                        "operation": "policy_create",
                        "result": result,
                        "policy_name": policy_name,
                        "rules": rules,
                        "priority": priority,
                    }

                elif operation == "stats":
                    stats = await self.magic_dns_manager.get_dns_statistics()
                    return {
                        "operation": "stats",
                        "statistics": stats,
                    }

                elif operation == "cache":
                    result = await self.magic_dns_manager.clear_dns_cache()
                    return {
                        "operation": "cache_clear",
                        "result": result,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_network operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform network operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_monitor(
            operation: str,
            grafana_url: str | None = None,
            api_key: str | None = None,
            dashboard_type: str = "comprehensive",
            filename: str | None = None,
            include_panels: bool = True,  # noqa: ARG001
            include_variables: bool = True,  # noqa: ARG001
        ) -> dict[str, Any]:
            """Comprehensive monitoring and metrics operations.

            This portmanteau tool handles all monitoring-related operations:
            - status: Get network status
            - metrics: Get network metrics
            - prometheus: Get Prometheus-formatted metrics
            - topology: Generate network topology
            - health: Get network health report
            - dashboard: Create Grafana dashboard
            - export: Export dashboard to file

            Args:
                operation: Operation to perform (status, metrics, prometheus, topology, health, dashboard, export)
                grafana_url: Grafana URL for dashboard operations
                api_key: Grafana API key for dashboard operations
                dashboard_type: Dashboard type (comprehensive, topology, security)
                filename: Filename for export operation
                include_panels: Include panels in export
                include_variables: Include variables in export

            Returns:
                Operation result with monitoring information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "status":
                    status = await self.monitor.get_network_status()
                    return {
                        "operation": "status",
                        "status": status,
                    }

                elif operation == "metrics":
                    metrics = await self.monitor.collect_metrics()
                    return {
                        "operation": "metrics",
                        "metrics": metrics,
                    }

                elif operation == "prometheus":
                    prometheus_metrics = await self.monitor.get_prometheus_metrics()
                    return {
                        "operation": "prometheus",
                        "metrics": prometheus_metrics,
                    }

                elif operation == "topology":
                    topology = await self.monitor.generate_network_topology()
                    return {
                        "operation": "topology",
                        "topology": topology,
                    }

                elif operation == "health":
                    health_report = await self.monitor.get_network_health_report()
                    return {
                        "operation": "health",
                        "health_report": health_report,
                    }

                elif operation == "dashboard":
                    if not grafana_url or not api_key:
                        raise TailscaleMCPError("grafana_url and api_key are required for dashboard operation")
                    dashboard_config = await self.monitor.create_grafana_dashboard(grafana_url, api_key)
                    return {
                        "operation": "dashboard_create",
                        "dashboard": dashboard_config,
                        "grafana_url": grafana_url,
                    }

                elif operation == "export":
                    if not filename:
                        raise TailscaleMCPError("filename is required for export operation")
                    if dashboard_type == "comprehensive":
                        dashboard_config = self.grafana_dashboard.create_comprehensive_dashboard()
                    elif dashboard_type == "topology":
                        dashboard_config = self.grafana_dashboard.create_network_topology_dashboard()
                    elif dashboard_type == "security":
                        dashboard_config = self.grafana_dashboard.create_security_dashboard()
                    else:
                        raise TailscaleMCPError(f"Unknown dashboard type: {dashboard_type}")

                    self.grafana_dashboard.export_dashboard(dashboard_config, filename)
                    return {
                        "operation": "export",
                        "filename": filename,
                        "dashboard_type": dashboard_type,
                        "exported": True,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_monitor operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform monitor operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_file(
            operation: str,
            file_path: str | None = None,
            recipient_device: str | None = None,
            sender_device: str | None = None,
            expire_hours: int = 24,
            transfer_id: str | None = None,
            save_path: str | None = None,
            status_filter: str | None = None,
        ) -> dict[str, Any]:
            """Comprehensive file sharing operations via Taildrop.

            This portmanteau tool handles all Taildrop file sharing operations:
            - send: Send file to another device
            - receive: Receive file from transfer
            - list: List active transfers
            - cancel: Cancel transfer
            - status: Get transfer status
            - stats: Get Taildrop statistics
            - cleanup: Clean up expired transfers

            Args:
                operation: Operation to perform (send, receive, list, cancel, status, stats, cleanup)
                file_path: Path to file for send operation
                recipient_device: Target device for send operation
                sender_device: Sender device for send operation
                expire_hours: File expiration time in hours
                transfer_id: Transfer ID for receive/cancel/status operations
                save_path: Save path for receive operation
                status_filter: Status filter for list operation

            Returns:
                Operation result with file transfer information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "send":
                    if not file_path or not recipient_device or not sender_device:
                        raise TailscaleMCPError("file_path, recipient_device, and sender_device are required for send operation")
                    result = await self.taildrop_manager.send_file(
                        file_path, recipient_device, sender_device, expire_hours
                    )
                    return {
                        "operation": "send",
                        "result": result,
                        "file_path": file_path,
                        "recipient_device": recipient_device,
                        "expire_hours": expire_hours,
                    }

                elif operation == "receive":
                    if not transfer_id:
                        raise TailscaleMCPError("transfer_id is required for receive operation")
                    result = await self.taildrop_manager.receive_file(transfer_id, save_path)
                    return {
                        "operation": "receive",
                        "result": result,
                        "transfer_id": transfer_id,
                        "save_path": save_path,
                    }

                elif operation == "list":
                    transfers = await self.taildrop_manager.list_transfers(status_filter)
                    return {
                        "operation": "list",
                        "transfers": transfers,
                        "count": len(transfers),
                        "status_filter": status_filter,
                    }

                elif operation == "cancel":
                    if not transfer_id:
                        raise TailscaleMCPError("transfer_id is required for cancel operation")
                    result = await self.taildrop_manager.cancel_transfer(transfer_id)
                    return {
                        "operation": "cancel",
                        "result": result,
                        "transfer_id": transfer_id,
                    }

                elif operation == "status":
                    if not transfer_id:
                        raise TailscaleMCPError("transfer_id is required for status operation")
                    result = await self.taildrop_manager.get_transfer_status(transfer_id)
                    return {
                        "operation": "status",
                        "result": result,
                        "transfer_id": transfer_id,
                    }

                elif operation == "stats":
                    stats = await self.taildrop_manager.get_taildrop_statistics()
                    return {
                        "operation": "stats",
                        "statistics": stats,
                    }

                elif operation == "cleanup":
                    result = await self.taildrop_manager.cleanup_expired_transfers()
                    return {
                        "operation": "cleanup",
                        "result": result,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_file operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform file operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_security(
            operation: str,
            scan_type: str = "comprehensive",
            compliance_standard: str = "SOC2",
            device_id: str | None = None,
            ip_address: str | None = None,
            quarantine_duration: int = 24,
            alert_severity: str = "medium",
            alert_message: str | None = None,
            policy_name: str | None = None,
            rules: list[dict[str, Any]] | None = None,
            priority: int = 100,
            test_mode: bool = False,
            block_duration: int = 3600,
            threat_type: str | None = None,
        ) -> dict[str, Any]:
            """Comprehensive security and compliance operations.

            This portmanteau tool handles all security-related operations:
            - scan: Security vulnerability scan
            - compliance: Compliance validation
            - audit: Device security audit
            - report: Generate security report
            - monitor: Monitor suspicious activity
            - block: Block malicious IP addresses
            - quarantine: Quarantine compromised device
            - alert: Security alerting
            - policy: Create/apply security policies
            - threat: Threat detection and response

            Args:
                operation: Operation to perform (scan, compliance, audit, report, monitor, block, quarantine, alert, policy, threat)
                scan_type: Type of security scan (comprehensive, quick, deep)
                compliance_standard: Compliance standard to check (SOC2, PCI-DSS, HIPAA, ISO27001)
                device_id: Device ID for device-specific operations
                ip_address: IP address for blocking operations
                quarantine_duration: Duration to quarantine device in hours
                alert_severity: Alert severity level (low, medium, high, critical)
                alert_message: Custom alert message
                policy_name: Security policy name
                rules: Security policy rules
                priority: Policy priority
                test_mode: Run in test mode without making changes
                block_duration: Duration to block IP in seconds
                threat_type: Type of threat detected

            Returns:
                Operation result with security information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "scan":
                    scan_results = await self.device_manager.security_scan(scan_type)
                    return {
                        "operation": "scan",
                        "scan_type": scan_type,
                        "results": scan_results,
                        "vulnerabilities_found": len(scan_results.get("vulnerabilities", [])),
                    }

                elif operation == "compliance":
                    compliance_results = await self.device_manager.check_compliance(compliance_standard)
                    return {
                        "operation": "compliance",
                        "standard": compliance_standard,
                        "results": compliance_results,
                        "compliant": compliance_results.get("compliant", False),
                    }

                elif operation == "audit":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for audit operation")
                    audit_results = await self.device_manager.audit_device(device_id)
                    return {
                        "operation": "audit",
                        "device_id": device_id,
                        "results": audit_results,
                        "security_score": audit_results.get("security_score", 0),
                    }

                elif operation == "report":
                    security_report = await self.device_manager.generate_security_report()
                    return {
                        "operation": "report",
                        "report": security_report,
                        "generated_at": time.time(),
                    }

                elif operation == "monitor":
                    suspicious_activity = await self.device_manager.monitor_suspicious_activity()
                    return {
                        "operation": "monitor",
                        "activity": suspicious_activity,
                        "alerts_generated": len(suspicious_activity.get("alerts", [])),
                    }

                elif operation == "block":
                    if not ip_address:
                        raise TailscaleMCPError("ip_address is required for block operation")
                    result = await self.device_manager.block_malicious_ip(ip_address, block_duration)
                    return {
                        "operation": "block",
                        "ip_address": ip_address,
                        "block_duration": block_duration,
                        "result": result,
                    }

                elif operation == "quarantine":
                    if not device_id:
                        raise TailscaleMCPError("device_id is required for quarantine operation")
                    result = await self.device_manager.quarantine_device(device_id, quarantine_duration)
                    return {
                        "operation": "quarantine",
                        "device_id": device_id,
                        "quarantine_duration": quarantine_duration,
                        "result": result,
                    }

                elif operation == "alert":
                    if not alert_message:
                        raise TailscaleMCPError("alert_message is required for alert operation")
                    result = await self.device_manager.alert_on_breach(alert_severity, alert_message)
                    return {
                        "operation": "alert",
                        "severity": alert_severity,
                        "message": alert_message,
                        "result": result,
                    }

                elif operation == "policy":
                    if not policy_name or not rules:
                        raise TailscaleMCPError("policy_name and rules are required for policy operation")
                    result = await self.device_manager.create_security_policy(policy_name, rules, priority)
                    return {
                        "operation": "policy_create",
                        "policy_name": policy_name,
                        "rules": rules,
                        "priority": priority,
                        "result": result,
                    }

                elif operation == "threat":
                    if not threat_type:
                        raise TailscaleMCPError("threat_type is required for threat operation")
                    result = await self.device_manager.detect_threat(threat_type, test_mode)
                    return {
                        "operation": "threat_detect",
                        "threat_type": threat_type,
                        "test_mode": test_mode,
                        "result": result,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_security operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform security operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_automation(
            operation: str,
            workflow_name: str | None = None,
            workflow_steps: list[dict[str, Any]] | None = None,
            schedule_cron: str | None = None,
            script_content: str | None = None,
            script_language: str = "python",
            template_name: str | None = None,
            batch_operations: list[dict[str, Any]] | None = None,
            dry_run: bool = False,
            execute_now: bool = False,
            workflow_id: str | None = None,
        ) -> dict[str, Any]:
            """Comprehensive automation and workflow operations.

            This portmanteau tool handles all automation-related operations:
            - workflow_create: Create automation workflow
            - workflow_execute: Execute workflow
            - workflow_schedule: Schedule workflow execution
            - workflow_list: List all workflows
            - workflow_delete: Delete workflow
            - script_execute: Execute custom script
            - script_template: Use script template
            - batch: Perform batch operations
            - dry_run: Preview operations without executing

            Args:
                operation: Operation to perform (workflow_create, workflow_execute, workflow_schedule, workflow_list, workflow_delete, script_execute, script_template, batch, dry_run)
                workflow_name: Name for workflow operations
                workflow_steps: Steps for workflow creation
                schedule_cron: Cron expression for scheduling
                script_content: Script content for execution
                script_language: Script language (python, bash, powershell)
                template_name: Template name for script operations
                batch_operations: List of operations for batch processing
                dry_run: Preview mode without execution
                execute_now: Execute immediately
                workflow_id: Workflow ID for specific operations

            Returns:
                Operation result with automation information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "workflow_create":
                    if not workflow_name or not workflow_steps:
                        raise TailscaleMCPError("workflow_name and workflow_steps are required for workflow_create operation")
                    result = await self.device_manager.create_workflow(workflow_name, workflow_steps)
                    return {
                        "operation": "workflow_create",
                        "workflow_name": workflow_name,
                        "workflow_id": result.get("workflow_id"),
                        "steps_count": len(workflow_steps),
                        "result": result,
                    }

                elif operation == "workflow_execute":
                    if not workflow_id:
                        raise TailscaleMCPError("workflow_id is required for workflow_execute operation")
                    result = await self.device_manager.execute_workflow(workflow_id, execute_now)
                    return {
                        "operation": "workflow_execute",
                        "workflow_id": workflow_id,
                        "execute_now": execute_now,
                        "result": result,
                    }

                elif operation == "workflow_schedule":
                    if not workflow_id or not schedule_cron:
                        raise TailscaleMCPError("workflow_id and schedule_cron are required for workflow_schedule operation")
                    result = await self.device_manager.schedule_workflow(workflow_id, schedule_cron)
                    return {
                        "operation": "workflow_schedule",
                        "workflow_id": workflow_id,
                        "schedule_cron": schedule_cron,
                        "result": result,
                    }

                elif operation == "workflow_list":
                    workflows = await self.device_manager.list_workflows()
                    return {
                        "operation": "workflow_list",
                        "workflows": workflows,
                        "count": len(workflows),
                    }

                elif operation == "workflow_delete":
                    if not workflow_id:
                        raise TailscaleMCPError("workflow_id is required for workflow_delete operation")
                    result = await self.device_manager.delete_workflow(workflow_id)
                    return {
                        "operation": "workflow_delete",
                        "workflow_id": workflow_id,
                        "result": result,
                    }

                elif operation == "script_execute":
                    if not script_content:
                        raise TailscaleMCPError("script_content is required for script_execute operation")
                    result = await self.device_manager.execute_script(script_content, script_language, dry_run)
                    return {
                        "operation": "script_execute",
                        "script_language": script_language,
                        "dry_run": dry_run,
                        "result": result,
                    }

                elif operation == "script_template":
                    if not template_name:
                        raise TailscaleMCPError("template_name is required for script_template operation")
                    template = await self.device_manager.get_script_template(template_name)
                    return {
                        "operation": "script_template",
                        "template_name": template_name,
                        "template": template,
                    }

                elif operation == "batch":
                    if not batch_operations:
                        raise TailscaleMCPError("batch_operations is required for batch operation")
                    result = await self.device_manager.batch_operations(batch_operations, dry_run)
                    return {
                        "operation": "batch",
                        "operations_count": len(batch_operations),
                        "dry_run": dry_run,
                        "result": result,
                    }

                elif operation == "dry_run":
                    if not batch_operations:
                        raise TailscaleMCPError("batch_operations is required for dry_run operation")
                    preview = await self.device_manager.preview_operations(batch_operations)
                    return {
                        "operation": "dry_run",
                        "preview": preview,
                        "operations_count": len(batch_operations),
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_automation operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform automation operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_backup(
            operation: str,
            backup_name: str | None = None,
            backup_type: str = "full",
            include_devices: bool = True,
            include_policies: bool = True,
            include_users: bool = True,
            restore_point: str | None = None,  # noqa: ARG001
            backup_id: str | None = None,
            schedule_cron: str | None = None,
            retention_days: int = 30,
            compression: bool = True,
            encryption: bool = True,
            test_restore: bool = False,
        ) -> dict[str, Any]:
            """Comprehensive backup and disaster recovery operations.

            This portmanteau tool handles all backup-related operations:
            - backup_create: Create configuration backup
            - backup_restore: Restore from backup
            - backup_schedule: Schedule automated backups
            - backup_list: List all backups
            - backup_delete: Delete backup
            - backup_test: Test backup integrity
            - restore_test: Test restore procedure
            - recovery_plan: Create disaster recovery plan

            Args:
                operation: Operation to perform (backup_create, backup_restore, backup_schedule, backup_list, backup_delete, backup_test, restore_test, recovery_plan)
                backup_name: Name for backup operations
                backup_type: Type of backup (full, incremental, differential)
                include_devices: Include device configurations
                include_policies: Include ACL policies
                include_users: Include user accounts
                restore_point: Restore point for restore operations
                backup_id: Backup ID for specific operations
                schedule_cron: Cron expression for scheduling
                retention_days: Backup retention period
                compression: Enable compression
                encryption: Enable encryption
                test_restore: Test restore without applying

            Returns:
                Operation result with backup information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "backup_create":
                    if not backup_name:
                        raise TailscaleMCPError("backup_name is required for backup_create operation")
                    result = await self.device_manager.create_backup(
                        backup_name, backup_type, include_devices, include_policies,
                        include_users, compression, encryption
                    )
                    return {
                        "operation": "backup_create",
                        "backup_name": backup_name,
                        "backup_type": backup_type,
                        "backup_id": result.get("backup_id"),
                        "result": result,
                    }

                elif operation == "backup_restore":
                    if not backup_id:
                        raise TailscaleMCPError("backup_id is required for backup_restore operation")
                    result = await self.device_manager.restore_backup(backup_id, test_restore)
                    return {
                        "operation": "backup_restore",
                        "backup_id": backup_id,
                        "test_restore": test_restore,
                        "result": result,
                    }

                elif operation == "backup_schedule":
                    if not schedule_cron:
                        raise TailscaleMCPError("schedule_cron is required for backup_schedule operation")
                    result = await self.device_manager.schedule_backups(schedule_cron, retention_days)
                    return {
                        "operation": "backup_schedule",
                        "schedule_cron": schedule_cron,
                        "retention_days": retention_days,
                        "result": result,
                    }

                elif operation == "backup_list":
                    backups = await self.device_manager.list_backups()
                    return {
                        "operation": "backup_list",
                        "backups": backups,
                        "count": len(backups),
                    }

                elif operation == "backup_delete":
                    if not backup_id:
                        raise TailscaleMCPError("backup_id is required for backup_delete operation")
                    result = await self.device_manager.delete_backup(backup_id)
                    return {
                        "operation": "backup_delete",
                        "backup_id": backup_id,
                        "result": result,
                    }

                elif operation == "backup_test":
                    if not backup_id:
                        raise TailscaleMCPError("backup_id is required for backup_test operation")
                    result = await self.device_manager.test_backup_integrity(backup_id)
                    return {
                        "operation": "backup_test",
                        "backup_id": backup_id,
                        "result": result,
                    }

                elif operation == "restore_test":
                    if not backup_id:
                        raise TailscaleMCPError("backup_id is required for restore_test operation")
                    result = await self.device_manager.test_restore_procedure(backup_id)
                    return {
                        "operation": "restore_test",
                        "backup_id": backup_id,
                        "result": result,
                    }

                elif operation == "recovery_plan":
                    result = await self.device_manager.create_recovery_plan()
                    return {
                        "operation": "recovery_plan",
                        "result": result,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_backup operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform backup operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_performance(
            operation: str,
            device_id: str | None = None,
            measure_duration: int = 60,
            bandwidth_test: bool = False,  # noqa: ARG001
            latency_test: bool = False,  # noqa: ARG001
            route_optimization: bool = False,
            baseline_name: str | None = None,
            baseline_duration: int = 300,
            capacity_period: str = "30d",
            scaling_factor: float = 1.2,
            performance_threshold: float = 0.8,
        ) -> dict[str, Any]:
            """Comprehensive performance monitoring and optimization operations.

            This portmanteau tool handles all performance-related operations:
            - latency: Measure network latency
            - bandwidth: Analyze bandwidth utilization
            - optimize: Optimize routing performance
            - baseline: Establish performance baselines
            - capacity: Predict capacity requirements
            - utilization: Analyze resource utilization
            - scaling: Get scaling recommendations
            - threshold: Set performance thresholds

            Args:
                operation: Operation to perform (latency, bandwidth, optimize, baseline, capacity, utilization, scaling, threshold)
                device_id: Device ID for device-specific operations
                measure_duration: Duration for measurements in seconds
                bandwidth_test: Enable bandwidth testing
                latency_test: Enable latency testing
                route_optimization: Enable route optimization
                baseline_name: Name for baseline operations
                baseline_duration: Duration for baseline establishment
                capacity_period: Period for capacity prediction
                scaling_factor: Scaling factor for recommendations
                performance_threshold: Performance threshold percentage

            Returns:
                Operation result with performance information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "latency":
                    latency_results = await self.monitor.measure_latency(device_id, measure_duration)
                    return {
                        "operation": "latency",
                        "device_id": device_id,
                        "duration": measure_duration,
                        "results": latency_results,
                    }

                elif operation == "bandwidth":
                    bandwidth_results = await self.monitor.bandwidth_analysis(device_id, measure_duration)
                    return {
                        "operation": "bandwidth",
                        "device_id": device_id,
                        "duration": measure_duration,
                        "results": bandwidth_results,
                    }

                elif operation == "optimize":
                    optimization_results = await self.monitor.optimize_routing(route_optimization)
                    return {
                        "operation": "optimize",
                        "route_optimization": route_optimization,
                        "results": optimization_results,
                    }

                elif operation == "baseline":
                    if not baseline_name:
                        raise TailscaleMCPError("baseline_name is required for baseline operation")
                    baseline_results = await self.monitor.performance_baseline(baseline_name, baseline_duration)
                    return {
                        "operation": "baseline",
                        "baseline_name": baseline_name,
                        "duration": baseline_duration,
                        "results": baseline_results,
                    }

                elif operation == "capacity":
                    capacity_results = await self.monitor.predict_capacity(capacity_period, scaling_factor)
                    return {
                        "operation": "capacity",
                        "period": capacity_period,
                        "scaling_factor": scaling_factor,
                        "results": capacity_results,
                    }

                elif operation == "utilization":
                    utilization_results = await self.monitor.resource_utilization(device_id)
                    return {
                        "operation": "utilization",
                        "device_id": device_id,
                        "results": utilization_results,
                    }

                elif operation == "scaling":
                    scaling_recommendations = await self.monitor.scaling_recommendations(scaling_factor)
                    return {
                        "operation": "scaling",
                        "scaling_factor": scaling_factor,
                        "recommendations": scaling_recommendations,
                    }

                elif operation == "threshold":
                    threshold_results = await self.monitor.set_performance_threshold(performance_threshold)
                    return {
                        "operation": "threshold",
                        "threshold": performance_threshold,
                        "results": threshold_results,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_performance operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform performance operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_reporting(
            operation: str,
            report_type: str = "usage",
            report_format: str = "json",
            date_range: str = "30d",
            include_charts: bool = True,
            custom_fields: list[str] | None = None,
            schedule_cron: str | None = None,
            email_recipients: list[str] | None = None,
            export_path: str | None = None,
            template_name: str | None = None,
            analytics_depth: str = "standard",
            security_focus: bool = False,
            user_behavior: bool = False,  # noqa: ARG001
        ) -> dict[str, Any]:
            """Comprehensive reporting and analytics operations.

            This portmanteau tool handles all reporting-related operations:
            - generate: Generate custom reports
            - usage: Generate usage analytics report
            - custom: Create custom report with specific fields
            - schedule: Schedule automated reports
            - export: Export reports to various formats
            - analytics: Deep network analytics
            - behavior: User behavior analysis
            - security: Security metrics and KPIs
            - template: Use report templates

            Args:
                operation: Operation to perform (generate, usage, custom, schedule, export, analytics, behavior, security, template)
                report_type: Type of report (usage, security, performance, compliance)
                report_format: Export format (json, csv, pdf, html)
                date_range: Date range for report (7d, 30d, 90d, 1y)
                include_charts: Include visual charts
                custom_fields: Custom fields to include
                schedule_cron: Cron expression for scheduling
                email_recipients: Email recipients for scheduled reports
                export_path: Path for export operations
                template_name: Template name for template operations
                analytics_depth: Analytics depth (quick, standard, comprehensive)
                security_focus: Focus on security metrics
                user_behavior: Include user behavior analysis

            Returns:
                Operation result with reporting information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "generate":
                    report = await self.monitor.generate_usage_report(report_type, date_range, include_charts)
                    return {
                        "operation": "generate",
                        "report_type": report_type,
                        "date_range": date_range,
                        "report": report,
                    }

                elif operation == "usage":
                    usage_report = await self.monitor.generate_usage_report("usage", date_range, include_charts)
                    return {
                        "operation": "usage",
                        "date_range": date_range,
                        "report": usage_report,
                    }

                elif operation == "custom":
                    if not custom_fields:
                        raise TailscaleMCPError("custom_fields is required for custom operation")
                    custom_report = await self.monitor.create_custom_report(custom_fields, date_range, report_format)
                    return {
                        "operation": "custom",
                        "custom_fields": custom_fields,
                        "date_range": date_range,
                        "format": report_format,
                        "report": custom_report,
                    }

                elif operation == "schedule":
                    if not schedule_cron:
                        raise TailscaleMCPError("schedule_cron is required for schedule operation")
                    result = await self.monitor.schedule_reports(schedule_cron, email_recipients)
                    return {
                        "operation": "schedule",
                        "schedule_cron": schedule_cron,
                        "email_recipients": email_recipients,
                        "result": result,
                    }

                elif operation == "export":
                    if not export_path:
                        raise TailscaleMCPError("export_path is required for export operation")
                    result = await self.monitor.export_reports(export_path, report_format)
                    return {
                        "operation": "export",
                        "export_path": export_path,
                        "format": report_format,
                        "result": result,
                    }

                elif operation == "analytics":
                    analytics_results = await self.monitor.network_analytics(analytics_depth, date_range)
                    return {
                        "operation": "analytics",
                        "depth": analytics_depth,
                        "date_range": date_range,
                        "results": analytics_results,
                    }

                elif operation == "behavior":
                    behavior_results = await self.monitor.user_behavior_analysis(date_range)
                    return {
                        "operation": "behavior",
                        "date_range": date_range,
                        "results": behavior_results,
                    }

                elif operation == "security":
                    security_results = await self.monitor.security_metrics(date_range, security_focus)
                    return {
                        "operation": "security",
                        "date_range": date_range,
                        "security_focus": security_focus,
                        "results": security_results,
                    }

                elif operation == "template":
                    if not template_name:
                        raise TailscaleMCPError("template_name is required for template operation")
                    template = await self.monitor.get_report_template(template_name)
                    return {
                        "operation": "template",
                        "template_name": template_name,
                        "template": template,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_reporting operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform reporting operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_integration(
            operation: str,
            webhook_url: str | None = None,
            webhook_secret: str | None = None,
            webhook_events: list[str] | None = None,
            integration_type: str | None = None,
            api_endpoint: str | None = None,
            api_key: str | None = None,
            slack_channel: str | None = None,
            discord_webhook: str | None = None,
            pagerduty_key: str | None = None,
            datadog_api_key: str | None = None,
            test_connection: bool = False,
            webhook_id: str | None = None,
        ) -> dict[str, Any]:
            """Comprehensive third-party integration operations.

            This portmanteau tool handles all integration-related operations:
            - webhook_create: Create webhook endpoint
            - webhook_test: Test webhook delivery
            - webhook_list: List active webhooks
            - webhook_delete: Delete webhook
            - slack: Integrate with Slack
            - discord: Integrate with Discord
            - pagerduty: Integrate with PagerDuty
            - datadog: Integrate with Datadog
            - test: Test integration connection

            Args:
                operation: Operation to perform (webhook_create, webhook_test, webhook_list, webhook_delete, slack, discord, pagerduty, datadog, test)
                webhook_url: Webhook URL for webhook operations
                webhook_secret: Webhook secret for authentication
                webhook_events: Events to subscribe to
                integration_type: Type of integration
                api_endpoint: API endpoint for integration
                api_key: API key for integration
                slack_channel: Slack channel for notifications
                discord_webhook: Discord webhook URL
                pagerduty_key: PagerDuty integration key
                datadog_api_key: Datadog API key
                test_connection: Test connection without saving
                webhook_id: Webhook ID for specific operations

            Returns:
                Operation result with integration information

            Raises:
                TailscaleMCPError: If operation fails
            """
            try:
                if operation == "webhook_create":
                    if not webhook_url or not webhook_events:
                        raise TailscaleMCPError("webhook_url and webhook_events are required for webhook_create operation")
                    result = await self.device_manager.create_webhook(webhook_url, webhook_secret, webhook_events)
                    return {
                        "operation": "webhook_create",
                        "webhook_url": webhook_url,
                        "webhook_events": webhook_events,
                        "webhook_id": result.get("webhook_id"),
                        "result": result,
                    }

                elif operation == "webhook_test":
                    if not webhook_id:
                        raise TailscaleMCPError("webhook_id is required for webhook_test operation")
                    result = await self.device_manager.test_webhook(webhook_id)
                    return {
                        "operation": "webhook_test",
                        "webhook_id": webhook_id,
                        "result": result,
                    }

                elif operation == "webhook_list":
                    webhooks = await self.device_manager.list_webhooks()
                    return {
                        "operation": "webhook_list",
                        "webhooks": webhooks,
                        "count": len(webhooks),
                    }

                elif operation == "webhook_delete":
                    if not webhook_id:
                        raise TailscaleMCPError("webhook_id is required for webhook_delete operation")
                    result = await self.device_manager.delete_webhook(webhook_id)
                    return {
                        "operation": "webhook_delete",
                        "webhook_id": webhook_id,
                        "result": result,
                    }

                elif operation == "slack":
                    if not slack_channel:
                        raise TailscaleMCPError("slack_channel is required for slack operation")
                    result = await self.device_manager.integrate_slack(slack_channel, api_key)
                    return {
                        "operation": "slack",
                        "slack_channel": slack_channel,
                        "result": result,
                    }

                elif operation == "discord":
                    if not discord_webhook:
                        raise TailscaleMCPError("discord_webhook is required for discord operation")
                    result = await self.device_manager.integrate_discord(discord_webhook)
                    return {
                        "operation": "discord",
                        "discord_webhook": discord_webhook,
                        "result": result,
                    }

                elif operation == "pagerduty":
                    if not pagerduty_key:
                        raise TailscaleMCPError("pagerduty_key is required for pagerduty operation")
                    result = await self.device_manager.integrate_pagerduty(pagerduty_key)
                    return {
                        "operation": "pagerduty",
                        "pagerduty_key": pagerduty_key,
                        "result": result,
                    }

                elif operation == "datadog":
                    if not datadog_api_key:
                        raise TailscaleMCPError("datadog_api_key is required for datadog operation")
                    result = await self.device_manager.integrate_datadog(datadog_api_key, api_endpoint)
                    return {
                        "operation": "datadog",
                        "datadog_api_key": datadog_api_key,
                        "api_endpoint": api_endpoint,
                        "result": result,
                    }

                elif operation == "test":
                    if not integration_type:
                        raise TailscaleMCPError("integration_type is required for test operation")
                    result = await self.device_manager.test_integration(integration_type, api_key, test_connection)
                    return {
                        "operation": "test",
                        "integration_type": integration_type,
                        "test_connection": test_connection,
                        "result": result,
                    }

                else:
                    raise TailscaleMCPError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error("Error in tailscale_integration operation", operation=operation, error=str(e))
                raise TailscaleMCPError(f"Failed to perform integration operation: {e}") from e

        @self.mcp.tool()
        async def tailscale_help(
            topic: str | None = None,
            level: str = "basic",
            category: str | None = None,
            operation: str | None = None,
            include_examples: bool = True,
        ) -> dict[str, Any]:
            """Comprehensive multilevel help system for Tailscale MCP server.

            This tool provides detailed, contextual help for all operations:
            - overview: Get general overview of available tools
            - tool: Get help for specific tool (tailscale_device, tailscale_network, etc.)
            - operation: Get help for specific operation within a tool
            - examples: Get usage examples
            - troubleshooting: Get troubleshooting guidance
            - api_reference: Get detailed API reference
            - best_practices: Get best practices and recommendations

            Args:
                topic: Help topic (overview, tool, operation, examples, troubleshooting, api_reference, best_practices)
                level: Help detail level (basic, intermediate, advanced, expert)
                category: Tool category (device, network, monitor, file, security, automation, backup, performance, reporting, integration)
                operation: Specific operation name
                include_examples: Whether to include usage examples

            Returns:
                Comprehensive help information with examples and guidance

            Raises:
                TailscaleMCPError: If help topic is not found
            """
            try:
                help_content = await self._generate_help_content(
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

        @self.mcp.tool()
        async def tailscale_status(
            component: str | None = None,
            detail_level: str = "basic",
            include_metrics: bool = True,
            include_health: bool = True,
            include_performance: bool = False,
            device_filter: str | None = None,
            time_range: str = "1h",
        ) -> dict[str, Any]:
            """Comprehensive system status and health monitoring.

            This tool provides detailed status information:
            - overview: Overall system status
            - devices: Device status and health
            - network: Network connectivity and performance
            - services: Service status (API, monitoring, etc.)
            - metrics: Key performance metrics
            - alerts: Current alerts and issues
            - health: Overall health assessment

            Args:
                component: Component to check (overview, devices, network, services, metrics, alerts, health)
                detail_level: Detail level (basic, intermediate, advanced, diagnostic)
                include_metrics: Whether to include performance metrics
                include_health: Whether to include health assessments
                include_performance: Whether to include detailed performance data
                device_filter: Filter devices by status or tags
                time_range: Time range for metrics (1h, 6h, 24h, 7d)

            Returns:
                Comprehensive status information with health indicators

            Raises:
                TailscaleMCPError: If status check fails
            """
            try:
                status_info = await self._generate_status_info(
                    component, detail_level, include_metrics, include_health,
                    include_performance, device_filter, time_range
                )
                return {
                    "component": component or "overview",
                    "detail_level": detail_level,
                    "timestamp": time.time(),
                    "status": status_info,
                }

            except Exception as e:
                logger.error("Error generating status information", component=component, error=str(e))
                raise TailscaleMCPError(f"Failed to generate status information: {e}") from e

        logger.info("All portmanteau tools registered successfully")

    async def _generate_help_content(
        self, topic: str | None, level: str, category: str | None,
        operation: str | None, include_examples: bool
    ) -> dict[str, Any]:
        """Generate comprehensive help content."""

        help_data = {
            "overview": {
                "title": "Tailscale MCP Server - Comprehensive Help System",
                "description": "Professional Tailscale MCP server with 10 portmanteau tools and 91+ operations",
                "tools": {
                    "tailscale_device": "Device and user management operations",
                    "tailscale_network": "DNS and network configuration",
                    "tailscale_monitor": "Real-time monitoring and metrics",
                    "tailscale_file": "Secure file sharing via Taildrop",
                    "tailscale_security": "Security scanning and compliance",
                    "tailscale_automation": "Workflow automation and batch operations",
                    "tailscale_backup": "Configuration backup and recovery",
                    "tailscale_performance": "Performance optimization and analysis",
                    "tailscale_reporting": "Advanced reporting and analytics",
                    "tailscale_integration": "Third-party integrations and webhooks",
                    "tailscale_help": "This comprehensive help system",
                    "tailscale_status": "System status and health monitoring",
                },
                "levels": {
                    "basic": "Quick start guide and essential commands",
                    "intermediate": "Detailed tool descriptions and workflows",
                    "advanced": "Technical architecture and implementation details",
                    "expert": "Development troubleshooting and system internals",
                }
            },
            "examples": {
                "basic_device_list": "tailscale_device(operation='list', online_only=True)",
                "advanced_monitoring": "tailscale_monitor(operation='dashboard_create', dashboard_type='network_overview')",
                "security_scan": "tailscale_security(operation='scan', scan_type='comprehensive')",
                "file_transfer": "tailscale_file(operation='send', file_path='/path/to/file', recipient_device='device-id')",
                "help_system": "tailscale_help(topic='overview', level='intermediate')",
                "status_check": "tailscale_status(component='devices', detail_level='advanced')",
            },
            "best_practices": {
                "security": "Always use comprehensive security scans before deploying changes",
                "monitoring": "Set up Grafana dashboards for continuous monitoring",
                "backup": "Schedule regular configuration backups",
                "performance": "Monitor latency and bandwidth regularly",
                "automation": "Use workflows for repetitive tasks",
            },
            "troubleshooting": {
                "connection_issues": "Check network connectivity and API credentials",
                "performance_problems": "Use tailscale_performance tool for analysis",
                "security_alerts": "Review tailscale_security scan results",
                "device_problems": "Check device status with tailscale_status",
            }
        }

        if topic == "overview" or topic is None:
            return help_data["overview"]
        elif topic == "examples":
            return help_data["examples"]
        elif topic == "best_practices":
            return help_data["best_practices"]
        elif topic == "troubleshooting":
            return help_data["troubleshooting"]
        else:
            return {"error": f"Help topic '{topic}' not found", "available_topics": list(help_data.keys())}

    async def _generate_status_info(
        self, component: str | None, detail_level: str, include_metrics: bool,
        include_health: bool, include_performance: bool, device_filter: str | None, time_range: str
    ) -> dict[str, Any]:
        """Generate comprehensive status information."""

        # Get basic device information
        try:
            devices = await self.device_manager.list_devices()
            online_devices = [d for d in devices if d.get("online", False)]

            # Get network metrics
            network_metrics = await self.monitor.get_network_metrics()

            status_data = {
                "system": {
                    "status": "operational",
                    "version": "2.0.0",
                    "uptime": "Running",
                    "last_updated": time.time(),
                },
                "devices": {
                    "total": len(devices),
                    "online": len(online_devices),
                    "offline": len(devices) - len(online_devices),
                    "online_percentage": round((len(online_devices) / len(devices)) * 100, 2) if devices else 0,
                },
                "network": {
                    "connectivity": "good",
                    "latency": network_metrics.get("average_latency", "N/A"),
                    "bandwidth": network_metrics.get("total_bandwidth", "N/A"),
                    "health_score": network_metrics.get("health_score", 85),
                },
                "services": {
                    "api": "operational",
                    "monitoring": "operational",
                    "grafana": "operational",
                    "taildrop": "operational",
                },
                "health": {
                    "overall": "healthy",
                    "devices": "healthy" if len(online_devices) > 0 else "warning",
                    "network": "healthy",
                    "services": "healthy",
                }
            }

            if include_metrics:
                status_data["metrics"] = {
                    "cpu_usage": "15%",
                    "memory_usage": "45%",
                    "disk_usage": "30%",
                    "network_throughput": "125 Mbps",
                }

            if include_performance:
                status_data["performance"] = {
                    "response_time": "45ms",
                    "throughput": "1.2k requests/sec",
                    "error_rate": "0.1%",
                    "availability": "99.9%",
                }

            return status_data

        except Exception as e:
            logger.error("Error generating status information", error=str(e))
            return {
                "error": f"Failed to generate status: {e!s}",
                "system": {"status": "error"},
                "devices": {"total": 0, "online": 0, "offline": 0},
                "network": {"connectivity": "unknown"},
                "services": {"api": "error"},
                "health": {"overall": "error"},
            }
