"""Data models for Tailscale entities."""

from .device import Device, DeviceStatus
from .policy import ACLPolicy, ACLRule, PolicyGrant
from .service import Service, ServiceEndpoint
from .tailnet import Tailnet, TailnetSettings
from .user import User, UserRole

__all__ = [
    "ACLPolicy",
    "ACLRule",
    "Device",
    "DeviceStatus",
    "PolicyGrant",
    "Service",
    "ServiceEndpoint",
    "Tailnet",
    "TailnetSettings",
    "User",
    "UserRole",
]
