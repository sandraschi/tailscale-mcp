"""
Tailscale Portmanteau Tools

Refactored modular tool registration system.
Each tool is in its own module for better maintainability.
"""

import structlog
from fastmcp import FastMCP

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

from ._base import ToolContext
from .automation_tool import register_automation_tool
from .backup_tool import register_backup_tool
from .device_tool import register_device_tool
from .file_tool import register_file_tool
from .funnel_tool import register_funnel_tool
from .help_tool import register_help_tool
from .integration_tool import register_integration_tool
from .monitor_tool import register_monitor_tool
from .network_tool import register_network_tool
from .performance_tool import register_performance_tool
from .reporting_tool import register_reporting_tool
from .sampling_tool import register_sampling_tool
from .security_tool import register_security_tool
from .status_tool import register_status_tool

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
        funnel_manager: FunnelManager | None = None,
        config: TailscaleConfig | None = None,
    ):
        """Initialize portmanteau tools.

        Args:
            mcp: FastMCP instance
            device_manager: Device manager instance
            monitor: Monitoring instance
            grafana_dashboard: Grafana dashboard instance
            taildrop_manager: Taildrop manager instance
            magic_dns_manager: MagicDNS manager instance
            funnel_manager: Funnel manager instance (optional)
        """
        self.mcp = mcp
        self.device_manager = device_manager
        self.monitor = monitor
        self.grafana_dashboard = grafana_dashboard
        self.taildrop_manager = taildrop_manager
        self.magic_dns_manager = magic_dns_manager
        self.funnel_manager = funnel_manager

        # Initialize operations layer - use device_manager config if not provided
        if config is None:
            config = TailscaleConfig(
                tailscale_api_key=device_manager.api_key or "",
                tailscale_tailnet=device_manager.tailnet or "",
            )
        self.config = config

        # Initialize operations classes for use in portmanteau tools
        self.network_ops = NetworkOperations(config=self.config)
        self.policy_ops = PolicyOperations(config=self.config)
        self.audit_ops = AuditOperations(config=self.config)
        self.tag_ops = TagOperations(config=self.config)
        self.key_ops = KeyOperations(config=self.config)
        self.policy_analyzer = PolicyAnalyzer(config=self.config)
        self.analytics_ops = AnalyticsOperations(config=self.config)
        self.reporting_ops = ReportingOperations(config=self.config)
        self.service_ops = ServiceOperations(config=self.config)

        # Create tool context
        self.ctx = ToolContext(
            mcp=mcp,
            device_manager=device_manager,
            monitor=monitor,
            grafana_dashboard=grafana_dashboard,
            taildrop_manager=taildrop_manager,
            magic_dns_manager=magic_dns_manager,
            funnel_manager=funnel_manager,
            config=self.config,
            network_ops=self.network_ops,
            policy_ops=self.policy_ops,
            audit_ops=self.audit_ops,
            tag_ops=self.tag_ops,
            key_ops=self.key_ops,
            policy_analyzer=self.policy_analyzer,
            analytics_ops=self.analytics_ops,
            reporting_ops=self.reporting_ops,
            service_ops=self.service_ops,
        )

        self._register_tools()

    def _register_tools(self) -> None:
        """Register all portmanteau tools from modules."""
        # Register all tools from separate modules
        register_device_tool(self.ctx)
        register_network_tool(self.ctx)
        register_monitor_tool(self.ctx)
        register_file_tool(self.ctx)
        register_funnel_tool(self.ctx)
        register_security_tool(self.ctx)
        register_automation_tool(self.ctx)
        register_backup_tool(self.ctx)
        register_performance_tool(self.ctx)
        register_reporting_tool(self.ctx)
        register_sampling_tool(self.ctx)
        register_integration_tool(self.ctx)
        register_help_tool(self.ctx)
        register_status_tool(self.ctx)

        logger.info("All portmanteau tools registered successfully")
