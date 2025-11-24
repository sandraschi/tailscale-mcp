"""Unit tests for data models."""

from datetime import datetime

from tailscalemcp.models.device import Device, DeviceStatus
from tailscalemcp.models.service import Service, ServiceEndpoint


def test_device_from_api_response():
    """Test Device model creation from API response."""
    api_data = {
        "id": "device123",
        "nodeKey": "node-key-123",
        "machineKey": "machine-key-123",
        "name": "test-device",
        "hostname": "test-host",
        "os": "linux",
        "osVersion": "22.04",
        "clientVersion": "1.50.0",
        "addresses": [{"ip": "100.64.0.1"}],
        "tags": ["tag:test", "tag:engineering"],
        "authorized": True,
        "connectedToControl": True,
        "lastSeen": "2024-01-15T12:00:00Z",
        "expires": "2025-01-15T12:00:00Z",
    }

    device = Device.from_api_response(api_data)

    assert device.id == "device123"
    assert device.name == "test-device"
    assert device.hostname == "test-host"
    assert device.os == "linux"
    assert device.ipv4 == "100.64.0.1"
    assert device.tags == ["tag:test", "tag:engineering"]
    assert device.authorized is True
    assert device.connected_to_control is True
    assert isinstance(device.last_seen, datetime)
    assert device.status == DeviceStatus.ONLINE


def test_device_status_offline():
    """Test device status calculation for offline device."""
    api_data = {
        "id": "device123",
        "name": "test-device",
        "hostname": "test-host",
        "os": "linux",
        "authorized": True,
        "connectedToControl": False,
        "lastSeen": "2024-01-01T00:00:00Z",
    }

    device = Device.from_api_response(api_data)
    assert device.status == DeviceStatus.OFFLINE


def test_device_status_unauthorized():
    """Test device status calculation for unauthorized device."""
    api_data = {
        "id": "device123",
        "name": "test-device",
        "hostname": "test-host",
        "os": "linux",
        "authorized": False,
        "connectedToControl": False,
    }

    device = Device.from_api_response(api_data)
    assert device.status == DeviceStatus.UNAUTHORIZED


def test_device_to_dict():
    """Test device serialization to dict."""
    device = Device(
        id="device123",
        name="test-device",
        hostname="test-host",
        os="linux",
        tags=["tag:test"],
        authorized=True,
        connected_to_control=True,
    )

    device_dict = device.to_dict()
    assert device_dict["id"] == "device123"
    assert device_dict["name"] == "test-device"
    assert device_dict["tags"] == ["tag:test"]


def test_service_from_api_response():
    """Test Service model creation from API response."""
    api_data = {
        "id": "svc-123",
        "name": "api-service",
        "tailvipIPv4": "100.101.102.103",
        "magicDNS": "api.tail",
        "tags": ["prod", "api"],
        "endpoints": [
            {
                "deviceId": "device123",
                "ip": "100.64.0.1",
                "port": 8080,
                "protocol": "tcp",
            }
        ],
    }

    service = Service.from_api_response(api_data)

    assert service.id == "svc-123"
    assert service.name == "api-service"
    assert service.tailvip_ipv4 == "100.101.102.103"
    assert service.magicdns_name == "api.tail"
    assert service.tags == ["prod", "api"]
    assert len(service.endpoints) == 1
    assert service.endpoints[0].device_id == "device123"
    assert service.endpoints[0].port == 8080
    assert service.endpoints[0].protocol == "tcp"


def test_service_to_dict():
    """Test service serialization to dict."""
    service = Service(
        id="svc-123",
        name="api-service",
        tailvip_ipv4="100.101.102.103",
        magicdns_name="api.tail",
        tags=["prod"],
        endpoints=[
            ServiceEndpoint(device_id="device123", port=8080, protocol="tcp")
        ],
    )

    service_dict = service.to_dict()
    assert service_dict["id"] == "svc-123"
    assert service_dict["name"] == "api-service"
    assert service_dict["tailvipIPv4"] == "100.101.102.103"
    assert service_dict["magicDNS"] == "api.tail"
    assert len(service_dict["endpoints"]) == 1







