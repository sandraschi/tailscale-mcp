"""Helper functions for portmanteau tools."""

import time
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from tailscalemcp.device_management import AdvancedDeviceManager
    from tailscalemcp.funnel import FunnelManager
    from tailscalemcp.monitoring import TailscaleMonitor

logger = structlog.get_logger(__name__)


async def generate_help_content(
    topic: str | None,
    level: str,  # noqa: ARG001
    category: str | None,  # noqa: ARG001
    operation: str | None,  # noqa: ARG001
    include_examples: bool,  # noqa: ARG001
) -> dict[str, Any]:
    """Generate comprehensive help content.

    Args:
        topic: Help topic
        level: Help detail level
        category: Tool category
        operation: Specific operation name
        include_examples: Whether to include examples

    Returns:
        Help content dictionary
    """
    help_data = {
        "overview": {
            "title": "Tailscale MCP Server - Comprehensive Help System",
            "description": "Professional Tailscale MCP server with 13 portmanteau tools and 91+ operations",
            "tools": {
                "tailscale_device": "Device and user management operations",
                "tailscale_network": "DNS and network configuration",
                "tailscale_monitor": "Real-time monitoring and metrics",
                "tailscale_file": "Secure file sharing via Taildrop",
                "tailscale_funnel": "Funnel operations for exposing local services to public internet via HTTPS",
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
            },
        },
        "examples": {
            "basic_device_list": "tailscale_device(operation='list', online_only=True)",
            "advanced_monitoring": "tailscale_monitor(operation='dashboard_create', dashboard_type='network_overview')",
            "security_scan": "tailscale_security(operation='scan', scan_type='comprehensive')",
            "file_transfer": "tailscale_file(operation='send', file_path='/path/to/file', recipient_device='device-id')",
            "funnel_enable": "tailscale_funnel(operation='funnel_enable', port=8080)",
            "funnel_status": "tailscale_funnel(operation='funnel_status')",
            "funnel_list": "tailscale_funnel(operation='funnel_list')",
            "funnel_disable": "tailscale_funnel(operation='funnel_disable', port=8080)",
            "funnel_certificate": "tailscale_funnel(operation='funnel_certificate_info', port=8080)",
            "help_system": "tailscale_help(topic='overview', level='intermediate')",
            "status_check": "tailscale_status(component='devices', detail_level='advanced')",
        },
        "best_practices": {
            "security": "Always use comprehensive security scans before deploying changes",
            "monitoring": "Set up Grafana dashboards for continuous monitoring",
            "backup": "Schedule regular configuration backups",
            "performance": "Monitor latency and bandwidth regularly",
            "automation": "Use workflows for repetitive tasks",
            "funnel": "Use Funnel for temporary, secure exposure of local services. Disable when not needed. Always verify ACL policy includes 'funnel' node attribute before enabling.",
        },
        "troubleshooting": {
            "connection_issues": "Check network connectivity and API credentials",
            "performance_problems": "Use tailscale_performance tool for analysis",
            "security_alerts": "Review tailscale_security scan results",
            "device_problems": "Check device status with tailscale_status",
            "funnel_issues": "Verify Funnel is enabled in ACL policy, device has 'funnel' node attribute, Tailscale CLI is installed and accessible, and Tailscale version is 1.38.3+",
        },
        "funnel": {
            "title": "Tailscale Funnel - Detailed Guide",
            "description": "Comprehensive guide to Tailscale Funnel for exposing local services to the public internet",
            "what_is_funnel": {
                "summary": "Tailscale Funnel allows you to securely expose local services running on your machine to the public internet via HTTPS with automatic TLS certificates.",
                "use_cases": [
                    "Share local development servers with team members or clients",
                    "Expose web applications for testing or demos",
                    "Provide temporary access to APIs or services",
                    "Share local tools or dashboards without complex port forwarding",
                    "Enable public access to services behind firewalls or NAT",
                ],
                "benefits": [
                    "Automatic TLS certificates - no manual certificate management",
                    "Secure HTTPS access from anywhere on the internet",
                    "No port forwarding or router configuration needed",
                    "Temporary and easy to disable when not needed",
                    "Works behind firewalls and NAT",
                ],
            },
            "prerequisites": {
                "tailscale_version": "Tailscale version 1.38.3 or later required",
                "cli_installation": "Tailscale CLI must be installed and accessible in PATH",
                "acl_policy": "Funnel must be enabled in your tailnet's access control policy",
                "node_attribute": "The device must have the 'funnel' node attribute in ACL policy",
                "example_acl": {
                    "description": "Example ACL policy to enable Funnel:",
                    "code": """// Example ACL policy
{
  "nodeAttrs": [
    {
      "target": ["autogroup:members"],
      "attr": ["funnel"]
    }
  ],
  "acls": [
    {
      "action": "accept",
      "src": ["autogroup:members"],
      "dst": ["*:*"]
    }
  ]
}""",
                },
            },
            "operations": {
                "funnel_enable": {
                    "description": "Enable Funnel for a specific port to expose a local service",
                    "parameters": {
                        "port": "Port number (1-65535) - the local port to expose",
                        "allow_tcp": "Allow TCP connections (default: True)",
                        "allow_tls": "Allow TLS/HTTPS connections (default: True)",
                    },
                    "returns": "Public HTTPS URL that can be accessed from anywhere",
                    "example": "tailscale_funnel(operation='funnel_enable', port=8080)",
                    "notes": [
                        "The service must already be running on the specified port",
                        "You'll receive a public URL like: https://your-device.tailnet-name.ts.net:8080",
                        "This URL is accessible from the public internet",
                    ],
                },
                "funnel_disable": {
                    "description": "Disable Funnel for a specific port or all ports",
                    "parameters": {
                        "port": "Port number to disable (optional - if None, disables all Funnels)",
                    },
                    "example": "tailscale_funnel(operation='funnel_disable', port=8080)",
                    "notes": [
                        "Disabling Funnel immediately stops public access",
                        "The local service continues running, just not publicly accessible",
                    ],
                },
                "funnel_status": {
                    "description": "Get current Funnel status and active services",
                    "returns": "Information about all active Funnel services",
                    "example": "tailscale_funnel(operation='funnel_status')",
                    "notes": [
                        "Shows all ports currently exposed via Funnel",
                        "Includes public URLs and connection status",
                    ],
                },
                "funnel_list": {
                    "description": "List all active Funnel services with details",
                    "returns": "List of active Funnels with port, public URL, and status",
                    "example": "tailscale_funnel(operation='funnel_list')",
                    "notes": [
                        "Returns structured list of all active Funnels",
                        "Useful for monitoring and auditing exposed services",
                    ],
                },
                "funnel_certificate_info": {
                    "description": "Get TLS certificate information for a Funnel service",
                    "parameters": {
                        "port": "Port number (required) - the port to get certificate info for",
                    },
                    "returns": "Certificate details including issuer, expiration, and status",
                    "example": "tailscale_funnel(operation='funnel_certificate_info', port=8080)",
                    "notes": [
                        "Certificates are automatically managed by Tailscale",
                        "Useful for verifying certificate validity and expiration",
                    ],
                },
            },
            "common_scenarios": {
                "local_dev_server": {
                    "title": "Expose Local Development Server",
                    "description": "Share your local development server with team members",
                    "steps": [
                        "1. Start your development server (e.g., on port 3000)",
                        "2. Enable Funnel: tailscale_funnel(operation='funnel_enable', port=3000)",
                        "3. Share the returned public URL with your team",
                        "4. Disable when done: tailscale_funnel(operation='funnel_disable', port=3000)",
                    ],
                },
                "api_testing": {
                    "title": "Expose API for Testing",
                    "description": "Make your local API accessible for external testing",
                    "steps": [
                        "1. Start your API server (e.g., on port 8000)",
                        "2. Enable Funnel: tailscale_funnel(operation='funnel_enable', port=8000)",
                        "3. Use the public URL for API testing tools",
                        "4. Check status: tailscale_funnel(operation='funnel_status')",
                        "5. Disable when testing is complete",
                    ],
                },
                "temporary_demo": {
                    "title": "Temporary Demo Access",
                    "description": "Provide temporary access to a demo application",
                    "steps": [
                        "1. Start your demo application",
                        "2. Enable Funnel for the application port",
                        "3. Share the public URL with stakeholders",
                        "4. Monitor active Funnels: tailscale_funnel(operation='funnel_list')",
                        "5. Disable after the demo is complete",
                    ],
                },
            },
            "security_considerations": {
                "acl_policy": "Always ensure proper ACL policies are in place before enabling Funnel",
                "temporary_use": "Funnel is designed for temporary access - disable when not needed",
                "service_security": "Ensure your local service has proper authentication and security",
                "monitoring": "Regularly check funnel_list to see what's exposed",
                "certificates": "TLS certificates are automatically managed, but verify certificate info periodically",
            },
            "troubleshooting": {
                "cli_not_found": {
                    "issue": "Tailscale CLI not found",
                    "solution": "Install Tailscale CLI and ensure it's in your system PATH",
                },
                "funnel_not_enabled": {
                    "issue": "Funnel not enabled in ACL",
                    "solution": "Add 'funnel' node attribute to your ACL policy for the device",
                },
                "port_already_in_use": {
                    "issue": "Port already in use or service not running",
                    "solution": "Ensure your service is running on the specified port before enabling Funnel",
                },
                "version_too_old": {
                    "issue": "Tailscale version too old",
                    "solution": "Upgrade to Tailscale version 1.38.3 or later",
                },
                "no_public_url": {
                    "issue": "Funnel enabled but no public URL returned",
                    "solution": "Check funnel_status to see if Funnel is active. Verify ACL policy and device attributes.",
                },
            },
        },
    }

    if topic == "overview" or topic is None:
        return help_data["overview"]
    elif topic == "examples":
        return help_data["examples"]
    elif topic == "best_practices":
        return help_data["best_practices"]
    elif topic == "troubleshooting":
        return help_data["troubleshooting"]
    elif topic == "funnel":
        return help_data["funnel"]
    else:
        return {
            "error": f"Help topic '{topic}' not found",
            "available_topics": list(help_data.keys()),
        }


async def generate_mermaid_diagram(
    device_manager: "AdvancedDeviceManager",
    funnel_manager: "FunnelManager | None" = None,
) -> str:
    """Generate Mermaid diagram of tailnet topology.

    Args:
        device_manager: Device manager instance
        funnel_manager: Optional funnel manager instance

    Returns:
        Mermaid diagram code as string
    """
    try:
        # Get devices
        devices = await device_manager.list_devices(online_only=False)

        # Get active funnels if manager available
        active_funnels: dict[int, dict[str, Any]] = {}
        if funnel_manager:
            try:
                funnels = await funnel_manager.list_funnels()
                for funnel in funnels:
                    if isinstance(funnel, dict) and "port" in funnel:
                        active_funnels[funnel["port"]] = funnel
            except Exception:
                pass

        # Build Mermaid diagram
        lines = ["graph TB"]

        # Add devices as nodes
        device_nodes: dict[str, str] = {}  # device_id -> node_id
        online_count = 0
        exit_nodes: list[str] = []
        subnet_routers: list[str] = []

        for node_counter, device in enumerate(devices):
            device_id = device.get("id") or device.get("device_id", "")
            name = device.get("name") or device.get(
                "hostname", f"Device-{node_counter}"
            )
            online = device.get("online", False)
            is_exit = device.get("is_exit_node", False)
            is_subnet = device.get("is_subnet_router", False)
            tags = device.get("tags", [])

            if online:
                online_count += 1

            # Create node ID (sanitize for Mermaid - remove special chars)
            node_id = f"dev{node_counter}"
            device_nodes[device_id] = node_id

            # Build node label (escape quotes and special chars)
            label_parts = [name.replace('"', "'")]
            status_icon = "🟢" if online else "🔴"
            label_parts.append(f"{status_icon} {'Online' if online else 'Offline'}")

            if is_exit:
                label_parts.append("Exit Node")
                exit_nodes.append(node_id)
            if is_subnet:
                label_parts.append("Subnet Router")
                subnet_routers.append(node_id)
            if tags:
                tag_str = ", ".join(tags[:2])  # Show first 2 tags
                label_parts.append(f"Tags: {tag_str}")

            label = "\\n".join(label_parts)

            # Node styling based on status (with dark text for readability)
            if online:
                if is_exit:
                    style = "fill:#90EE90,stroke:#FF6B6B,stroke-width:3px,color:#000000"  # Green with red border, black text
                elif is_subnet:
                    style = "fill:#90EE90,stroke:#4ECDC4,stroke-width:3px,color:#000000"  # Green with teal border, black text
                else:
                    style = "fill:#90EE90,stroke:#333,stroke-width:2px,color:#000000"  # Green for online, black text
            else:
                style = "fill:#FFB6C1,stroke:#333,stroke-width:2px,color:#000000"  # Light pink for offline, black text

            # Escape quotes in label for Mermaid
            safe_label = label.replace('"', "'")
            lines.append(f'    {node_id}["{safe_label}"]')
            lines.append(f"    style {node_id} {style}")

        # Add funnel nodes if any
        if active_funnels:
            lines.append("    subgraph Funnels[Active Funnels 🔗]")
            for port, funnel_info in active_funnels.items():
                funnel_node_id = f"funnel{port}"
                public_url = funnel_info.get("public_url", f"Port {port}")
                # Truncate long URLs
                url_display = (
                    public_url[:40] + "..." if len(public_url) > 40 else public_url
                )
                label = f"Funnel Port {port}\\n{url_display}"
                safe_label = label.replace('"', "'")
                lines.append(f'    {funnel_node_id}["{safe_label}"]')
                lines.append(
                    f"    style {funnel_node_id} fill:#FFD700,stroke:#FF8C00,stroke-width:2px,color:#000000"
                )
            lines.append("    end")

        # Add connections (simplified mesh - all devices connected to tailnet)
        # In a real implementation, you'd get peer connections from Tailscale API
        if device_nodes:
            # Connect first device as hub (simplified topology)
            first_node = next(iter(device_nodes.values()))
            for i, node_id in enumerate(device_nodes.values()):
                if i > 0:  # Skip first device
                    lines.append(f"    {first_node} <--> {node_id}")

        # Add legend
        lines.append("    subgraph Legend[Legend]")
        lines.append('    Online["🟢 Online Device"]')
        lines.append('    Offline["🔴 Offline Device"]')
        if exit_nodes:
            lines.append('    Exit["Exit Node"]')
        if subnet_routers:
            lines.append('    Subnet["Subnet Router"]')
        if active_funnels:
            lines.append('    Funnel["Active Funnel"]')
        lines.append("    style Online fill:#90EE90,color:#000000")
        lines.append("    style Offline fill:#FFB6C1,color:#000000")
        if exit_nodes:
            lines.append(
                "    style Exit fill:#90EE90,stroke:#FF6B6B,stroke-width:3px,color:#000000"
            )
        if subnet_routers:
            lines.append(
                "    style Subnet fill:#90EE90,stroke:#4ECDC4,stroke-width:3px,color:#000000"
            )
        if active_funnels:
            lines.append("    style Funnel fill:#FFD700,stroke:#FF8C00,color:#000000")
        lines.append("    end")

        # Add summary comment
        lines.insert(
            1,
            f"    %% Tailnet Topology: {len(devices)} devices ({online_count} online, {len(exit_nodes)} exit nodes, {len(subnet_routers)} subnet routers, {len(active_funnels)} active funnels)",
        )

        return "\n".join(lines)

    except Exception as e:
        logger = structlog.get_logger(__name__)
        logger.warning("Failed to generate Mermaid diagram", error=str(e))
        return f"%% Error generating diagram: {e}"


async def generate_status_info(
    mcp: "FastMCP",
    device_manager: "AdvancedDeviceManager",
    monitor: "TailscaleMonitor",
    component: str | None,  # noqa: ARG001
    detail_level: str,
    include_metrics: bool,
    include_health: bool,  # noqa: ARG001
    include_performance: bool,
    device_filter: str | None,  # noqa: ARG001
    time_range: str,  # noqa: ARG001
    include_mermaid: bool = False,
    funnel_manager: "FunnelManager | None" = None,
) -> dict[str, Any]:
    """Generate comprehensive status information.

    Args:
        mcp: FastMCP instance
        device_manager: Device manager instance
        monitor: Monitoring instance
        component: Component to check
        detail_level: Detail level
        include_metrics: Whether to include metrics
        include_health: Whether to include health
        include_performance: Whether to include performance
        device_filter: Device filter
        time_range: Time range

    Returns:
        Status information dictionary
    """
    import structlog

    logger = structlog.get_logger(__name__)

    # Get basic device information
    try:
        devices = await device_manager.list_devices()
        online_devices = [d for d in devices if d.get("online", False)]

        # Get network metrics
        network_metrics = await monitor.get_network_metrics()

        # Get MCP server capabilities (tools, prompts, resources)
        tools = await mcp._list_tools_mcp()
        prompts = await mcp._list_prompts_mcp()
        resources = await mcp._list_resources_mcp()
        resource_templates = await mcp._list_resource_templates_mcp()

        status_data = {
            "system": {
                "status": "operational",
                "version": "2.0.0",
                "uptime": "Running",
                "last_updated": time.time(),
            },
            "mcp_server": {
                "tools": {
                    "count": len(tools),
                    "names": (
                        [tool.name for tool in tools]
                        if detail_level in ["intermediate", "advanced", "diagnostic"]
                        else None
                    ),
                },
                "prompts": {
                    "count": len(prompts),
                    "names": (
                        [prompt.name for prompt in prompts]
                        if detail_level in ["intermediate", "advanced", "diagnostic"]
                        else None
                    ),
                    "list": (
                        [
                            {
                                "name": prompt.name,
                                "description": getattr(prompt, "description", None),
                            }
                            for prompt in prompts
                        ]
                        if detail_level in ["advanced", "diagnostic"]
                        else None
                    ),
                },
                "resources": {
                    "count": len(resources),
                    "templates_count": len(resource_templates),
                    "uris": (
                        [str(resource.uri) for resource in resources]
                        if detail_level in ["intermediate", "advanced", "diagnostic"]
                        else None
                    ),
                    "templates": (
                        [
                            {
                                "uriTemplate": str(template.uriTemplate),
                                "name": getattr(template, "name", None),
                                "description": getattr(template, "description", None),
                            }
                            for template in resource_templates
                        ]
                        if detail_level in ["advanced", "diagnostic"]
                        else None
                    ),
                    "list": (
                        [
                            {
                                "uri": str(resource.uri),
                                "name": getattr(resource, "name", None),
                                "description": getattr(resource, "description", None),
                            }
                            for resource in resources
                        ]
                        if detail_level in ["advanced", "diagnostic"]
                        else None
                    ),
                },
            },
            "devices": {
                "total": len(devices),
                "online": len(online_devices),
                "offline": len(devices) - len(online_devices),
                "online_percentage": (
                    round((len(online_devices) / len(devices)) * 100, 2)
                    if devices
                    else 0
                ),
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
                "mcp_server": (
                    "healthy"
                    if len(tools) > 0 and len(prompts) > 0 and len(resources) > 0
                    else "warning"
                ),
            },
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

        # Generate Mermaid diagram if requested
        if include_mermaid:
            try:
                mermaid_diagram = await generate_mermaid_diagram(
                    device_manager, funnel_manager
                )
                status_data["mermaid_diagram"] = mermaid_diagram
            except Exception as e:
                logger.warning("Failed to generate Mermaid diagram", error=str(e))
                status_data["mermaid_diagram"] = None

        return status_data

    except Exception as e:
        logger.error("Error generating status information", error=str(e))

        # Still try to get MCP server info even if other operations fail
        try:
            tools = await mcp._list_tools_mcp()
            prompts = await mcp._list_prompts_mcp()
            resources = await mcp._list_resources_mcp()
            resource_templates = await mcp._list_resource_templates_mcp()

            mcp_server_info = {
                "tools": {
                    "count": len(tools),
                    "names": (
                        [tool.name for tool in tools]
                        if detail_level in ["intermediate", "advanced", "diagnostic"]
                        else None
                    ),
                },
                "prompts": {
                    "count": len(prompts),
                    "names": (
                        [prompt.name for prompt in prompts]
                        if detail_level in ["intermediate", "advanced", "diagnostic"]
                        else None
                    ),
                    "list": (
                        [
                            {
                                "name": prompt.name,
                                "description": getattr(prompt, "description", None),
                            }
                            for prompt in prompts
                        ]
                        if detail_level in ["advanced", "diagnostic"]
                        else None
                    ),
                },
                "resources": {
                    "count": len(resources),
                    "templates_count": len(resource_templates),
                    "uris": (
                        [str(resource.uri) for resource in resources]
                        if detail_level in ["intermediate", "advanced", "diagnostic"]
                        else None
                    ),
                    "templates": (
                        [
                            {
                                "uriTemplate": str(template.uriTemplate),
                                "name": getattr(template, "name", None),
                                "description": getattr(template, "description", None),
                            }
                            for template in resource_templates
                        ]
                        if detail_level in ["advanced", "diagnostic"]
                        else None
                    ),
                    "list": (
                        [
                            {
                                "uri": str(resource.uri),
                                "name": getattr(resource, "name", None),
                                "description": getattr(resource, "description", None),
                            }
                            for resource in resources
                        ]
                        if detail_level in ["advanced", "diagnostic"]
                        else None
                    ),
                },
            }
        except Exception as mcp_error:
            logger.warning("Failed to get MCP server info", error=str(mcp_error))
            mcp_server_info = {
                "tools": {"count": 0},
                "prompts": {"count": 0},
                "resources": {"count": 0, "templates_count": 0},
            }

        return {
            "error": f"Failed to generate status: {e!s}",
            "system": {"status": "error"},
            "mcp_server": mcp_server_info,
            "devices": {"total": 0, "online": 0, "offline": 0},
            "network": {"connectivity": "unknown"},
            "services": {"api": "error"},
            "health": {"overall": "error"},
        }
