"""Integration tests for device operations."""

from unittest.mock import AsyncMock, patch

import pytest

from tailscalemcp.config import TailscaleConfig
from tailscalemcp.exceptions import NotFoundError
from tailscalemcp.operations.devices import DeviceOperations


@pytest.fixture
def config():
    """Create test configuration."""
    return TailscaleConfig(
        tailscale_api_key="tskey-test",
        tailscale_tailnet="test.tailnet.ts.net",
    )


@pytest.fixture
def operations(config):
    """Create device operations for testing."""
    return DeviceOperations(config=config)


@pytest.mark.asyncio
async def test_list_devices(operations):
    """Test listing devices."""
    mock_devices = [
        {
            "id": "device1",
            "name": "test-device",
            "hostname": "test-host",
            "os": "linux",
            "addresses": [{"ip": "100.64.0.1"}],
            "authorized": True,
            "connectedToControl": True,
            "tags": ["tag:test"],
            "lastSeen": "2024-01-15T12:00:00Z",
        }
    ]

    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"devices": mock_devices}
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        devices = await operations.list_devices()
        assert len(devices) == 1
        assert devices[0].id == "device1"
        assert devices[0].name == "test-device"


@pytest.mark.asyncio
async def test_list_devices_online_only(operations):
    """Test listing only online devices."""
    mock_devices = [
        {
            "id": "device1",
            "name": "online-device",
            "hostname": "online-host",
            "os": "linux",
            "addresses": [{"ip": "100.64.0.1"}],
            "authorized": True,
            "connectedToControl": True,
            "tags": [],
            "lastSeen": "2024-01-15T12:00:00Z",
        },
        {
            "id": "device2",
            "name": "offline-device",
            "hostname": "offline-host",
            "os": "linux",
            "addresses": [{"ip": "100.64.0.2"}],
            "authorized": True,
            "connectedToControl": False,
            "tags": [],
            "lastSeen": "2024-01-01T00:00:00Z",
        },
    ]

    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"devices": mock_devices}
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        devices = await operations.list_devices(online_only=True)
        assert len(devices) == 1
        assert devices[0].id == "device1"
        assert devices[0].name == "online-device"


@pytest.mark.asyncio
async def test_get_device(operations):
    """Test getting a single device."""
    mock_device = {
        "id": "device1",
        "name": "test-device",
        "hostname": "test-host",
        "os": "linux",
        "addresses": [{"ip": "100.64.0.1"}],
        "authorized": True,
        "connectedToControl": True,
        "tags": ["tag:test"],
        "lastSeen": "2024-01-15T12:00:00Z",
    }

    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_device
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        device = await operations.get_device("device1")
        assert device.id == "device1"
        assert device.name == "test-device"


@pytest.mark.asyncio
async def test_get_device_not_found(operations):
    """Test getting non-existent device."""
    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 404
        mock_request.return_value = mock_response_obj

        with pytest.raises(NotFoundError):
            await operations.get_device("nonexistent")


@pytest.mark.asyncio
async def test_authorize_device(operations):
    """Test authorizing a device."""
    mock_device = {
        "id": "device1",
        "name": "test-device",
        "hostname": "test-host",
        "os": "linux",
        "addresses": [{"ip": "100.64.0.1"}],
        "authorized": True,
        "connectedToControl": True,
        "tags": [],
        "lastSeen": "2024-01-15T12:00:00Z",
    }

    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        # First call: get device
        # Second call: update device
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_device
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        device = await operations.authorize_device("device1", True, "Test authorization")
        assert device.authorized is True


@pytest.mark.asyncio
async def test_rename_device(operations):
    """Test renaming a device."""
    mock_device = {
        "id": "device1",
        "name": "new-name",
        "hostname": "test-host",
        "os": "linux",
        "addresses": [{"ip": "100.64.0.1"}],
        "authorized": True,
        "connectedToControl": True,
        "tags": [],
        "lastSeen": "2024-01-15T12:00:00Z",
    }

    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_device
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        device = await operations.rename_device("device1", "new-name")
        assert device.name == "new-name"


@pytest.mark.asyncio
async def test_search_devices(operations):
    """Test searching devices."""
    mock_devices = [
        {
            "id": "device1",
            "name": "engineering-laptop",
            "hostname": "eng-laptop",
            "os": "linux",
            "addresses": [{"ip": "100.64.0.1"}],
            "authorized": True,
            "connectedToControl": True,
            "tags": ["tag:engineering"],
            "lastSeen": "2024-01-15T12:00:00Z",
        },
        {
            "id": "device2",
            "name": "sales-laptop",
            "hostname": "sales-laptop",
            "os": "windows",
            "addresses": [{"ip": "100.64.0.2"}],
            "authorized": True,
            "connectedToControl": True,
            "tags": ["tag:sales"],
            "lastSeen": "2024-01-15T12:00:00Z",
        },
    ]

    with patch.object(
        operations.client.client, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"devices": mock_devices}
        mock_response_obj.raise_for_status = AsyncMock()
        mock_request.return_value = mock_response_obj

        devices = await operations.search_devices("engineering", ["name", "tags"])
        assert len(devices) == 1
        assert devices[0].name == "engineering-laptop"







