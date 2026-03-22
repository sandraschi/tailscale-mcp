"""
TailscaleMCP - A FastMCP 3.1+ Tailscale controller

This module provides an MCP server for managing Tailscale networks,
including device management, access control, and network monitoring.
"""

from .version import __version__

__author__ = "Sandra Schi <sandra@sandraschi.dev>"
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
    "__version__",
    "get_server",
    "server",
]
