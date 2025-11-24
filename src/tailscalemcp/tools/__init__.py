"""
Tailscale Portmanteau Tools

Modular tool registration system for Tailscale MCP server.
Each tool is in its own module for better maintainability.
"""

from .portmanteau_tools import TailscalePortmanteauTools

__all__ = ["TailscalePortmanteauTools"]
