"""
Operations layer for Tailscale MCP.

Provides service layer abstraction between business logic and API client.
"""

from tailscalemcp.operations.analytics import AnalyticsOperations
from tailscalemcp.operations.audit import AuditOperations
from tailscalemcp.operations.devices import DeviceOperations
from tailscalemcp.operations.keys import KeyOperations
from tailscalemcp.operations.network import NetworkOperations
from tailscalemcp.operations.policies import PolicyOperations
from tailscalemcp.operations.policy_analyzer import PolicyAnalyzer
from tailscalemcp.operations.reporting import ReportingOperations
from tailscalemcp.operations.services import ServiceOperations
from tailscalemcp.operations.tags import TagOperations

__all__ = [
    "AnalyticsOperations",
    "AuditOperations",
    "DeviceOperations",
    "KeyOperations",
    "NetworkOperations",
    "PolicyAnalyzer",
    "PolicyOperations",
    "ReportingOperations",
    "ServiceOperations",
    "TagOperations",
]
