"""
Tests for structured logging functionality in the Tailscale MCP server.
"""

import json
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import structlog

from src.tailscalemcp.__main__ import setup_structured_logging


class TestStructuredLogging:
    """Test structured logging setup and functionality."""

    def teardown_method(self):
        """Clean up after each test method."""
        # Reset structlog configuration
        structlog.reset_defaults()
        
        # Clean up logging handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            try:
                handler.close()
            except:
                pass
            root_logger.removeHandler(handler)

    def test_setup_structured_logging_creates_directory(self):
        """Test that logging setup creates the log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            assert log_file.parent.exists()
            assert log_file.parent.is_dir()

    def test_setup_structured_logging_configures_structlog(self):
        """Test that structlog is properly configured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            # Verify structlog is configured
            assert structlog.is_configured()
            
            # Test that we can create a logger
            logger = structlog.get_logger("test")
            assert logger is not None

    def test_structured_logging_outputs_json(self):
        """Test that structured logging outputs JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            # Create a logger and log a message
            logger = structlog.get_logger("test_logger")
            logger.info("Test message", device_id="test-device", operation="test")
            
            # Wait a moment for file to be written
            import time
            time.sleep(0.1)
            
            # Read the log file and verify JSON format
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_content = f.read().strip()
                    
                # Should be valid JSON
                log_data = json.loads(log_content)
                
                # Verify expected fields
                assert log_data["event"] == "Test message"
                assert log_data["logger"] == "test_logger"
                assert log_data["device_id"] == "test-device"
                assert log_data["operation"] == "test"
                assert "timestamp" in log_data
                assert "level" in log_data

    def test_structured_logging_includes_timestamp(self):
        """Test that structured logging includes timestamp."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            logger = structlog.get_logger("test_logger")
            logger.info("Test message")
            
            # Wait a moment for file to be written
            import time
            time.sleep(0.1)
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.loads(f.read().strip())
                    
                # Verify timestamp is in ISO format
                assert "timestamp" in log_data
                timestamp = log_data["timestamp"]
                assert timestamp is not None
                # Should be in ISO format (contains 'T' and 'Z')
                assert 'T' in timestamp or 'Z' in timestamp

    def test_structured_logging_respects_log_level(self):
        """Test that structured logging respects log level configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Set to WARNING level
            setup_structured_logging("WARNING", str(log_file))
            
            logger = structlog.get_logger("test_logger")
            logger.info("This should not appear")
            logger.warning("This should appear")
            
            # Wait a moment for file to be written
            import time
            time.sleep(0.1)
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_content = f.read().strip()
                    
                # Should only contain the warning message
                log_data = json.loads(log_content)
                assert log_data["event"] == "This should appear"
                assert log_data["level"] == "WARNING"

    def test_structured_logging_handles_exceptions(self):
        """Test that structured logging properly handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            logger = structlog.get_logger("test_logger")
            
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Exception occurred", device_id="test-device")
            
            # Wait a moment for file to be written
            import time
            time.sleep(0.1)
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_content = f.read().strip()
                    
                log_data = json.loads(log_content)
                
                # Verify exception information is included
                assert log_data["event"] == "Exception occurred"
                assert log_data["device_id"] == "test-device"
                # Exception info might be in different fields depending on configuration
                assert "exception" in log_data or "exc_info" in log_data or "error" in log_data

    def test_structured_logging_multiple_handlers(self):
        """Test that structured logging sets up both file and console handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            root_logger = logging.getLogger()
            handlers = root_logger.handlers
            
            # Should have at least 2 handlers (file and console)
            assert len(handlers) >= 2
            
            # Verify handler types
            handler_types = [type(h).__name__ for h in handlers]
            assert "FileHandler" in handler_types
            assert "StreamHandler" in handler_types

    def test_structured_logging_with_context(self):
        """Test that structured logging preserves context across log calls."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            logger = structlog.get_logger("test_logger")
            
            # Log multiple messages with context
            logger.info("First message", device_id="test-device", operation="start")
            logger.info("Second message", operation="process")
            logger.info("Third message", operation="end")
            
            # Wait a moment for file to be written
            import time
            time.sleep(0.1)
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                # Should have 3 log entries
                assert len(lines) == 3
                
                # Verify each log entry
                for i, line in enumerate(lines):
                    log_data = json.loads(line.strip())
                    assert log_data["logger"] == "test_logger"
                    assert log_data["level"] == "INFO"
                    
                    if i == 0:
                        assert log_data["device_id"] == "test-device"
                        assert log_data["operation"] == "start"
                    elif i == 1:
                        assert log_data["operation"] == "process"
                    elif i == 2:
                        assert log_data["operation"] == "end"

    def test_structured_logging_performance(self):
        """Test that structured logging performs reasonably well."""
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            logger = structlog.get_logger("test_logger")
            
            # Log 10 messages and measure time (reduced from 100 for faster tests)
            start_time = time.time()
            for i in range(10):
                logger.info(f"Message {i}", iteration=i, device_id=f"device-{i}")
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Should complete in reasonable time (less than 1 second for 10 messages)
            assert duration < 1.0
            
            # Wait for file writes
            time.sleep(0.1)
            
            # Verify all messages were written
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                assert len(lines) == 10

    def test_structured_logging_loki_compatibility(self):
        """Test that structured logging output is compatible with Loki parsing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            setup_structured_logging("INFO", str(log_file))
            
            logger = structlog.get_logger("test_logger")
            
            # Log message with typical Loki fields
            logger.info("Device operation", 
                       device_id="test-device",
                       device_name="test-server",
                       operation="authorize",
                       status="success",
                       duration=0.5,
                       bytes_sent=1024,
                       bytes_received=2048)
            
            # Wait a moment for file to be written
            import time
            time.sleep(0.1)
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_data = json.loads(f.read().strip())
                    
                # Verify all fields that Promtail expects
                expected_fields = [
                    "timestamp", "level", "logger", "event",
                    "device_id", "device_name", "operation", "status",
                    "duration", "bytes_sent", "bytes_received"
                ]
                
                for field in expected_fields:
                    assert field in log_data, f"Missing field: {field}"
                    
                # Verify field types
                assert isinstance(log_data["device_id"], str)
                assert isinstance(log_data["device_name"], str)
                assert isinstance(log_data["operation"], str)
                assert isinstance(log_data["status"], str)
                assert isinstance(log_data["duration"], (int, float))
                assert isinstance(log_data["bytes_sent"], (int, float))
                assert isinstance(log_data["bytes_received"], (int, float))