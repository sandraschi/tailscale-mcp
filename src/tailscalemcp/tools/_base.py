"""
Base utilities for portmanteau tool registration.

Provides shared types and utilities for tool modules.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from tailscalemcp.client.api_client import TailscaleAPIClient
    from tailscalemcp.config import TailscaleConfig
    from tailscalemcp.device_management import AdvancedDeviceManager
    from tailscalemcp.funnel import FunnelManager
    from tailscalemcp.grafana_dashboard import TailscaleGrafanaDashboard
    from tailscalemcp.magic_dns import MagicDNSManager
    from tailscalemcp.monitoring import TailscaleMonitor
    from tailscalemcp.operations.analytics import AnalyticsOperations
    from tailscalemcp.operations.audit import AuditOperations
    from tailscalemcp.operations.keys import KeyOperations
    from tailscalemcp.operations.network import NetworkOperations
    from tailscalemcp.operations.policies import PolicyOperations
    from tailscalemcp.operations.policy_analyzer import PolicyAnalyzer
    from tailscalemcp.operations.reporting import ReportingOperations
    from tailscalemcp.operations.services import ServiceOperations
    from tailscalemcp.operations.tags import TagOperations
    from tailscalemcp.taildrop import TaildropManager


class ToolContext:
    """Context object passed to tool registration functions."""

    def __init__(
        self,
        mcp: "FastMCP",
        device_manager: "AdvancedDeviceManager",
        monitor: "TailscaleMonitor",
        grafana_dashboard: "TailscaleGrafanaDashboard",
        taildrop_manager: "TaildropManager",
        magic_dns_manager: "MagicDNSManager",
        funnel_manager: "FunnelManager | None",
        config: "TailscaleConfig",
        api_client: "TailscaleAPIClient",
        network_ops: "NetworkOperations | None" = None,
        policy_ops: "PolicyOperations | None" = None,
        audit_ops: "AuditOperations | None" = None,
        tag_ops: "TagOperations | None" = None,
        key_ops: "KeyOperations | None" = None,
        policy_analyzer: "PolicyAnalyzer | None" = None,
        analytics_ops: "AnalyticsOperations | None" = None,
        reporting_ops: "ReportingOperations | None" = None,
        service_ops: "ServiceOperations | None" = None,
    ):
        """Initialize tool context.

        Args:
            mcp: FastMCP instance
            device_manager: Device manager instance
            monitor: Monitoring instance
            grafana_dashboard: Grafana dashboard instance
            taildrop_manager: Taildrop manager instance
            magic_dns_manager: MagicDNS manager instance
            funnel_manager: Funnel manager instance
            config: Configuration instance
            network_ops: Network operations instance
            policy_ops: Policy operations instance
            audit_ops: Audit operations instance
            tag_ops: Tag operations instance
            key_ops: Key operations instance
            policy_analyzer: Policy analyzer instance
            analytics_ops: Analytics operations instance
            reporting_ops: Reporting operations instance
            service_ops: Service operations instance
        """
        self.mcp = mcp
        self.device_manager = device_manager
        self.monitor = monitor
        self.grafana_dashboard = grafana_dashboard
        self.taildrop_manager = taildrop_manager
        self.magic_dns_manager = magic_dns_manager
        self.funnel_manager = funnel_manager
        self.config = config
        self.api_client = api_client
        self.network_ops = network_ops
        self.policy_ops = policy_ops
        self.audit_ops = audit_ops
        self.tag_ops = tag_ops
        self.key_ops = key_ops
        self.policy_analyzer = policy_analyzer
        self.analytics_ops = analytics_ops
        self.reporting_ops = reporting_ops
        self.service_ops = service_ops
