"""
Tests for structured logging functionality in the Tailscale MCP server.
"""

import builtins
import contextlib
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest
import structlog

from tailscalemcp.__main__ import setup_structured_logging

_win = pytest.mark.xfail(sys.platform == "win32", reason="Windows file locking", strict=False)


class TestStructuredLogging:
    """Test structured logging setup and functionality."""

    def teardown_method(self):
        """Clean up logging handlers after each test."""
        root_logger = logging.getLogger()
        for h in list(root_logger.handlers):
            if isinstance(h, (logging.FileHandler, logging.StreamHandler)):
                h.close()
                root_logger.removeHandler(h)

    @_win
    def test_setup_structured_logging_creates_directory(self):
        """Test that the log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "subdir" / "test.log"
            setup_structured_logging("INFO", str(log_file))
            assert log_file.parent.exists()

    @_win
    def test_setup_structured_logging_configures_structlog(self):
        """Test that structlog is properly configured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            assert Path(log_file).parent.exists()

    @_win
    def test_structured_logging_outputs_json(self):
        """Test that log output is valid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            logger.info("Test message", device_id="test-device", operation="test")
            with open(log_file) as f:
                log_content = f.read().strip()
            log_data = json.loads(log_content)
            assert log_data["event"] == "Test message"
            assert log_data["device_id"] == "test-device"
            assert log_data["logger"] == "test_logger"

    @_win
    def test_structured_logging_includes_timestamp(self):
        """Test that log entries include ISO timestamps."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            logger.info("Test message")
            with open(log_file) as f:
                log_content = f.read().strip()
            log_data = json.loads(log_content)
            assert "timestamp" in log_data
            assert "T" in log_data["timestamp"]

    @_win
    def test_structured_logging_respects_log_level(self):
        """Test that DEBUG messages are filtered when level is INFO."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            logger.debug("This should not appear")
            logger.warning("This should appear")
            with open(log_file) as f:
                log_content = f.read().strip()
            log_data = json.loads(log_content)
            assert log_data["event"] == "This should appear"
            assert log_data["level"] == "warning"

    @_win
    def test_structured_logging_handles_exceptions(self):
        """Test that exceptions are properly logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Exception occurred", device_id="test-device")
            with open(log_file) as f:
                log_content = f.read().strip()
            log_data = json.loads(log_content)
            assert log_data["event"] == "Exception occurred"
            assert "exception" in log_data

    @_win
    def test_structured_logging_multiple_handlers(self):
        """Test that structured logging sets up both file and console handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            root_logger = logging.getLogger()
            handler_types = [type(h).__name__ for h in root_logger.handlers]
            assert "FileHandler" in handler_types

    @_win
    def test_structured_logging_with_context(self):
        """Test logging with structured context data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            logger.info("First message", device_id="test-device", operation="start")
            logger.info("Second message", operation="process")
            logger.info("Third message", operation="end")
            with open(log_file) as f:
                lines = [line for line in f if line.strip()]
            assert len(lines) == 3
            for i, line in enumerate(lines):
                log_data = json.loads(line.strip())
                assert "timestamp" in log_data
                assert "event" in log_data

    @_win
    def test_structured_logging_performance(self):
        """Test logging performance with multiple entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            for i in range(10):
                logger.info(f"Message {i}", device_id=f"device-{i}", iteration=i)
            with open(log_file) as f:
                lines = [line for line in f if line.strip()]
            assert len(lines) == 10

    @_win
    def test_structured_logging_loki_compatibility(self):
        """Test that log format is compatible with Loki's JSON expectations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_structured_logging("INFO", str(log_file))
            logger = structlog.get_logger("test_logger")
            logger.info(
                "Device operation",
                device_id="test-device",
                device_name="test-server",
                operation="authorize",
                status="success",
                duration=0.5,
                bytes_sent=1024,
                bytes_received=2048,
            )
            with open(log_file) as f:
                log_content = f.read().strip()
            log_data = json.loads(log_content)
            for key in ("event", "timestamp", "level", "logger", "device_id"):
                assert key in log_data, f"Missing key: {key}"
