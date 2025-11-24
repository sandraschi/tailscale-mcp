"""Service models for Tailscale Services (TailVIPs)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ServiceEndpoint(BaseModel):
    """Concrete endpoint behind a service (backing node/port)."""

    device_id: str = Field(..., description="Backing device ID")
    ip: str | None = Field(None, description="Backing device IP")
    port: int = Field(..., description="Service port exposed")
    protocol: str = Field("tcp", description="Protocol (tcp/udp)")


class Service(BaseModel):
    """Tailscale logical Service with TailVIP and MagicDNS."""

    id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name (human-readable)")
    tailvip_ipv4: str | None = Field(None, description="Assigned TailVIP IPv4")
    tailvip_ipv6: str | None = Field(None, description="Assigned TailVIP IPv6")
    magicdns_name: str | None = Field(None, description="MagicDNS name for the service")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    tags: list[str] = Field(
        default_factory=list, description="Tags applied to the service"
    )
    endpoints: list[ServiceEndpoint] = Field(
        default_factory=list, description="Backing endpoints for the service"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Service":
        """Create Service from API response structure.

        The exact wire format may evolve; fields are mapped defensively.
        """
        endpoints: list[ServiceEndpoint] = []
        for ep in data.get("endpoints", []) or []:
            endpoints.append(
                ServiceEndpoint(
                    device_id=ep.get("deviceId") or ep.get("device_id", ""),
                    ip=ep.get("ip"),
                    port=int(ep.get("port", 0)),
                    protocol=(ep.get("protocol") or "tcp").lower(),
                )
            )

        return cls(
            id=data.get("id", ""),
            name=data.get("name", data.get("serviceName", "")),
            tailvip_ipv4=data.get("tailvipIPv4") or data.get("tailvip_ipv4"),
            tailvip_ipv6=data.get("tailvipIPv6") or data.get("tailvip_ipv6"),
            magicdns_name=data.get("magicDNS") or data.get("magicdns_name"),
            created_at=None,
            updated_at=None,
            tags=data.get("tags", []) or [],
            endpoints=endpoints,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize service to API-friendly dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "tailvipIPv4": self.tailvip_ipv4,
            "tailvipIPv6": self.tailvip_ipv6,
            "magicDNS": self.magicdns_name,
            "tags": self.tags,
            "endpoints": [
                {
                    "deviceId": ep.device_id,
                    "ip": ep.ip,
                    "port": ep.port,
                    "protocol": ep.protocol,
                }
                for ep in self.endpoints
            ],
        }
