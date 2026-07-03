"""
MagicDNS and Advanced Networking Module

Provides comprehensive MagicDNS configuration, custom DNS management,
and advanced networking features for Tailscale networks.
"""

import time
from typing import Any

import structlog
from pydantic import BaseModel, Field

from .client.api_client import TailscaleAPIClient
from .exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class DNSRecord(BaseModel):
    """DNS record model."""

    name: str = Field(..., description="DNS record name")
    type: str = Field(..., description="DNS record type (A, AAAA, CNAME, TXT)")
    value: str = Field(..., description="DNS record value")
    ttl: int = Field(default=3600, description="Time to live in seconds")
    created_at: float = Field(..., description="Record creation timestamp")
    updated_at: float = Field(..., description="Record last update timestamp")


class MagicDNSConfig(BaseModel):
    """MagicDNS configuration model."""

    enabled: bool = Field(default=True, description="MagicDNS enabled status")
    base_domain: str = Field(..., description="Base domain for MagicDNS")
    custom_records: list[DNSRecord] = Field(
        default_factory=list, description="Custom DNS records"
    )
    search_domains: list[str] = Field(
        default_factory=list, description="Search domains"
    )
    nameservers: list[str] = Field(
        default_factory=list, description="Custom nameservers"
    )
    override_local_dns: bool = Field(default=False, description="Override local DNS")


class NetworkPolicy(BaseModel):
    """Network policy model."""

    policy_id: str = Field(..., description="Policy identifier")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    rules: list[dict[str, Any]] = Field(..., description="Policy rules")
    enabled: bool = Field(default=True, description="Policy enabled status")
    priority: int = Field(default=100, description="Policy priority")
    created_at: float = Field(..., description="Policy creation timestamp")
    updated_at: float = Field(..., description="Policy last update timestamp")


class MagicDNSManager:
    """Comprehensive MagicDNS and networking manager."""

    def __init__(self, tailnet: str, base_domain: str | None = None):
        """Initialize MagicDNS manager.

        Args:
            tailnet: Tailnet name
            base_domain: Base domain for MagicDNS
        """
        self.tailnet = tailnet
        self.base_domain = base_domain or f"{tailnet}.ts.net"
        self.config = MagicDNSConfig(base_domain=self.base_domain, enabled=True)
        self.dns_records: dict[str, DNSRecord] = {}
        self.network_policies: dict[str, NetworkPolicy] = {}
        self.dns_cache: dict[str, tuple[str, float]] = {}
        self.cache_ttl = 300  # 5 minutes
        self.api_client = TailscaleAPIClient(tailnet=tailnet)

        logger.info(
            "MagicDNS manager initialized",
            tailnet=tailnet,
            base_domain=self.base_domain,
        )

    async def get_dns_configuration(self) -> dict[str, Any]:
        """Fetch DNS configuration from Tailscale Admin API."""
        try:
            cfg = await self.api_client.get_dns_config()
            logger.info("DNS configuration fetched")
            return cfg
        except Exception as e:
            logger.error("Error fetching DNS configuration", error=str(e))
            raise TailscaleMCPError(f"Failed to fetch DNS configuration: {e}") from e

    async def configure_magic_dns(
        self, enabled: bool = True, override_local_dns: bool = False
    ) -> dict[str, Any]:
        """Configure MagicDNS settings.

        Note: MagicDNS toggle is not exposed directly via the public Admin API.
        """
        raise TailscaleMCPError(
            "Configuring MagicDNS enable/disable is not supported via the Tailscale Admin API."
        )

    async def add_dns_record(
        self, name: str, record_type: str, value: str, ttl: int = 3600
    ) -> dict[str, Any]:
        """Add a custom DNS record.

        Args:
            name: DNS record name
            record_type: Record type (A, AAAA, CNAME, TXT)
            value: Record value
            ttl: Time to live in seconds

        Returns:
            DNS record creation result
        """
        raise TailscaleMCPError(
            "Adding custom DNS records is not supported via the Tailscale Admin API."
        )

    async def remove_dns_record(self, name: str, record_type: str) -> dict[str, Any]:
        """Remove a DNS record.

        Args:
            name: DNS record name
            record_type: Record type

        Returns:
            DNS record removal result
        """
        raise TailscaleMCPError(
            "Removing custom DNS records is not supported via the Tailscale Admin API."
        )

    async def list_dns_records(
        self, record_type: str | None = None
    ) -> list[dict[str, Any]]:
        """List DNS records.

        Args:
            record_type: Optional filter by record type

        Returns:
            List of DNS records
        """
        raise TailscaleMCPError(
            "Listing custom DNS records is not supported via the Tailscale Admin API."
        )

    async def resolve_dns(
        self, hostname: str, record_type: str = "A", use_cache: bool = True
    ) -> dict[str, Any]:
        """Resolve DNS hostname.

        Args:
            hostname: Hostname to resolve
            record_type: Record type to resolve
            use_cache: Whether to use DNS cache

        Returns:
            DNS resolution result
        """
        raise TailscaleMCPError(
            "DNS resolution via Admin API is not supported; perform resolution externally."
        )

    async def add_search_domain(self, domain: str) -> dict[str, Any]:
        """Add a search domain.

        Args:
            domain: Domain to add to search list

        Returns:
            Search domain addition result
        """
        raise TailscaleMCPError(
            "Managing search domains is not supported via the Tailscale Admin API."
        )

    async def remove_search_domain(self, domain: str) -> dict[str, Any]:
        """Remove a search domain.

        Args:
            domain: Domain to remove from search list

        Returns:
            Search domain removal result
        """
        raise TailscaleMCPError(
            "Managing search domains is not supported via the Tailscale Admin API."
        )

    async def create_network_policy(
        self,
        policy_name: str,
        rules: list[dict[str, Any]],
        description: str = "",
        priority: int = 100,
    ) -> dict[str, Any]:
        """Create a network policy.

        Args:
            policy_name: Name of the policy
            rules: List of policy rules
            description: Policy description
            priority: Policy priority

        Returns:
            Policy creation result
        """
        raise TailscaleMCPError(
            "Creating/applying custom network policies is not supported via the public Admin API."
        )

    async def apply_network_policy(self, policy_id: str) -> dict[str, Any]:
        """Apply a network policy.

        Args:
            policy_id: Policy ID to apply

        Returns:
            Policy application result
        """
        raise TailscaleMCPError(
            "Applying custom network policies is not supported via the public Admin API."
        )

    async def get_dns_statistics(self) -> dict[str, Any]:
        """Get DNS statistics.

        Returns:
            DNS statistics summary
        """
        # Limited stats with Admin API context only
        try:
            cfg = await self.get_dns_configuration()
            return {
                "magic_dns_enabled": cfg.get("magicDNS"),
                "nameservers": cfg.get("dns", {}).get("nameservers"),
                "base_domain": self.base_domain,
            }
        except Exception as e:
            logger.error("Error getting DNS statistics", error=str(e))
            raise

    async def clear_dns_cache(self) -> dict[str, Any]:
        """Clear DNS cache.

        Returns:
            Cache clearing result
        """
        try:
            cache_size = len(self.dns_cache)
            self.dns_cache.clear()

            logger.info("DNS cache cleared", cache_size=cache_size)

            return {
                "cache_size_before": cache_size,
                "cache_size_after": 0,
                "timestamp": time.time(),
                "message": f"DNS cache cleared ({cache_size} entries removed)",
            }

        except Exception as e:
            logger.error("Error clearing DNS cache", error=str(e))
            raise TailscaleMCPError(f"Failed to clear DNS cache: {e}") from e
