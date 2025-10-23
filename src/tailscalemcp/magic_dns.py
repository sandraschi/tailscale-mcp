"""
MagicDNS and Advanced Networking Module

Provides comprehensive MagicDNS configuration, custom DNS management,
and advanced networking features for Tailscale networks.
"""

import time
from typing import Any

import structlog
from pydantic import BaseModel, Field

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

        logger.info(
            "MagicDNS manager initialized",
            tailnet=tailnet,
            base_domain=self.base_domain,
        )

    async def configure_magic_dns(
        self, enabled: bool = True, override_local_dns: bool = False
    ) -> dict[str, Any]:
        """Configure MagicDNS settings.

        Args:
            enabled: Enable or disable MagicDNS
            override_local_dns: Override local DNS settings

        Returns:
            Configuration result
        """
        try:
            self.config.enabled = enabled
            self.config.override_local_dns = override_local_dns

            logger.info(
                "MagicDNS configured",
                enabled=enabled,
                override_local_dns=override_local_dns,
                base_domain=self.base_domain,
            )

            return {
                "enabled": enabled,
                "base_domain": self.base_domain,
                "override_local_dns": override_local_dns,
                "timestamp": time.time(),
                "message": f"MagicDNS {'enabled' if enabled else 'disabled'} for {self.base_domain}",
            }

        except Exception as e:
            logger.error("Error configuring MagicDNS", error=str(e))
            raise TailscaleMCPError(f"Failed to configure MagicDNS: {e}") from e

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
        try:
            # Validate record type
            valid_types = ["A", "AAAA", "CNAME", "TXT", "MX", "SRV"]
            if record_type.upper() not in valid_types:
                raise ValueError(f"Invalid record type: {record_type}")

            # Create DNS record
            record_key = f"{name}:{record_type.upper()}"
            dns_record = DNSRecord(
                name=name,
                type=record_type.upper(),
                value=value,
                ttl=ttl,
                created_at=time.time(),
                updated_at=time.time(),
            )

            self.dns_records[record_key] = dns_record
            self.config.custom_records.append(dns_record)

            # Clear DNS cache for this record
            if record_key in self.dns_cache:
                del self.dns_cache[record_key]

            logger.info(
                "DNS record added",
                name=name,
                type=record_type.upper(),
                value=value,
                ttl=ttl,
            )

            return {
                "name": name,
                "type": record_type.upper(),
                "value": value,
                "ttl": ttl,
                "timestamp": time.time(),
                "message": f"DNS record {name} ({record_type.upper()}) added successfully",
            }

        except Exception as e:
            logger.error("Error adding DNS record", error=str(e))
            raise TailscaleMCPError(f"Failed to add DNS record: {e}") from e

    async def remove_dns_record(self, name: str, record_type: str) -> dict[str, Any]:
        """Remove a DNS record.

        Args:
            name: DNS record name
            record_type: Record type

        Returns:
            DNS record removal result
        """
        try:
            record_key = f"{name}:{record_type.upper()}"

            if record_key not in self.dns_records:
                raise ValueError(f"DNS record not found: {record_key}")

            # Remove from records
            del self.dns_records[record_key]

            # Remove from config
            self.config.custom_records = [
                r
                for r in self.config.custom_records
                if not (r.name == name and r.type == record_type.upper())
            ]

            # Clear DNS cache
            if record_key in self.dns_cache:
                del self.dns_cache[record_key]

            logger.info("DNS record removed", name=name, type=record_type.upper())

            return {
                "name": name,
                "type": record_type.upper(),
                "timestamp": time.time(),
                "message": f"DNS record {name} ({record_type.upper()}) removed successfully",
            }

        except Exception as e:
            logger.error("Error removing DNS record", error=str(e))
            raise TailscaleMCPError(f"Failed to remove DNS record: {e}") from e

    async def list_dns_records(
        self, record_type: str | None = None
    ) -> list[dict[str, Any]]:
        """List DNS records.

        Args:
            record_type: Optional filter by record type

        Returns:
            List of DNS records
        """
        try:
            records = []

            for record in self.dns_records.values():
                if record_type and record.type != record_type.upper():
                    continue

                records.append(
                    {
                        "name": record.name,
                        "type": record.type,
                        "value": record.value,
                        "ttl": record.ttl,
                        "created_at": record.created_at,
                        "updated_at": record.updated_at,
                    }
                )

            logger.info(
                "DNS records listed",
                total_records=len(records),
                filter_type=record_type,
            )

            return records

        except Exception as e:
            logger.error("Error listing DNS records", error=str(e))
            raise TailscaleMCPError(f"Failed to list DNS records: {e}") from e

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
        try:
            record_key = f"{hostname}:{record_type.upper()}"

            # Check cache first
            if use_cache and record_key in self.dns_cache:
                cached_value, cached_time = self.dns_cache[record_key]
                if time.time() - cached_time < self.cache_ttl:
                    return {
                        "hostname": hostname,
                        "type": record_type.upper(),
                        "value": cached_value,
                        "cached": True,
                        "timestamp": cached_time,
                    }

            # Check custom DNS records
            if record_key in self.dns_records:
                record = self.dns_records[record_key]
                self.dns_cache[record_key] = (record.value, time.time())

                return {
                    "hostname": hostname,
                    "type": record_type.upper(),
                    "value": record.value,
                    "cached": False,
                    "source": "custom",
                    "timestamp": time.time(),
                }

            # Simulate MagicDNS resolution
            if hostname.endswith(f".{self.base_domain}"):
                # Extract device name from hostname
                device_name = hostname.replace(f".{self.base_domain}", "")
                # Simulate device IP resolution
                device_ip = (
                    f"100.64.{hash(device_name) % 255}.{(hash(device_name) >> 8) % 255}"
                )

                self.dns_cache[record_key] = (device_ip, time.time())

                return {
                    "hostname": hostname,
                    "type": record_type.upper(),
                    "value": device_ip,
                    "cached": False,
                    "source": "magic_dns",
                    "timestamp": time.time(),
                }

            # No resolution found
            return {
                "hostname": hostname,
                "type": record_type.upper(),
                "value": None,
                "cached": False,
                "source": "not_found",
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error("Error resolving DNS", error=str(e))
            raise TailscaleMCPError(f"Failed to resolve DNS: {e}") from e

    async def add_search_domain(self, domain: str) -> dict[str, Any]:
        """Add a search domain.

        Args:
            domain: Domain to add to search list

        Returns:
            Search domain addition result
        """
        try:
            if domain not in self.config.search_domains:
                self.config.search_domains.append(domain)

            logger.info("Search domain added", domain=domain)

            return {
                "domain": domain,
                "search_domains": self.config.search_domains,
                "timestamp": time.time(),
                "message": f"Search domain {domain} added successfully",
            }

        except Exception as e:
            logger.error("Error adding search domain", error=str(e))
            raise TailscaleMCPError(f"Failed to add search domain: {e}") from e

    async def remove_search_domain(self, domain: str) -> dict[str, Any]:
        """Remove a search domain.

        Args:
            domain: Domain to remove from search list

        Returns:
            Search domain removal result
        """
        try:
            if domain in self.config.search_domains:
                self.config.search_domains.remove(domain)

            logger.info("Search domain removed", domain=domain)

            return {
                "domain": domain,
                "search_domains": self.config.search_domains,
                "timestamp": time.time(),
                "message": f"Search domain {domain} removed successfully",
            }

        except Exception as e:
            logger.error("Error removing search domain", error=str(e))
            raise TailscaleMCPError(f"Failed to remove search domain: {e}") from e

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
        try:
            policy_id = f"policy_{int(time.time())}"

            policy = NetworkPolicy(
                policy_id=policy_id,
                name=policy_name,
                description=description,
                rules=rules,
                priority=priority,
                created_at=time.time(),
                updated_at=time.time(),
            )

            self.network_policies[policy_id] = policy

            logger.info(
                "Network policy created",
                policy_id=policy_id,
                policy_name=policy_name,
                rules_count=len(rules),
            )

            return {
                "policy_id": policy_id,
                "policy_name": policy_name,
                "description": description,
                "rules_count": len(rules),
                "priority": priority,
                "timestamp": time.time(),
                "message": f"Network policy {policy_name} created successfully",
            }

        except Exception as e:
            logger.error("Error creating network policy", error=str(e))
            raise TailscaleMCPError(f"Failed to create network policy: {e}") from e

    async def apply_network_policy(self, policy_id: str) -> dict[str, Any]:
        """Apply a network policy.

        Args:
            policy_id: Policy ID to apply

        Returns:
            Policy application result
        """
        try:
            if policy_id not in self.network_policies:
                raise ValueError(f"Network policy not found: {policy_id}")

            policy = self.network_policies[policy_id]
            policy.enabled = True
            policy.updated_at = time.time()

            logger.info(
                "Network policy applied", policy_id=policy_id, policy_name=policy.name
            )

            return {
                "policy_id": policy_id,
                "policy_name": policy.name,
                "enabled": True,
                "timestamp": time.time(),
                "message": f"Network policy {policy.name} applied successfully",
            }

        except Exception as e:
            logger.error("Error applying network policy", error=str(e))
            raise TailscaleMCPError(f"Failed to apply network policy: {e}") from e

    async def get_dns_statistics(self) -> dict[str, Any]:
        """Get DNS statistics.

        Returns:
            DNS statistics summary
        """
        try:
            total_records = len(self.dns_records)
            record_types = {}

            for record in self.dns_records.values():
                record_types[record.type] = record_types.get(record.type, 0) + 1

            cache_size = len(self.dns_cache)
            cache_hits = 0  # This would be tracked in a real implementation

            return {
                "total_dns_records": total_records,
                "record_type_distribution": record_types,
                "cache_size": cache_size,
                "cache_hits": cache_hits,
                "search_domains": len(self.config.search_domains),
                "network_policies": len(self.network_policies),
                "active_policies": sum(
                    1 for p in self.network_policies.values() if p.enabled
                ),
                "magic_dns_enabled": self.config.enabled,
                "base_domain": self.base_domain,
            }

        except Exception as e:
            logger.error("Error getting DNS statistics", error=str(e))
            raise TailscaleMCPError(f"Failed to get DNS statistics: {e}") from e

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
