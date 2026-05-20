"""
Tailscale API Client — consolidated.

Re-exports the enhanced client with rate limiting and retry.
All code should import from ``tailscalemcp.client.api_client`` directly.
"""

from tailscalemcp.client.api_client import TailscaleAPIClient

__all__ = ["TailscaleAPIClient"]
