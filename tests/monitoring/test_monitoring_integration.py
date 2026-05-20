"""
Integration tests for the monitoring stack in the Tailscale MCP server.
"""

import builtins
import contextlib
import json
import logging
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import structlog

from tailscalemcp.__main__ import setup_prometheus_metrics, setup_structured_logging

_win = pytest.mark.xfail(sys.platform == "win32", reason="Windows file locking", strict=False)


class TestMonitoringIntegration:
    """Test the integration of structured logging and Prometheus metrics."""

    def teardown_method(self):
        """Clean up log handlers after each test."""
        root_logger = logging.getLogger()
        for h in list(root_logger.handlers):
            if isinstance(h, (logging.FileHandler, logging.StreamHandler)):
                h.close()
                root_logger.removeHandler(h)

    @_win
    def test_structured_logging_with_prometheus_metrics(self):
        """Test that structured logging and Prometheus can coexist."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                logger.info(
                    "Device operation completed",
                    device_id="test-device",
                    operation="authorize",
                    status="success",
                    duration_ms=150,
                )

                with open(log_file) as f:
                    log_content = f.read().strip()
                log_data = json.loads(log_content)
                assert log_data["event"] == "Device operation completed"
                assert log_data["device_id"] == "test-device"

    @_win
    def test_monitoring_stack_initialization(self):
        """Test that the monitoring stack initializes correctly."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server") as mock_server,
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))
                mock_server.assert_called_once_with(9091)
                assert Path(log_file).parent.exists()

    @_win
    def test_log_metrics_correlation(self):
        """Test that log entries and metrics share consistent identifiers."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                device_id = "device-123"
                logger.info("Device connected", device_id=device_id, status="online")

                with open(log_file) as f:
                    log_content = f.read().strip()
                log_data = json.loads(log_content)
                assert log_data["device_id"] == device_id
                assert log_data["status"] == "online"

    @_win
    def test_error_logging_with_metrics(self):
        """Test that errors are logged with context for metric correlation."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                try:
                    raise ConnectionError("Failed to connect to device")
                except ConnectionError:
                    logger.exception(
                        "Device connection failed",
                        device_id="device-456",
                        error_type="ConnectionError",
                    )

                with open(log_file) as f:
                    log_content = f.read().strip()
                log_data = json.loads(log_content)
                assert log_data["event"] == "Device connection failed"
                assert "exception" in log_data

    @_win
    def test_device_activity_monitoring(self):
        """Test monitoring of device activity with structured logs."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                activities = [
                    ("device-001", "connect", {"ip": "100.64.0.1"}),
                    ("device-001", "auth", {"method": "key"}),
                    ("device-002", "connect", {"ip": "100.64.0.2"}),
                ]
                for device_id, action, details in activities:
                    logger.info(f"Device {action}", device_id=device_id, **details)

                with open(log_file) as f:
                    lines = [line for line in f if line.strip()]
                assert len(lines) == 3

    @_win
    def test_network_traffic_monitoring(self):
        """Test network traffic monitoring with structured logging."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                logger.info(
                    "Network traffic",
                    bytes_sent=1024,
                    bytes_received=2048,
                    source_ip="100.64.0.1",
                    dest_ip="100.64.0.2",
                    protocol="tcp",
                )

                with open(log_file) as f:
                    log_content = f.read().strip()
                log_data = json.loads(log_content)
                assert log_data["bytes_sent"] == 1024
                assert log_data["bytes_received"] == 2048

    @_win
    def test_api_request_monitoring(self):
        """Test API request monitoring with structured logging."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                logger.info(
                    "API request",
                    endpoint="/devices",
                    method="GET",
                    status_code=200,
                    response_time=0.1,
                )

                with open(log_file) as f:
                    log_content = f.read().strip()
                log_data = json.loads(log_content)
                assert log_data["endpoint"] == "/devices"
                assert log_data["status_code"] == 200

    @_win
    def test_monitoring_stack_health_check(self):
        """Test monitoring stack health check with structured logging."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                logger.info(
                    "Health check",
                    component="monitoring_stack",
                    status="healthy",
                )

                with open(log_file) as f:
                    log_content = f.read().strip()
                log_data = json.loads(log_content)
                assert log_data["component"] == "monitoring_stack"
                assert log_data["status"] == "healthy"

    @_win
    def test_monitoring_stack_error_recovery(self):
        """Test error recovery with structured logging."""
        import logging

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            with (
                patch("tailscalemcp.__main__.start_http_server"),
                patch("tailscalemcp.__main__.Info"),
            ):
                setup_prometheus_metrics(9091)
                setup_structured_logging("INFO", str(log_file))

                logger = structlog.get_logger("test_logger")
                logger.error("Component failed", component="test_component", error="Test error")
                logger.info("Component recovered", component="test_component", recovery_time=0.5)

                with open(log_file) as f:
                    lines = [line for line in f if line.strip()]
                assert len(lines) == 2
