"""
TailscaleMCP - A FastMCP 2.12 compliant Tailscale controller

This module provides an MCP server for managing Tailscale networks,
including device management, access control, and network monitoring.
"""

__version__ = "2.0.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"

from .exceptions import TailscaleMCPError
from .mcp_server import TailscaleMCPServer

# Create a default server instance for convenience
server = TailscaleMCPServer()


def get_server() -> TailscaleMCPServer:
    """Get the default Tailscale MCP server instance."""
    return server


__all__ = [
    "TailscaleMCPError",
    "TailscaleMCPServer",
    "get_server",
    "server",
]
