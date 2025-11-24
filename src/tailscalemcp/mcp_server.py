"""
Tailscale MCP Server

A FastMCP 2.13+ compliant server for managing Tailscale networks with comprehensive features.
Organized in a modular structure with tools separated by category.
Features persistent storage for funnels, transfers, and user preferences.
"""

import os
import platform
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import structlog
from dotenv import load_dotenv
from fastmcp import FastMCP

# Try to import DiskStore for persistent storage
try:
    from key_value.aio.stores.disk import DiskStore

    DISK_STORE_AVAILABLE = True
except ImportError:
    DISK_STORE_AVAILABLE = False
    DiskStore = None

from .device_management import AdvancedDeviceManager
from .funnel import FunnelManager
from .grafana_dashboard import TailscaleGrafanaDashboard
from .magic_dns import MagicDNSManager
from .monitoring import TailscaleMonitor
from .taildrop import TaildropManager
from .tools import TailscalePortmanteauTools

# Load .env file if it exists (after imports to avoid E402)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Also try loading from current directory
    load_dotenv()

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


def create_server_lifespan(_api_key: str | None, tailnet: str | None):
    """Create server lifespan for FastMCP 2.13+.

    Args:
        api_key: Tailscale API key
        tailnet: Tailnet name

    Returns:
        Server lifespan context manager
    """

    @asynccontextmanager
    async def server_lifespan(mcp_instance: FastMCP):
        """Server lifespan for startup and cleanup."""
        # ========== STARTUP ==========
        logger.info("Tailscale MCP Server starting up", tailnet=tailnet)

        # Store startup time (if storage is available)
        # Note: FastMCP 2.13+ storage may not be available in all contexts
        # We make it optional to allow the server to run without persistence
        try:
            storage = getattr(mcp_instance, "storage", None)
            if storage is not None:
                try:
                    await storage.set("tailscale:startup_time", time.time())
                    await storage.set("tailscale:server_started", True)
                    logger.info("Persistent storage initialized")
                except AttributeError:
                    # Storage object exists but doesn't have set method
                    logger.debug("Storage object found but methods not available")
            else:
                logger.debug(
                    "Persistent storage not available - continuing without persistence"
                )
        except Exception as e:
            logger.debug("Storage initialization skipped", error=str(e))

        # Store storage reference for managers (will be set after server init)
        # Note: Managers are initialized before lifespan, so we'll update them here
        # For now, storage will be accessed through mcp_instance.storage in tools

        yield  # Server runs here

        # ========== SHUTDOWN ==========
        logger.info("Tailscale MCP Server shutting down")

        # Save state to persistent storage (optional)
        try:
            storage = getattr(mcp_instance, "storage", None)
            if storage is not None:
                try:
                    # Save funnels (if manager has storage access)
                    # Note: Managers will save their state through tool operations

                    # Save server state
                    await storage.set("tailscale:last_shutdown", time.time())
                    await storage.set("tailscale:server_started", False)
                    logger.info("State saved to persistent storage")
                except AttributeError:
                    logger.debug("Storage methods not available - skipping state save")
            else:
                logger.debug("Persistent storage not available - skipping state save")
        except Exception as e:
            logger.debug("State save skipped", error=str(e))

    return server_lifespan


class TailscaleMCPServer:
    """FastMCP 2.13+ compliant Tailscale network controller server with persistent storage."""

    def __init__(self, api_key: str | None = None, tailnet: str | None = None):
        """Initialize the Tailscale MCP server.

        Args:
            api_key: Tailscale API key (default: from TAILSCALE_API_KEY env var)
            tailnet: Tailnet name (default: from TAILSCALE_TAILNET env var)
        """
        self.api_key = api_key or os.getenv("TAILSCALE_API_KEY")
        self.tailnet = tailnet or os.getenv("TAILSCALE_TAILNET")

        # Log configuration (but not the actual API key for security)
        if self.api_key:
            api_key_preview = (
                f"{self.api_key[:20]}..." if len(self.api_key) > 20 else "set"
            )
            logger.info(
                "API credentials loaded",
                api_key_preview=api_key_preview,
                tailnet=self.tailnet,
            )
        else:
            logger.error(
                "No API credentials found! Check user_config or environment variables"
            )

        # Initialize FastMCP with server lifespan (2.13+ feature)
        lifespan = create_server_lifespan(self.api_key, self.tailnet)
        self.mcp = FastMCP("Tailscale Network Controller MCP", lifespan=lifespan)

        # Configure DiskStore for persistent storage (if available)
        # FastMCP may provide its own storage, but we'll use DiskStore directly for guaranteed persistence
        self._disk_storage = None
        if DISK_STORE_AVAILABLE:
            try:
                # Get platform-appropriate storage directory
                if os.name == "nt":  # Windows
                    appdata = os.getenv(
                        "APPDATA", os.path.expanduser("~\\AppData\\Roaming")
                    )
                    storage_dir = Path(appdata) / "Tailscale Network Controller MCP"
                else:  # macOS/Linux
                    home = Path.home()
                    if platform.system() == "Darwin":  # macOS
                        storage_dir = (
                            home
                            / "Library"
                            / "Application Support"
                            / "Tailscale Network Controller MCP"
                        )
                    else:  # Linux
                        storage_dir = (
                            home
                            / ".local"
                            / "share"
                            / "Tailscale Network Controller MCP"
                        )

                # Create directory if it doesn't exist
                storage_dir.mkdir(parents=True, exist_ok=True)

                # Initialize DiskStore
                self._disk_storage = DiskStore(directory=str(storage_dir))
                logger.info("DiskStore initialized", storage_dir=str(storage_dir))

                # Try to set it on mcp.storage if FastMCP supports it
                # If not, we'll use _disk_storage directly in managers
                try:
                    if hasattr(self.mcp, "storage"):
                        self.mcp.storage = self._disk_storage
                        logger.info("DiskStore assigned to mcp.storage")
                except Exception:
                    logger.debug(
                        "Could not assign DiskStore to mcp.storage, will use directly"
                    )
            except Exception as e:
                logger.warning(
                    "Failed to initialize DiskStore, using default storage",
                    error=str(e),
                )
                self._disk_storage = None

        # Initialize managers with storage reference
        self.monitor = TailscaleMonitor(api_key=self.api_key, tailnet=self.tailnet)
        self.grafana_dashboard = TailscaleGrafanaDashboard(self.tailnet or "default")
        self.taildrop_manager = TaildropManager(use_cli=True)

        # Use DiskStore if available, otherwise try mcp.storage, otherwise None
        storage_for_managers = self._disk_storage
        if storage_for_managers is None:
            storage_for_managers = getattr(self.mcp, "storage", None)

        # Initialize funnel manager with storage
        self.funnel_manager = FunnelManager(
            use_cli=True, mcp_storage=storage_for_managers
        )

        self.device_manager = AdvancedDeviceManager(
            api_key=self.api_key, tailnet=self.tailnet
        )
        self.magic_dns_manager = MagicDNSManager(tailnet=self.tailnet or "default")

        if storage_for_managers:
            logger.debug(
                "Storage reference set on managers",
                storage_type=type(storage_for_managers).__name__,
            )

        # Initialize portmanteau tools
        self._initialize_portmanteau_tools()

        # Initialize prompts and resources directly (like tools)
        self._register_prompts_and_resources()

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
            self.funnel_manager,
        )

        logger.info("Portmanteau tools initialized successfully")

    def _register_prompts_and_resources(self) -> None:
        """Register prompts and resources directly on mcp instance (like tools)."""

        # Register prompts
        @self.mcp.prompt()
        def list_devices_prompt(
            online_only: bool = False, filter_tags: list[str] | None = None
        ) -> list[dict[str, Any]]:
            """List all devices in the Tailscale tailnet."""
            tags_str = f" with tags {', '.join(filter_tags)}" if filter_tags else ""
            online_str = "online " if online_only else ""
            query = f"List all {online_str}devices{tags_str} in the tailnet"
            return [{"role": "user", "content": query}]

        @self.mcp.prompt()
        def get_device_details_prompt(device_id: str) -> list[dict[str, Any]]:
            """Get detailed information about a specific device."""
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
            """Authorize a device to join the Tailscale tailnet."""
            reason_str = f" (reason: {reason})" if reason else ""
            return [
                {"role": "user", "content": f"Authorize device {device_id}{reason_str}"}
            ]

        @self.mcp.prompt()
        def check_network_status_prompt() -> list[dict[str, Any]]:
            """Check the overall network status and health."""
            return [
                {
                    "role": "user",
                    "content": "Show me the current network status and health",
                }
            ]

        @self.mcp.prompt()
        def create_security_report_prompt() -> list[dict[str, Any]]:
            """Generate a comprehensive security report."""
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
            """Create a backup of the Tailscale configuration."""
            name_str = f" named {backup_name}" if backup_name else ""
            return [
                {
                    "role": "user",
                    "content": f"Create a backup of the Tailscale configuration{name_str}",
                }
            ]

        # Register resources
        @self.mcp.resource("tailscale://devices")
        async def devices_resource() -> str:
            """List all devices in the tailnet."""
            import json

            devices = await self.device_manager.list_devices()
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
            """Get details for a specific device."""
            import json

            device = await self.device_manager.get_device(device_id)
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
            """Get current network status."""
            import json

            status = await self.monitor.get_network_status()
            return json.dumps(
                {"status": status, "resource": "tailscale://network/status"}, indent=2
            )

        @self.mcp.resource("tailscale://network/topology")
        async def network_topology_resource() -> str:
            """Get network topology map."""
            import json

            topology = await self.monitor.generate_network_topology()
            return json.dumps(
                {"topology": topology, "resource": "tailscale://network/topology"},
                indent=2,
            )

        @self.mcp.resource("tailscale://security/report")
        async def security_report_resource() -> str:
            """Get security report."""
            import json

            report = await self.device_manager.generate_security_report()
            return json.dumps(
                {"report": report, "resource": "tailscale://security/report"}, indent=2
            )

        @self.mcp.resource("tailscale://monitoring/metrics")
        async def metrics_resource() -> str:
            """Get Prometheus-formatted metrics."""
            metrics = await self.monitor.get_prometheus_metrics()
            return metrics

        @self.mcp.resource("tailscale://monitoring/health")
        async def health_resource() -> str:
            """Get network health report."""
            import json

            health = await self.monitor.get_network_health_report()
            return json.dumps(
                {"health": health, "resource": "tailscale://monitoring/health"},
                indent=2,
            )

        # Store references to prevent garbage collection
        self._prompt_refs = [
            list_devices_prompt,
            get_device_details_prompt,
            authorize_device_prompt,
            check_network_status_prompt,
            create_security_report_prompt,
            backup_configuration_prompt,
        ]
        self._resource_refs = [
            devices_resource,
            device_resource,
            network_status_resource,
            network_topology_resource,
            security_report_resource,
            metrics_resource,
            health_resource,
        ]

        # Verify actual registration by checking FastMCP's internal state
        # Note: This is async, so we can't call it in __init__, but we log what we registered
        logger.info(
            "Prompts and resources registered successfully",
            prompts_registered=len(self._prompt_refs),
            resources_registered=len(self._resource_refs),
            note="These are registered via FastMCP decorators for direct MCP protocol usage (Cursor, Windsurf, etc.)",
        )

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
