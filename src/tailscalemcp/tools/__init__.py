"""
Tailscale MCP Tools Package

Portmanteau tools following the database-mcp pattern to avoid tool explosion.
Each tool combines multiple related operations into a single, powerful interface.
"""

from .portmanteau_tools import TailscalePortmanteauTools

__all__ = ["TailscalePortmanteauTools"]
