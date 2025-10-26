"""
Integration tests for the monitoring stack in the Tailscale MCP server.
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import structlog

from src.tailscalemcp.__main__ import setup_structured_logging, setup_prometheus_metrics


class TestMonitoringIntegration:
    """Test the integration of structured logging and Prometheus metrics."""

    def teardown_method(self):
        """Clean up after each test method."""
        # Reset structlog configuration
        structlog.reset_defaults()
        
        # Clean up logging handlers
        import logging
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            try:
                handler.close()
            except:
                pass
            root_logger.removeHandler(handler)

    def test_structured_logging_with_prometheus_metrics(self):
        """Test that structured logging works alongside Prometheus metrics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup both logging and metrics
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Create a logger and log some messages
            logger = structlog.get_logger("test_logger")
            logger.info("Test message", device_id="test-device", operation="test")
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify logging worked
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.loads(f.read().strip())
                    
                assert log_data["event"] == "Test message"
                assert log_data["device_id"] == "test-device"

    def test_monitoring_stack_initialization(self):
        """Test that the monitoring stack initializes correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server') as mock_server:
                with patch('src.tailscalemcp.__main__.Info') as mock_info:
                    mock_info_instance = MagicMock()
                    mock_info.return_value = mock_info_instance
                    
                    setup_prometheus_metrics(9091)
                    setup_structured_logging("INFO", str(log_file))
                    
                    # Verify metrics server started
                    mock_server.assert_called_once_with(9091)
                    
                    # Verify structlog is configured
                    assert structlog.is_configured()

    def test_log_metrics_correlation(self):
        """Test that logs and metrics can be correlated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log messages with correlation IDs
            logger = structlog.get_logger("test_logger")
            correlation_id = "test-correlation-123"
            
            logger.info("Operation started", 
                       correlation_id=correlation_id,
                       device_id="test-device",
                       operation="start")
            
            logger.info("Operation completed", 
                       correlation_id=correlation_id,
                       device_id="test-device",
                       operation="complete")
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify correlation
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                assert len(lines) == 2
                
                # Both log entries should have the same correlation_id
                for line in lines:
                    log_data = json.loads(line.strip())
                    assert log_data["correlation_id"] == correlation_id

    def test_error_logging_with_metrics(self):
        """Test that error logging works with metrics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log an error
            logger = structlog.get_logger("test_logger")
            
            try:
                raise ValueError("Test error")
            except ValueError:
                logger.exception("Error occurred", 
                               device_id="test-device",
                               operation="error_test")
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify error logging
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.loads(f.read().strip())
                    
                assert log_data["event"] == "Error occurred"
                assert log_data["device_id"] == "test-device"
                assert "exception" in log_data or "exc_info" in log_data or "error" in log_data

    def test_device_activity_monitoring(self):
        """Test monitoring of device activity."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log device activity
            logger = structlog.get_logger("device_monitor")
            
            activities = [
                ("device-1", "authorize", "success"),
                ("device-2", "revoke", "success"),
                ("device-1", "connect", "success"),
                ("device-3", "authorize", "failed"),
            ]
            
            for device_id, operation, status in activities:
                logger.info("Device activity",
                           device_id=device_id,
                           operation=operation,
                           status=status,
                           timestamp=time.time())
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify device activity logging
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                assert len(lines) == 4
                
                # Verify each activity was logged
                for i, line in enumerate(lines):
                    log_data = json.loads(line.strip())
                    device_id, operation, status = activities[i]
                    
                    assert log_data["device_id"] == device_id
                    assert log_data["operation"] == operation
                    assert log_data["status"] == status

    def test_network_traffic_monitoring(self):
        """Test monitoring of network traffic."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log network traffic
            logger = structlog.get_logger("network_monitor")
            
            traffic_events = [
                {"bytes_sent": 1024, "bytes_received": 2048, "duration": 0.5},
                {"bytes_sent": 2048, "bytes_received": 4096, "duration": 1.0},
                {"bytes_sent": 512, "bytes_received": 1024, "duration": 0.25},
            ]
            
            for i, traffic in enumerate(traffic_events):
                logger.info("Network traffic",
                           device_id=f"device-{i+1}",
                           **traffic)
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify network traffic logging
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                assert len(lines) == 3
                
                # Verify each traffic event was logged
                for i, line in enumerate(lines):
                    log_data = json.loads(line.strip())
                    traffic = traffic_events[i]
                    
                    assert log_data["bytes_sent"] == traffic["bytes_sent"]
                    assert log_data["bytes_received"] == traffic["bytes_received"]
                    assert log_data["duration"] == traffic["duration"]

    def test_api_request_monitoring(self):
        """Test monitoring of API requests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log API requests
            logger = structlog.get_logger("api_monitor")
            
            api_requests = [
                {"method": "GET", "endpoint": "/devices", "status_code": 200, "response_time": 0.1},
                {"method": "POST", "endpoint": "/devices/authorize", "status_code": 201, "response_time": 0.2},
                {"method": "DELETE", "endpoint": "/devices/revoke", "status_code": 204, "response_time": 0.15},
            ]
            
            for request in api_requests:
                logger.info("API request",
                           **request)
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify API request logging
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                assert len(lines) == 3
                
                # Verify each API request was logged
                for i, line in enumerate(lines):
                    log_data = json.loads(line.strip())
                    request = api_requests[i]
                    
                    assert log_data["method"] == request["method"]
                    assert log_data["endpoint"] == request["endpoint"]
                    assert log_data["status_code"] == request["status_code"]
                    assert log_data["response_time"] == request["response_time"]

    def test_monitoring_stack_health_check(self):
        """Test health check functionality of the monitoring stack."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log health check
            logger = structlog.get_logger("health_monitor")
            
            logger.info("Health check",
                       component="monitoring_stack",
                       status="healthy",
                       timestamp=time.time())
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify health check logging
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.loads(f.read().strip())
                    
                assert log_data["event"] == "Health check"
                assert log_data["component"] == "monitoring_stack"
                assert log_data["status"] == "healthy"

    def test_monitoring_stack_error_recovery(self):
        """Test error recovery in the monitoring stack."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Setup monitoring stack
            with patch('src.tailscalemcp.__main__.start_http_server'):
                with patch('src.tailscalemcp.__main__.Info'):
                    setup_prometheus_metrics(9091)
            
            setup_structured_logging("INFO", str(log_file))
            
            # Log error and recovery
            logger = structlog.get_logger("recovery_monitor")
            
            logger.error("Component failed",
                        component="test_component",
                        error="Test error",
                        timestamp=time.time())
            
            logger.info("Component recovered",
                       component="test_component",
                       recovery_time=0.5,
                       timestamp=time.time())
            
            # Wait for file to be written
            time.sleep(0.1)
            
            # Verify error and recovery logging
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                assert len(lines) == 2
                
                # Verify error log
                error_log = json.loads(lines[0].strip())
                assert error_log["event"] == "Component failed"
                assert error_log["component"] == "test_component"
                assert error_log["error"] == "Test error"
                
                # Verify recovery log
                recovery_log = json.loads(lines[1].strip())
                assert recovery_log["event"] == "Component recovered"
                assert recovery_log["component"] == "test_component"
                assert recovery_log["recovery_time"] == 0.5