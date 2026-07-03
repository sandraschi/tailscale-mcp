"""
TailscaleMCP - A FastMCP 3.2+ Tailscale controller

This module provides an MCP server for managing Tailscale networks,
including device management, access control, and network monitoring.
"""

import logging
import os
import sys
from pathlib import Path

import structlog

from .version import __version__

__author__ = "Sandra Schi <sandra@sandraschi.dev>"
__license__ = "MIT"


_LOG_CONFIGURED = False


def setup_logging(log_level: str | None = None, log_file: str | None = None) -> None:
    """Configure structured logging once (idempotent).

    Args:
        log_level: Logging level string (default: from LOG_LEVEL env or INFO)
        log_file: Path to log file (default: logs/tailscale-mcp.log).
                  Pass empty string to disable file logging.
    """
    global _LOG_CONFIGURED
    if _LOG_CONFIGURED:
        return
    _LOG_CONFIGURED = True

    level = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    if log_file is None:
        log_file = os.getenv("LOG_FILE", "logs/tailscale-mcp.log")
    if log_file:
        from logging.handlers import RotatingFileHandler

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(file_handler)

    if sys.stderr.encoding and sys.stderr.encoding.lower() in ("ascii", "ansi_x3.4-1968"):
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(stderr_handler)


from .exceptions import TailscaleMCPError  # noqa: E402
from .mcp_server import TailscaleMCPServer  # noqa: E402

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
    "setup_logging",
]
