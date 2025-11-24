"""Tailnet models for Tailscale."""

from typing import Any

from pydantic import BaseModel, Field


class TailnetSettings(BaseModel):
    """Tailnet settings model."""

    magic_dns_enabled: bool = Field(False, description="MagicDNS enabled")
    default_route_enabled: bool = Field(False, description="Default route enabled")
    advertising_routes: list[str] = Field(
        default_factory=list, description="Advertised routes"
    )


class Tailnet(BaseModel):
    """Tailnet model."""

    name: str = Field(..., description="Tailnet name")
    display_name: str | None = Field(None, description="Display name")
    settings: TailnetSettings = Field(
        default_factory=TailnetSettings, description="Tailnet settings"
    )

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Tailnet":
        """Create Tailnet from API response.

        Args:
            data: Tailnet data from API

        Returns:
            Tailnet instance
        """
        settings_data = data.get("settings", {})
        settings = TailnetSettings(
            magic_dns_enabled=settings_data.get("magicDNS", False),
            default_route_enabled=settings_data.get("defaultRoute", False),
            advertising_routes=settings_data.get("advertisedRoutes", []),
        )

        return cls(
            name=data.get("name", ""),
            display_name=data.get("displayName", data.get("display_name")),
            settings=settings,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert tailnet to dictionary."""
        return self.model_dump(exclude_none=True)
