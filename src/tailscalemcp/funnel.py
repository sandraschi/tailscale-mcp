"""
Tailscale Funnel Module

Provides comprehensive Funnel functionality for exposing local services
to the public internet securely via HTTPS with automatic TLS certificates.
"""

import time
from typing import Any

import structlog
from pydantic import BaseModel, Field

from .exceptions import TailscaleMCPError
from .utils.tailscale_cli import TailscaleCLI

logger = structlog.get_logger(__name__)


class FunnelService(BaseModel):
    """Funnel service model."""

    port: int = Field(..., description="Port number")
    public_url: str | None = Field(None, description="Public HTTPS URL")
    tcp_enabled: bool = Field(True, description="TCP connections enabled")
    tls_enabled: bool = Field(True, description="TLS connections enabled")
    status: str = Field("active", description="Service status")
    created_at: float = Field(..., description="Creation timestamp")
    expires_at: float | None = Field(None, description="Expiration timestamp")


class FunnelManager:
    """Comprehensive Tailscale Funnel manager with persistent storage support."""

    def __init__(
        self,
        use_cli: bool = True,
        tailscale_binary: str | None = None,
        mcp_storage: Any = None,
    ):
        """Initialize Funnel manager.

        Args:
            use_cli: Use real Tailscale CLI for Funnel operations (default: True)
            tailscale_binary: Path to tailscale binary (default: auto-detect)
            mcp_storage: FastMCP storage instance for persistence (optional)
        """
        self.services: dict[int, FunnelService] = {}
        self.use_cli = use_cli
        self.mcp_storage = mcp_storage

        # Initialize CLI if enabled
        if self.use_cli:
            try:
                self.cli = TailscaleCLI(tailscale_binary=tailscale_binary)
                logger.info("Funnel manager using Tailscale CLI", cli_available=True)
            except Exception as e:
                logger.warning(
                    "Tailscale CLI not available, Funnel operations will fail",
                    error=str(e),
                )
                self.use_cli = False
                self.cli = None
        else:
            self.cli = None

        logger.info("Funnel manager initialized", use_cli=self.use_cli)

    async def _save_services_to_storage(self) -> None:
        """Save active services to persistent storage."""
        if not self.mcp_storage:
            return
        try:
            services_data = {
                port: service.model_dump() for port, service in self.services.items()
            }
            await self.mcp_storage.set("tailscale:active_funnels", services_data)
        except Exception as e:
            logger.warning("Failed to save funnels to storage", error=str(e))

    async def _load_services_from_storage(self) -> None:
        """Load active services from persistent storage."""
        if not self.mcp_storage:
            return
        try:
            services_data = await self.mcp_storage.get("tailscale:active_funnels")
            if services_data:
                self.services = {
                    int(port): FunnelService(**data)
                    for port, data in services_data.items()
                }
                logger.info("Loaded funnels from storage", count=len(self.services))
        except Exception as e:
            logger.warning("Failed to load funnels from storage", error=str(e))

    async def enable_funnel(
        self,
        port: int,
        allow_tcp: bool = True,
        allow_tls: bool = True,
    ) -> dict[str, Any]:
        """Enable Funnel for a port.

        Args:
            port: Port number to expose
            allow_tcp: Allow TCP connections (default: True)
            allow_tls: Allow TLS connections (default: True)

        Returns:
            Funnel enable result with public URL
        """
        try:
            if not self.use_cli or not self.cli:
                raise TailscaleMCPError(
                    "Tailscale CLI not available. Install Tailscale CLI to use Funnel."
                )

            if port < 1 or port > 65535:
                raise ValueError(f"Invalid port number: {port} (must be 1-65535)")

            logger.info("Enabling Funnel", port=port, tcp=allow_tcp, tls=allow_tls)

            # Use CLI to enable Funnel
            cli_result = await self.cli.funnel_enable(
                port=port, allow_tcp=allow_tcp, allow_tls=allow_tls
            )

            if cli_result.get("success"):
                public_url = cli_result.get("public_url")
                output = cli_result.get("output", "")

                # Save to persistent storage if available
                if self.mcp_storage:
                    try:
                        await self._save_services_to_storage()
                    except Exception as e:
                        logger.warning(
                            "Failed to save funnels to storage", error=str(e)
                        )

                # Parse public URL from output if not directly provided
                if not public_url and output:
                    for line in output.split("\n"):
                        if "https://" in line:
                            # Extract URL from line
                            parts = line.split()
                            for part in parts:
                                if part.startswith("https://"):
                                    public_url = part.strip()
                                    break

                # Create service record
                service = FunnelService(
                    port=port,
                    public_url=public_url,
                    tcp_enabled=allow_tcp,
                    tls_enabled=allow_tls,
                    status="active",
                    created_at=time.time(),
                )

                self.services[port] = service

                # Save to persistent storage if available (FastMCP 2.13+)
                if self.mcp_storage:
                    try:
                        await self._save_services_to_storage()
                    except Exception as e:
                        logger.warning(
                            "Failed to save funnels to storage", error=str(e)
                        )

                logger.info(
                    "Funnel enabled successfully",
                    port=port,
                    public_url=public_url,
                )

                return {
                    "success": True,
                    "port": port,
                    "public_url": public_url,
                    "tcp_enabled": allow_tcp,
                    "tls_enabled": allow_tls,
                    "status": "active",
                    "output": output,
                    "message": f"Funnel enabled for port {port}",
                }
            else:
                error_msg = cli_result.get("error", "Unknown error")
                logger.error("Failed to enable Funnel", port=port, error=error_msg)
                raise TailscaleMCPError(f"Failed to enable Funnel: {error_msg}")

        except TailscaleMCPError:
            raise
        except Exception as e:
            logger.error("Error enabling Funnel", port=port, error=str(e))
            raise TailscaleMCPError(f"Failed to enable Funnel: {e}") from e

    async def disable_funnel(self, port: int | None = None) -> dict[str, Any]:
        """Disable Funnel.

        Args:
            port: Optional specific port to disable (disables all if None)

        Returns:
            Funnel disable result
        """
        try:
            if not self.use_cli or not self.cli:
                raise TailscaleMCPError(
                    "Tailscale CLI not available. Install Tailscale CLI to use Funnel."
                )

            logger.info("Disabling Funnel", port=port)

            # Use CLI to disable Funnel
            cli_result = await self.cli.funnel_disable(port=port)

            if cli_result.get("success"):
                # Update service records
                if port:
                    if port in self.services:
                        self.services[port].status = "disabled"
                else:
                    # Disable all services
                    for service in self.services.values():
                        service.status = "disabled"

                # Save to persistent storage if available (FastMCP 2.13+)
                if self.mcp_storage:
                    try:
                        await self._save_services_to_storage()
                    except Exception as e:
                        logger.warning(
                            "Failed to save funnels to storage", error=str(e)
                        )

                logger.info("Funnel disabled successfully", port=port)

                return {
                    "success": True,
                    "port": port,
                    "status": "disabled",
                    "output": cli_result.get("output", ""),
                    "message": f"Funnel disabled for port {port}"
                    if port
                    else "All Funnels disabled",
                }
            else:
                error_msg = cli_result.get("error", "Unknown error")
                logger.error("Failed to disable Funnel", port=port, error=error_msg)
                raise TailscaleMCPError(f"Failed to disable Funnel: {error_msg}")

        except TailscaleMCPError:
            raise
        except Exception as e:
            logger.error("Error disabling Funnel", port=port, error=str(e))
            raise TailscaleMCPError(f"Failed to disable Funnel: {e}") from e

    async def get_funnel_status(self) -> dict[str, Any]:
        """Get Funnel status.

        Returns:
            Funnel status information
        """
        try:
            if not self.use_cli or not self.cli:
                # Return local service status if CLI not available
                return {
                    "active": len(
                        [s for s in self.services.values() if s.status == "active"]
                    )
                    > 0,
                    "services": [
                        {
                            "port": s.port,
                            "public_url": s.public_url,
                            "status": s.status,
                            "tcp_enabled": s.tcp_enabled,
                            "tls_enabled": s.tls_enabled,
                        }
                        for s in self.services.values()
                    ],
                    "note": "CLI not available, showing local service records only",
                }

            # Use CLI to get Funnel status
            cli_result = await self.cli.funnel_status()

            # Update local service records based on CLI status
            if isinstance(cli_result, dict):
                active = cli_result.get("active", False)
                funnels = cli_result.get("funnels", [])

                # Update local records
                for funnel_info in funnels:
                    if isinstance(funnel_info, dict):
                        port = funnel_info.get("port")
                        if port:
                            if port not in self.services:
                                self.services[port] = FunnelService(
                                    port=port,
                                    public_url=funnel_info.get("url"),
                                    status="active",
                                    created_at=time.time(),
                                )
                            else:
                                self.services[port].status = "active"
                                if funnel_info.get("url"):
                                    self.services[port].public_url = funnel_info.get(
                                        "url"
                                    )

                return {
                    "active": active,
                    "services": [
                        {
                            "port": s.port,
                            "public_url": s.public_url,
                            "status": s.status,
                            "tcp_enabled": s.tcp_enabled,
                            "tls_enabled": s.tls_enabled,
                        }
                        for s in self.services.values()
                        if s.status == "active"
                    ],
                    "cli_output": cli_result,
                }
            else:
                # Fallback for text output
                return {
                    "active": cli_result.get("active", False),
                    "output": cli_result.get("output", ""),
                    "services": [
                        {
                            "port": s.port,
                            "public_url": s.public_url,
                            "status": s.status,
                        }
                        for s in self.services.values()
                        if s.status == "active"
                    ],
                }

        except Exception as e:
            logger.error("Error getting Funnel status", error=str(e))
            raise TailscaleMCPError(f"Failed to get Funnel status: {e}") from e

    async def list_funnels(self) -> list[dict[str, Any]]:
        """List all active Funnels.

        Returns:
            List of active Funnel services
        """
        try:
            status = await self.get_funnel_status()
            return status.get("services", [])

        except Exception as e:
            logger.error("Error listing Funnels", error=str(e))
            raise TailscaleMCPError(f"Failed to list Funnels: {e}") from e

    async def get_certificate_info(self, port: int) -> dict[str, Any]:
        """Get certificate information for a Funnel service.

        Args:
            port: Port number

        Returns:
            Certificate information
        """
        try:
            if port not in self.services:
                raise ValueError(f"Funnel service not found for port {port}")

            service = self.services[port]
            if service.status != "active":
                raise ValueError(f"Funnel service not active for port {port}")

            # Funnel automatically manages certificates, so we return basic info
            return {
                "port": port,
                "public_url": service.public_url,
                "tls_enabled": service.tls_enabled,
                "certificate_managed": True,
                "certificate_provider": "Tailscale Funnel",
                "note": "Funnel automatically manages TLS certificates",
            }

        except Exception as e:
            logger.error("Error getting certificate info", port=port, error=str(e))
            raise TailscaleMCPError(f"Failed to get certificate info: {e}") from e
