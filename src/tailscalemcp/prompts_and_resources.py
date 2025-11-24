"""
MCP Prompts and Resources for Tailscale MCP Server.

This module provides reusable prompts and resources for common Tailscale operations.
Prompts are pre-configured templates that help users interact with the server.
Resources are read-only data sources accessible via URIs.
"""

from typing import Any


def register_prompts(mcp: Any) -> list[Any]:
    """Register all prompts with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        List of prompt function references to keep them alive
    """

    @mcp.prompt()
    def list_devices_prompt(
        online_only: bool = False, filter_tags: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """List all devices in the Tailscale tailnet.

        This prompt helps you list devices with optional filtering by online status and tags.

        Args:
            online_only: If True, only show devices that are currently online
            filter_tags: Optional list of tags to filter devices (devices must have ALL tags)

        Returns:
            List of message dictionaries with device information
        """
        tags_str = f" with tags {', '.join(filter_tags)}" if filter_tags else ""
        online_str = "online " if online_only else ""
        query = f"List all {online_str}devices{tags_str} in the tailnet"

        return [
            {
                "role": "user",
                "content": query,
            }
        ]

    @mcp.prompt()
    def get_device_details_prompt(device_id: str) -> list[dict[str, Any]]:
        """Get detailed information about a specific device.

        This prompt retrieves comprehensive information about a device including
        its configuration, status, tags, and network settings.

        Args:
            device_id: The device ID or hostname to query

        Returns:
            List of message dictionaries requesting device details
        """
        return [
            {
                "role": "user",
                "content": f"Show me detailed information for device {device_id}",
            }
        ]

    @mcp.prompt()
    def authorize_device_prompt(
        device_id: str, reason: str | None = None
    ) -> list[dict[str, Any]]:
        """Authorize a device to join the Tailscale tailnet.

        This prompt helps you authorize a pending device request.

        Args:
            device_id: The device ID to authorize
            reason: Optional reason for authorization (for audit logging)

        Returns:
            List of message dictionaries requesting device authorization
        """
        reason_str = f" (reason: {reason})" if reason else ""
        return [
            {
                "role": "user",
                "content": f"Authorize device {device_id}{reason_str}",
            }
        ]

    @mcp.prompt()
    def check_network_status_prompt() -> list[dict[str, Any]]:
        """Check the overall network status and health.

        This prompt retrieves comprehensive network status including device connectivity,
        latency, and overall health metrics.

        Returns:
            List of message dictionaries requesting network status
        """
        return [
            {
                "role": "user",
                "content": "Show me the current network status and health",
            }
        ]

    @mcp.prompt()
    def create_security_report_prompt() -> list[dict[str, Any]]:
        """Generate a comprehensive security report.

        This prompt creates a detailed security report with vulnerabilities,
        compliance status, and recommendations.

        Returns:
            List of message dictionaries requesting security report
        """
        return [
            {
                "role": "user",
                "content": "Generate a comprehensive security report for the tailnet",
            }
        ]

    @mcp.prompt()
    def backup_configuration_prompt(
        backup_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Create a backup of the Tailscale configuration.

        This prompt helps you create a backup of device configurations, policies,
        and user accounts.

        Args:
            backup_name: Optional name for the backup (defaults to timestamp-based name)

        Returns:
            List of message dictionaries requesting configuration backup
        """
        name_str = f" named {backup_name}" if backup_name else ""
        return [
            {
                "role": "user",
                "content": f"Create a backup of the Tailscale configuration{name_str}",
            }
        ]

    # Return references to prevent garbage collection
    # The decorators register the functions, but we need to keep references
    # so they don't get garbage collected
    return [
        list_devices_prompt,
        get_device_details_prompt,
        authorize_device_prompt,
        check_network_status_prompt,
        create_security_report_prompt,
        backup_configuration_prompt,
    ]


def register_resources(mcp: Any, device_manager: Any, monitor: Any) -> list[Any]:
    """Register all resources with the MCP server.

    Args:
        mcp: FastMCP server instance
        device_manager: Device manager instance
        monitor: Monitor instance

    Returns:
        List of resource function references to keep them alive
    """

    @mcp.resource("tailscale://devices")
    async def devices_resource() -> str:
        """List all devices in the tailnet.

        This resource provides a read-only view of all devices in the tailnet.
        Access via: tailscale://devices

        Returns:
            JSON string with device list
        """
        import json

        devices = await device_manager.list_devices()
        return json.dumps(
            {
                "devices": devices,
                "count": len(devices),
                "resource": "tailscale://devices",
            },
            indent=2,
        )

    @mcp.resource("tailscale://devices/{device_id}")
    async def device_resource(device_id: str) -> str:
        """Get details for a specific device.

        This resource provides detailed information about a specific device.
        Access via: tailscale://devices/{device_id}

        Args:
            device_id: The device ID or hostname

        Returns:
            JSON string with device details
        """
        import json

        device = await device_manager.get_device(device_id)
        return json.dumps(
            {
                "device": device,
                "device_id": device_id,
                "resource": f"tailscale://devices/{device_id}",
            },
            indent=2,
        )

    @mcp.resource("tailscale://network/status")
    async def network_status_resource() -> str:
        """Get current network status.

        This resource provides real-time network status including connectivity,
        latency, and health metrics.
        Access via: tailscale://network/status

        Returns:
            JSON string with network status
        """
        import json

        status = await monitor.get_network_status()
        return json.dumps(
            {
                "status": status,
                "resource": "tailscale://network/status",
            },
            indent=2,
        )

    @mcp.resource("tailscale://network/topology")
    async def network_topology_resource() -> str:
        """Get network topology map.

        This resource provides a visual representation of the network topology
        showing device connections and relationships.
        Access via: tailscale://network/topology

        Returns:
            JSON string with topology data
        """
        import json

        topology = await monitor.generate_network_topology()
        return json.dumps(
            {
                "topology": topology,
                "resource": "tailscale://network/topology",
            },
            indent=2,
        )

    @mcp.resource("tailscale://security/report")
    async def security_report_resource() -> str:
        """Get security report.

        This resource provides a comprehensive security report with vulnerabilities,
        compliance status, and recommendations.
        Access via: tailscale://security/report

        Returns:
            JSON string with security report
        """
        import json

        report = await device_manager.generate_security_report()
        return json.dumps(
            {
                "report": report,
                "resource": "tailscale://security/report",
            },
            indent=2,
        )

    @mcp.resource("tailscale://monitoring/metrics")
    async def metrics_resource() -> str:
        """Get Prometheus-formatted metrics.

        This resource provides metrics in Prometheus exposition format.
        Access via: tailscale://monitoring/metrics

        Returns:
            Prometheus-formatted metrics string
        """
        metrics = await monitor.get_prometheus_metrics()
        return metrics

    @mcp.resource("tailscale://monitoring/health")
    async def health_resource() -> str:
        """Get network health report.

        This resource provides a comprehensive health report with status,
        issues, and recommendations.
        Access via: tailscale://monitoring/health

        Returns:
            JSON string with health report
        """
        import json

        health = await monitor.get_network_health_report()
        return json.dumps(
            {
                "health": health,
                "resource": "tailscale://monitoring/health",
            },
            indent=2,
        )

    # Return references to prevent garbage collection
    # The decorators register the functions, but we need to keep references
    # so they don't get garbage collected
    return [
        devices_resource,
        device_resource,
        network_status_resource,
        network_topology_resource,
        security_report_resource,
        metrics_resource,
        health_resource,
    ]


# Legacy class-based approach (kept for backwards compatibility)
class TailscalePrompts:
    """Prompts for common Tailscale operations."""

    def __init__(self, mcp: Any):
        """Initialize prompts with FastMCP instance.

        Args:
            mcp: FastMCP server instance
        """
        self.mcp = mcp
        self._register_prompts()

    def _register_prompts(self) -> None:
        """Register all prompts with the MCP server."""
        # Store references to keep functions alive
        self._prompt_functions = []

        @self.mcp.prompt()
        def list_devices_prompt(
            online_only: bool = False, filter_tags: list[str] | None = None
        ) -> list[dict[str, Any]]:
            """List all devices in the Tailscale tailnet.

            This prompt helps you list devices with optional filtering by online status and tags.

            Args:
                online_only: If True, only show devices that are currently online
                filter_tags: Optional list of tags to filter devices (devices must have ALL tags)

            Returns:
                List of message dictionaries with device information
            """
            tags_str = f" with tags {', '.join(filter_tags)}" if filter_tags else ""
            online_str = "online " if online_only else ""
            query = f"List all {online_str}devices{tags_str} in the tailnet"

            return [
                {
                    "role": "user",
                    "content": query,
                }
            ]

        @self.mcp.prompt()
        def get_device_details_prompt(device_id: str) -> list[dict[str, Any]]:
            """Get detailed information about a specific device.

            This prompt retrieves comprehensive information about a device including
            its configuration, status, tags, and network settings.

            Args:
                device_id: The device ID or hostname to query

            Returns:
                List of message dictionaries requesting device details
            """
            return [
                {
                    "role": "user",
                    "content": f"Show me detailed information for device {device_id}",
                }
            ]

        @self.mcp.prompt()
        def authorize_device_prompt(
            device_id: str, reason: str | None = None
        ) -> list[dict[str, Any]]:
            """Authorize a device to join the Tailscale tailnet.

            This prompt helps you authorize a pending device request.

            Args:
                device_id: The device ID to authorize
                reason: Optional reason for authorization (for audit logging)

            Returns:
                List of message dictionaries requesting device authorization
            """
            reason_str = f" (reason: {reason})" if reason else ""
            return [
                {
                    "role": "user",
                    "content": f"Authorize device {device_id}{reason_str}",
                }
            ]

        @self.mcp.prompt()
        def check_network_status_prompt() -> list[dict[str, Any]]:
            """Check the overall network status and health.

            This prompt retrieves comprehensive network status including device connectivity,
            latency, and overall health metrics.

            Returns:
                List of message dictionaries requesting network status
            """
            return [
                {
                    "role": "user",
                    "content": "Show me the current network status and health",
                }
            ]

        @self.mcp.prompt()
        def create_security_report_prompt() -> list[dict[str, Any]]:
            """Generate a comprehensive security report.

            This prompt creates a detailed security report with vulnerabilities,
            compliance status, and recommendations.

            Returns:
                List of message dictionaries requesting security report
            """
            return [
                {
                    "role": "user",
                    "content": "Generate a comprehensive security report for the tailnet",
                }
            ]

        @self.mcp.prompt()
        def backup_configuration_prompt(
            backup_name: str | None = None,
        ) -> list[dict[str, Any]]:
            """Create a backup of the Tailscale configuration.

            This prompt helps you create a backup of device configurations, policies,
            and user accounts.

            Args:
                backup_name: Optional name for the backup (defaults to timestamp-based name)

            Returns:
                List of message dictionaries requesting configuration backup
            """
            name_str = f" named {backup_name}" if backup_name else ""
            return [
                {
                    "role": "user",
                    "content": f"Create a backup of the Tailscale configuration{name_str}",
                }
            ]

        # Store function references to prevent garbage collection
        self._prompt_functions = [
            list_devices_prompt,
            get_device_details_prompt,
            authorize_device_prompt,
            check_network_status_prompt,
            create_security_report_prompt,
            backup_configuration_prompt,
        ]


class TailscaleResources:
    """Resources for Tailscale data access via URIs."""

    def __init__(self, mcp: Any, device_manager: Any, monitor: Any):
        """Initialize resources with FastMCP instance and managers.

        Args:
            mcp: FastMCP server instance
            device_manager: Device manager instance
            monitor: Monitor instance
        """
        self.mcp = mcp
        self.device_manager = device_manager
        self.monitor = monitor
        self._register_resources()

    def _register_resources(self) -> None:
        """Register all resources with the MCP server."""
        # Capture managers in local variables for closures
        device_manager = self.device_manager
        monitor = self.monitor
        # Store references to keep functions alive
        self._resource_functions = []

        @self.mcp.resource("tailscale://devices")
        async def devices_resource() -> str:
            """List all devices in the tailnet.

            This resource provides a read-only view of all devices in the tailnet.
            Access via: tailscale://devices

            Returns:
                JSON string with device list
            """
            import json

            devices = await device_manager.list_devices()
            return json.dumps(
                {
                    "devices": devices,
                    "count": len(devices),
                    "resource": "tailscale://devices",
                },
                indent=2,
            )

        @self.mcp.resource("tailscale://devices/{device_id}")
        async def device_resource(device_id: str) -> str:
            """Get details for a specific device.

            This resource provides detailed information about a specific device.
            Access via: tailscale://devices/{device_id}

            Args:
                device_id: The device ID or hostname

            Returns:
                JSON string with device details
            """
            import json

            device = await device_manager.get_device(device_id)
            return json.dumps(
                {
                    "device": device,
                    "device_id": device_id,
                    "resource": f"tailscale://devices/{device_id}",
                },
                indent=2,
            )

        @self.mcp.resource("tailscale://network/status")
        async def network_status_resource() -> str:
            """Get current network status.

            This resource provides real-time network status including connectivity,
            latency, and health metrics.
            Access via: tailscale://network/status

            Returns:
                JSON string with network status
            """
            import json

            status = await monitor.get_network_status()
            return json.dumps(
                {
                    "status": status,
                    "resource": "tailscale://network/status",
                },
                indent=2,
            )

        @self.mcp.resource("tailscale://network/topology")
        async def network_topology_resource() -> str:
            """Get network topology map.

            This resource provides a visual representation of the network topology
            showing device connections and relationships.
            Access via: tailscale://network/topology

            Returns:
                JSON string with topology data
            """
            import json

            topology = await monitor.generate_network_topology()
            return json.dumps(
                {
                    "topology": topology,
                    "resource": "tailscale://network/topology",
                },
                indent=2,
            )

        @self.mcp.resource("tailscale://security/report")
        async def security_report_resource() -> str:
            """Get security report.

            This resource provides a comprehensive security report with vulnerabilities,
            compliance status, and recommendations.
            Access via: tailscale://security/report

            Returns:
                JSON string with security report
            """
            import json

            report = await device_manager.generate_security_report()
            return json.dumps(
                {
                    "report": report,
                    "resource": "tailscale://security/report",
                },
                indent=2,
            )

        @self.mcp.resource("tailscale://monitoring/metrics")
        async def metrics_resource() -> str:
            """Get Prometheus-formatted metrics.

            This resource provides metrics in Prometheus exposition format.
            Access via: tailscale://monitoring/metrics

            Returns:
                Prometheus-formatted metrics string
            """
            metrics = await monitor.get_prometheus_metrics()
            return metrics

        @self.mcp.resource("tailscale://monitoring/health")
        async def health_resource() -> str:
            """Get network health report.

            This resource provides a comprehensive health report with status,
            issues, and recommendations.
            Access via: tailscale://monitoring/health

            Returns:
                JSON string with health report
            """
            import json

            health = await monitor.get_network_health_report()
            return json.dumps(
                {
                    "health": health,
                    "resource": "tailscale://monitoring/health",
                },
                indent=2,
            )

        # Store function references to prevent garbage collection
        self._resource_functions = [
            devices_resource,
            device_resource,
            network_status_resource,
            network_topology_resource,
            security_report_resource,
            metrics_resource,
            health_resource,
        ]
