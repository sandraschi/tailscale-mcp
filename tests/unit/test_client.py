"""Unit tests for API client."""

from unittest.mock import AsyncMock, patch

import pytest

from tailscalemcp.client.api_client import TailscaleAPIClient
from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitExceededError,
)


@pytest.fixture
def config():
    """Create test configuration."""
    return TailscaleConfig(
        tailscale_api_key="tskey-test",
        tailscale_tailnet="test.tailnet.ts.net",
    )


@pytest.fixture
def api_client(config):
    """Create API client for testing."""
    return TailscaleAPIClient(config=config)


@pytest.mark.asyncio
async def test_list_devices_success(api_client):
    """Test successful device listing."""
    mock_response = {
        "devices": [
            {
                "id": "device1",
                "name": "test-device",
                "hostname": "test-host",
                "os": "linux",
                "addresses": [{"ip": "100.64.0.1"}],
                "authorized": True,
                "tags": ["tag:test"],
            }
        ]
    }

    with patch.object(
        api_client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        devices = await api_client.list_devices()
        assert len(devices) == 1
        assert devices[0]["id"] == "device1"
        assert devices[0]["name"] == "test-device"


@pytest.mark.asyncio
async def test_get_device_success(api_client):
    """Test successful device retrieval."""
    mock_response = {
        "id": "device1",
        "name": "test-device",
        "hostname": "test-host",
        "os": "linux",
    }

    with patch.object(
        api_client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        device = await api_client.get_device("device1")
        assert device["id"] == "device1"
        assert device["name"] == "test-device"


@pytest.mark.asyncio
async def test_get_device_not_found(api_client):
    """Test device not found error."""
    with patch.object(
        api_client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 404
        mock_request.return_value = mock_response_obj

        with pytest.raises(NotFoundError):
            await api_client.get_device("nonexistent")


@pytest.mark.asyncio
async def test_authentication_error(api_client):
    """Test authentication error handling."""
    with patch.object(
        api_client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 401
        mock_request.return_value = mock_response_obj

        with pytest.raises(AuthenticationError):
            await api_client.list_devices()


@pytest.mark.asyncio
async def test_rate_limit_error(api_client):
    """Test rate limit error handling."""
    with patch.object(
        api_client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 429
        mock_request.return_value = mock_response_obj

        with pytest.raises(RateLimitExceededError):
            await api_client.list_devices()


@pytest.mark.asyncio
async def test_context_manager(api_client):
    """Test context manager support."""
    async with api_client:
        # Client should work in context
        assert api_client.client is not None

    # Client should be closed after context
    await api_client.close()







