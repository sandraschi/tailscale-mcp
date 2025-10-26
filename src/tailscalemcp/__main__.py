"""
Tailscale MCP Server - Main Entry Point

This module provides the command-line interface for the Tailscale MCP server.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import structlog
from prometheus_client import Info, start_http_server

from . import TailscaleMCPServer, __version__
from .exceptions import ConfigurationError

logger = structlog.get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tailscale MCP Server - FastMCP 2.12 compliant Tailscale controller"
    )

    # Server configuration
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("TAILSCALE_API_KEY"),
        help="Tailscale API key (default: from TAILSCALE_API_KEY environment variable)",
    )
    parser.add_argument(
        "--tailnet",
        type=str,
        default=os.getenv("TAILSCALE_TAILNET"),
        help="Tailnet name (default: from TAILSCALE_TAILNET environment variable)",
    )

    # Logging
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="logs/tailscale-mcp.log",
        help="Log file path (default: logs/tailscale-mcp.log)",
    )

    # Monitoring
    parser.add_argument(
        "--prometheus-port",
        type=int,
        default=9091,
        help="Prometheus metrics port (default: 9091)",
    )

    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"Tailscale MCP Server {__version__}",
    )

    return parser.parse_args()


def validate_config(args: argparse.Namespace) -> None:
    """Validate configuration.

    Args:
        args: Parsed command line arguments

    Raises:
        ConfigurationError: If configuration is invalid
    """
    if not args.api_key:
        raise ConfigurationError(
            "Tailscale API key is required. Set TAILSCALE_API_KEY environment variable or use --api-key"
        )

    if not args.tailnet:
        raise ConfigurationError(
            "Tailnet name is required. Set TAILSCALE_TAILNET environment variable or use --tailnet"
        )


def setup_structured_logging(log_level: str, log_file: str) -> None:
    """Setup structured logging with file output for Loki integration."""
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure structlog for JSON output to file
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
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Setup file handler for structured logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    # Setup console handler for human-readable logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def setup_prometheus_metrics(port: int) -> None:
    """Setup Prometheus metrics."""
    # Start Prometheus metrics server
    start_http_server(port)

    # Create application info metric
    app_info = Info("tailscale_mcp_info", "Application information")
    app_info.info({
        "version": __version__,
        "name": "tailscale-mcp-server"
    })


def run_server() -> None:
    """Run the Tailscale MCP server."""
    args = parse_args()

    # Setup structured logging
    setup_structured_logging(args.log_level, args.log_file)

    # Setup Prometheus metrics
    setup_prometheus_metrics(args.prometheus_port)

    # Validate configuration
    try:
        validate_config(args)
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Create server instance
    server = TailscaleMCPServer(api_key=args.api_key, tailnet=args.tailnet)

    # Start the server directly with FastMCP
    try:
        logger.info("Starting Tailscale MCP Server", version=__version__)
        logger.info("Server configuration",
                   host=args.host,
                   port=args.port,
                   tailnet=args.tailnet,
                   prometheus_port=args.prometheus_port,
                   log_file=args.log_file)

        # Run the FastMCP server directly (it handles its own event loop)
        server.mcp.run()

    except Exception as e:
        logger.exception("Error running server", error=str(e))
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
