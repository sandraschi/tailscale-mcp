"""
Tailscale MCP Server - Main Entry Point

This module provides the command-line interface for the Tailscale MCP server.
"""

import os
import sys

import structlog
from prometheus_client import Info, start_http_server

from . import TailscaleMCPServer, __version__, setup_logging
from .exceptions import ConfigurationError
from .transport import create_argument_parser, resolve_config

logger = structlog.get_logger(__name__)


def validate_config() -> None:
    """Validate configuration from env vars.

    Raises:
        ConfigurationError: If configuration is invalid
    """
    api_key = os.getenv("TAILSCALE_API_KEY")
    tailnet = os.getenv("TAILSCALE_TAILNET")
    if not api_key:
        raise ConfigurationError(
            "Tailscale API key is required. Set TAILSCALE_API_KEY environment variable"
        )
    if not tailnet:
        raise ConfigurationError(
            "Tailnet name is required. Set TAILSCALE_TAILNET environment variable"
        )


def setup_structured_logging(log_level: str, log_file: str) -> None:
    """Setup structured logging with file and stderr output.

    Applies logging config directly (not idempotent — tests call this directly).
    """
    import logging as _logging
    import sys
    from pathlib import Path

    level = (log_level or "INFO").upper()
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    file_handler = _logging.FileHandler(log_file)
    file_handler.setFormatter(_logging.Formatter("%(message)s"))

    stderr_handler = _logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(_logging.Formatter("%(message)s"))

    root_logger = _logging.getLogger()
    root_logger.setLevel(getattr(_logging, level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stderr_handler)


def setup_prometheus_metrics(port: int) -> None:
    """Setup Prometheus metrics."""
    # Start Prometheus metrics server
    start_http_server(port)

    # Create application info metric
    app_info = Info("tailscale_mcp_info", "Application information")
    app_info.info({"version": __version__, "name": "tailscale-mcp-server"})


def run_server() -> None:
    """Run the Tailscale MCP server using the transport module (stdio/http/sse)."""
    parser = create_argument_parser("tailscale-mcp")
    parser.add_argument(
        "--prometheus-port",
        type=int,
        default=int(os.getenv("PROMETHEUS_PORT", "9091")),
        help="Prometheus metrics port (default: 9091)",
    )
    args = parser.parse_args()

    # Setup structured logging
    setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))

    # Setup Prometheus metrics
    setup_prometheus_metrics(args.prometheus_port)

    # Validate configuration
    validate_config()

    # Create server instance
    server = TailscaleMCPServer()

    # Start the server via transport module (handles --http, --stdio, MCP_TRANSPORT env)
    from .transport import run_server as run_transport_server

    run_transport_server(server.mcp, args, server_name="Tailscale Network Controller MCP")


def main() -> None:
    """Main entry point."""
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.exception("Unexpected error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
