"""Device models for Tailscale."""

import contextlib
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeviceStatus(str, Enum):
    """Device connection status."""

    ONLINE = "online"
    OFFLINE = "offline"
    UNAUTHORIZED = "unauthorized"
    UNKNOWN = "unknown"


class Device(BaseModel):
    """Tailscale device/node model."""

    id: str = Field(..., description="Device ID")
    node_key: str | None = Field(None, description="Node key")
    machine_key: str | None = Field(None, description="Machine key")
    name: str = Field(..., description="Device name")
    hostname: str = Field(..., description="Device hostname")
    os: str = Field(..., description="Operating system")
    os_version: str | None = Field(None, description="OS version")
    client_version: str | None = Field(None, description="Tailscale client version")
    ipv4: str | None = Field(None, description="IPv4 address")
    ipv6: str | None = Field(None, description="IPv6 address")
    tags: list[str] = Field(default_factory=list, description="Device tags")
    authorized: bool = Field(False, description="Device is authorized")
    connected_to_control: bool = Field(
        False, description="Device is connected to control plane"
    )
    last_seen: datetime | None = Field(None, description="Last seen timestamp")
    tailnet_lock_key: str | None = Field(None, description="Tailnet lock key")
    key_expiry_disabled: bool = Field(False, description="Key expiry disabled")
    expires: datetime | None = Field(None, description="Key expiration time")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Device":
        """Create Device from API response.

        Args:
            data: Device data from API

        Returns:
            Device instance
        """
        # Handle lastSeen timestamp
        last_seen = None
        if data.get("lastSeen"):
            with contextlib.suppress(ValueError, AttributeError):
                last_seen = datetime.fromisoformat(
                    data["lastSeen"].replace("Z", "+00:00")
                )

        # Handle expires timestamp
        expires = None
        if data.get("expires"):
            with contextlib.suppress(ValueError, AttributeError):
                expires = datetime.fromisoformat(data["expires"].replace("Z", "+00:00"))

        return cls(
            id=data.get("id", ""),
            node_key=data.get("nodeKey"),
            machine_key=data.get("machineKey"),
            name=data.get("name", ""),
            hostname=data.get("hostname", ""),
            os=data.get("os", "unknown"),
            os_version=data.get("osVersion"),
            client_version=data.get("clientVersion"),
            ipv4=data.get("addresses", [{}])[0].get("ip")
            if data.get("addresses")
            else None,
            ipv6=None,  # Extract from addresses if present
            tags=data.get("tags", []),
            authorized=data.get("authorized", False),
            connected_to_control=data.get("connectedToControl", False),
            last_seen=last_seen,
            tailnet_lock_key=data.get("tailnetLockKey"),
            key_expiry_disabled=data.get("keyExpiryDisabled", False),
            expires=expires,
        )

    @property
    def status(self) -> DeviceStatus:
        """Get device status."""
        if self.connected_to_control:
            return DeviceStatus.ONLINE
        elif not self.authorized:
            return DeviceStatus.UNAUTHORIZED
        elif self.last_seen:
            return DeviceStatus.OFFLINE
        else:
            return DeviceStatus.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        """Convert device to dictionary."""
        return self.model_dump(exclude_none=True)
