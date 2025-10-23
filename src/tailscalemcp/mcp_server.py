"""
Tailscale MCP Server

A FastMCP 2.12 compliant server for managing Tailscale networks with comprehensive features.
Organized in a modular structure with tools separated by category.
"""

import os

import structlog
from fastmcp import FastMCP

from .device_management import AdvancedDeviceManager
from .grafana_dashboard import TailscaleGrafanaDashboard
from .magic_dns import MagicDNSManager
from .monitoring import TailscaleMonitor
from .taildrop import TaildropManager
from .tools import TailscalePortmanteauTools

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class TailscaleMCPServer:
    """FastMCP 2.12 compliant Tailscale network controller server."""

    def __init__(self, api_key: str | None = None, tailnet: str | None = None):
        """Initialize the Tailscale MCP server.

        Args:
            api_key: Tailscale API key (default: from TAILSCALE_API_KEY env var)
            tailnet: Tailnet name (default: from TAILSCALE_TAILNET env var)
        """
        self.api_key = api_key or os.getenv("TAILSCALE_API_KEY")
        self.tailnet = tailnet or os.getenv("TAILSCALE_TAILNET")

        # Initialize FastMCP
        self.mcp = FastMCP("Tailscale Network Controller MCP")

        # Initialize managers
        self.monitor = TailscaleMonitor(api_key=self.api_key, tailnet=self.tailnet)
        self.grafana_dashboard = TailscaleGrafanaDashboard(self.tailnet or "default")
        self.taildrop_manager = TaildropManager()
        self.device_manager = AdvancedDeviceManager(
            api_key=self.api_key, tailnet=self.tailnet
        )
        self.magic_dns_manager = MagicDNSManager(tailnet=self.tailnet or "default")

        # Initialize portmanteau tools
        self._initialize_portmanteau_tools()

        logger.info("Tailscale MCP Server initialized", tailnet=self.tailnet)

    def _initialize_portmanteau_tools(self) -> None:
        """Initialize portmanteau tools."""
        self.portmanteau_tools = TailscalePortmanteauTools(
            self.mcp,
            self.device_manager,
            self.monitor,
            self.grafana_dashboard,
            self.taildrop_manager,
            self.magic_dns_manager,
        )

        logger.info("Portmanteau tools initialized successfully")

    async def start(self) -> None:
        """Start the MCP server."""
        logger.info("Starting Tailscale MCP server")
        await self.mcp.run()

    async def stop(self) -> None:
        """Stop the MCP server."""
        logger.info("Stopping Tailscale MCP server")
        # FastMCP 2.12 handles shutdown automatically

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Server instance for direct execution
server = TailscaleMCPServer()


async def main():
    """Main entry point for the MCP server."""
    async with server:
        # Server will run until interrupted
        pass


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
