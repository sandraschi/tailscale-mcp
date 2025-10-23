"""
Tailscale MCP Server - Main Entry Point

This module provides the command-line interface for the Tailscale MCP server.
"""

import argparse
import asyncio
import logging
import os
import signal
import sys

import structlog

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


async def run_server() -> None:
    """Run the Tailscale MCP server."""
    args = parse_args()

    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level)
    )

    # Validate configuration
    try:
        validate_config(args)
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Create server instance
    server = TailscaleMCPServer(api_key=args.api_key, tailnet=args.tailnet)

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler() -> None:
        """Handle shutdown signals."""
        logger.info("Shutdown signal received, stopping server...")
        shutdown_event.set()

    # Register signal handlers (Unix only)
    loop = asyncio.get_running_loop()
    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
    else:
        # On Windows, we'll handle KeyboardInterrupt in the main() function
        pass

    # Start the server
    try:
        logger.info(f"Starting Tailscale MCP Server v{__version__}")
        logger.info(f"Listening on {args.host}:{args.port}")
        logger.info(f"Connected to Tailnet: {args.tailnet}")

        # Start the server directly with FastMCP
        await server.mcp.run()

    except Exception as e:
        logger.exception(f"Error running server: {e}")
        sys.exit(1)
    finally:
        # Clean up
        logger.info("Stopping server...")
        await server.stop()
        logger.info("Server stopped")


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
