"""
Tests for the Tailscale MCP server.
"""

from unittest.mock import patch

import pytest

from tailscalemcp import TailscaleMCPServer
from tailscalemcp.exceptions import TailscaleMCPError


@pytest.fixture
def mock_httpx_client():
    """Mock the httpx.AsyncClient for testing."""
    with patch("httpx.AsyncClient") as mock_client:
        yield mock_client


@pytest.fixture
async def mcp_server():
    """Create a test instance of the TailscaleMCPServer."""
    server = TailscaleMCPServer(api_key="test_key", tailnet="test_tailnet")
    yield server
    # FastMCP 2.12 handles cleanup automatically


@pytest.mark.asyncio
async def test_server_initialization(mcp_server):
    """Test that the server initializes correctly."""
    assert mcp_server.api_key == "test_key"
    assert mcp_server.tailnet == "test_tailnet"
    assert mcp_server.mcp is not None
    assert mcp_server.device_manager is not None
    assert mcp_server.monitor is not None
    assert mcp_server.grafana_dashboard is not None
    assert mcp_server.taildrop_manager is not None
    assert mcp_server.magic_dns_manager is not None
    assert mcp_server.portmanteau_tools is not None


@pytest.mark.asyncio
async def test_device_manager_initialization(mcp_server):
    """Test that the device manager initializes correctly."""
    assert mcp_server.device_manager.api_key == "test_key"
    assert mcp_server.device_manager.tailnet == "test_tailnet"


@pytest.mark.asyncio
async def test_monitor_initialization(mcp_server):
    """Test that the monitor initializes correctly."""
    assert mcp_server.monitor.api_key == "test_key"
    assert mcp_server.monitor.tailnet == "test_tailnet"


@pytest.mark.asyncio
async def test_grafana_dashboard_initialization(mcp_server):
    """Test that the Grafana dashboard initializes correctly."""
    assert mcp_server.grafana_dashboard.tailnet == "test_tailnet"


@pytest.mark.asyncio
async def test_magic_dns_manager_initialization(mcp_server):
    """Test that the MagicDNS manager initializes correctly."""
    assert mcp_server.magic_dns_manager.tailnet == "test_tailnet"


@pytest.mark.asyncio
async def test_portmanteau_tools_initialization(mcp_server):
    """Test that the portmanteau tools initialize correctly."""
    assert mcp_server.portmanteau_tools.mcp is not None
    assert mcp_server.portmanteau_tools.device_manager is not None
    assert mcp_server.portmanteau_tools.monitor is not None
    assert mcp_server.portmanteau_tools.grafana_dashboard is not None
    assert mcp_server.portmanteau_tools.taildrop_manager is not None
    assert mcp_server.portmanteau_tools.magic_dns_manager is not None


@pytest.mark.asyncio
async def test_server_start_stop(mcp_server):
    """Test server start and stop functionality."""
    # Test that start/stop methods exist and are callable
    assert callable(mcp_server.start)
    assert callable(mcp_server.stop)

    # Test async context manager
    assert hasattr(mcp_server, "__aenter__")
    assert hasattr(mcp_server, "__aexit__")


@pytest.mark.asyncio
async def test_server_with_mock_httpx(mcp_server, mock_httpx_client):
    """Test server with mocked httpx client."""
    # This test ensures the mock_httpx_client fixture is used
    assert mock_httpx_client is not None
    assert mcp_server is not None


@pytest.mark.asyncio
async def test_tailscale_mcp_error():
    """Test TailscaleMCPError exception."""
    error = TailscaleMCPError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


@pytest.mark.asyncio
async def test_server_environment_variables():
    """Test server initialization with environment variables."""
    with patch.dict("os.environ", {
        "TAILSCALE_API_KEY": "env_api_key",
        "TAILSCALE_TAILNET": "env_tailnet"
    }):
        server = TailscaleMCPServer()
        assert server.api_key == "env_api_key"
        assert server.tailnet == "env_tailnet"


@pytest.mark.asyncio
async def test_server_parameter_override():
    """Test that parameters override environment variables."""
    with patch.dict("os.environ", {
        "TAILSCALE_API_KEY": "env_api_key",
        "TAILSCALE_TAILNET": "env_tailnet"
    }):
        server = TailscaleMCPServer(api_key="param_api_key", tailnet="param_tailnet")
        assert server.api_key == "param_api_key"
        assert server.tailnet == "param_tailnet"


@pytest.mark.asyncio
async def test_server_no_parameters():
    """Test server initialization with no parameters."""
    with patch.dict("os.environ", {}, clear=True):
        server = TailscaleMCPServer()
        assert server.api_key is None
        assert server.tailnet is None


@pytest.mark.asyncio
async def test_server_main_function():
    """Test the main function exists and is callable."""
    from tailscalemcp.mcp_server import main
    assert callable(main)


@pytest.mark.asyncio
async def test_server_instance():
    """Test that the server instance is created correctly."""
    from tailscalemcp.mcp_server import server
    assert isinstance(server, TailscaleMCPServer)


@pytest.mark.asyncio
async def test_fastmcp_initialization(mcp_server):
    """Test that FastMCP is initialized correctly."""
    assert mcp_server.mcp is not None
    assert hasattr(mcp_server.mcp, "run")


@pytest.mark.asyncio
async def test_managers_have_required_attributes(mcp_server):
    """Test that all managers have the required attributes."""
    # Device manager should have api_key and tailnet
    assert hasattr(mcp_server.device_manager, "api_key")
    assert hasattr(mcp_server.device_manager, "tailnet")

    # Monitor should have api_key and tailnet
    assert hasattr(mcp_server.monitor, "api_key")
    assert hasattr(mcp_server.monitor, "tailnet")

    # Grafana dashboard should have tailnet
    assert hasattr(mcp_server.grafana_dashboard, "tailnet")

    # MagicDNS manager should have tailnet
    assert hasattr(mcp_server.magic_dns_manager, "tailnet")


@pytest.mark.asyncio
async def test_portmanteau_tools_have_managers(mcp_server):
    """Test that portmanteau tools have access to all managers."""
    pt = mcp_server.portmanteau_tools

    assert pt.device_manager is mcp_server.device_manager
    assert pt.monitor is mcp_server.monitor
    assert pt.grafana_dashboard is mcp_server.grafana_dashboard
    assert pt.taildrop_manager is mcp_server.taildrop_manager
    assert pt.magic_dns_manager is mcp_server.magic_dns_manager
    assert pt.mcp is mcp_server.mcp
