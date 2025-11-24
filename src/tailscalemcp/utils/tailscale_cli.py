"""
Tailscale CLI Integration Utility

Provides async wrapper for Tailscale CLI commands with proper error handling
and output parsing for Taildrop and Funnel operations.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

import structlog

from tailscalemcp.exceptions import ConfigurationError, TailscaleMCPError

logger = structlog.get_logger(__name__)


class TailscaleCLI:
    """Async wrapper for Tailscale CLI commands."""

    def __init__(self, tailscale_binary: str | None = None, timeout: int = 60):
        """Initialize Tailscale CLI wrapper.

        Args:
            tailscale_binary: Path to tailscale binary (default: 'tailscale' in PATH)
            timeout: Command timeout in seconds (default: 60)
        """
        self.tailscale_binary = tailscale_binary or self._find_tailscale_binary()
        self.timeout = timeout

        if not self.tailscale_binary:
            logger.warning(
                "Tailscale CLI not found in PATH. Some features may not work.",
                hint="Install Tailscale CLI or set TAILSCALE_BINARY environment variable",
            )

    def _find_tailscale_binary(self) -> str | None:
        """Find tailscale binary in PATH.

        Returns:
            Path to tailscale binary or None if not found
        """
        # Check common locations
        common_paths = [
            "tailscale",  # In PATH
            "C:\\Program Files\\Tailscale\\tailscale.exe",  # Windows default
            "/usr/bin/tailscale",  # Linux
            "/usr/local/bin/tailscale",  # macOS/Linux
            "/Applications/Tailscale.app/Contents/MacOS/Tailscale",  # macOS app
        ]

        for path in common_paths:
            try:
                # Try to run 'tailscale version' to verify it works
                result = subprocess.run(
                    [path, "version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    logger.info("Tailscale CLI found", path=path)
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                continue

        return None

    async def _run_command(
        self,
        command: list[str],
        check: bool = True,
        capture_output: bool = True,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a Tailscale CLI command asynchronously.

        Args:
            command: Command and arguments as list
            check: Raise exception on non-zero exit code
            capture_output: Capture stdout and stderr
            timeout: Command timeout in seconds (default: self.timeout)

        Returns:
            CompletedProcess with stdout, stderr, and returncode

        Raises:
            TailscaleMCPError: If command fails and check=True
            ConfigurationError: If Tailscale CLI is not available
        """
        if not self.tailscale_binary:
            raise ConfigurationError(
                "Tailscale CLI not found. Please install Tailscale CLI or set "
                "TAILSCALE_BINARY environment variable."
            )

        full_command = [self.tailscale_binary, *command]
        timeout = timeout or self.timeout

        logger.debug("Running Tailscale CLI command", command=" ".join(full_command))

        try:
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            stdout_text = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""

            result = subprocess.CompletedProcess(
                full_command,
                process.returncode,
                stdout_text,
                stderr_text,
            )

            if check and result.returncode != 0:
                error_msg = stderr_text or stdout_text or "Unknown error"
                logger.error(
                    "Tailscale CLI command failed",
                    command=" ".join(full_command),
                    returncode=result.returncode,
                    stderr=stderr_text,
                )
                raise TailscaleMCPError(
                    f"Tailscale CLI command failed: {error_msg}",
                    code=result.returncode,
                )

            return result

        except TimeoutError:
            logger.error(
                "Tailscale CLI command timed out",
                command=" ".join(full_command),
                timeout=timeout,
            )
            raise TailscaleMCPError(
                f"Tailscale CLI command timed out after {timeout} seconds",
                code=124,
            ) from None
        except Exception as e:
            logger.error(
                "Error running Tailscale CLI command",
                command=" ".join(full_command),
                error=str(e),
            )
            raise TailscaleMCPError(f"Failed to run Tailscale CLI command: {e}") from e

    async def status(self) -> dict[str, Any]:
        """Get Tailscale status.

        Returns:
            Parsed status information
        """
        try:
            result = await self._run_command(["status", "--json"])
            status_data = json.loads(result.stdout)
            return status_data
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Tailscale status JSON", error=str(e))
            raise TailscaleMCPError("Failed to parse Tailscale status") from e

    async def file_send(
        self, file_path: str, recipient: str, wait: bool = True
    ) -> dict[str, Any]:
        """Send a file via Taildrop.

        Args:
            file_path: Path to file to send
            recipient: Recipient device name or IP
            wait: Wait for transfer to complete

        Returns:
            Transfer result information
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        command = ["file", "send", str(file_path_obj.absolute()), recipient]
        if wait:
            command.append("--wait")

        try:
            result = await self._run_command(
                command, timeout=300
            )  # 5 min timeout for large files
            return {
                "success": True,
                "file_path": str(file_path_obj.absolute()),
                "recipient": recipient,
                "output": result.stdout.strip(),
            }
        except TailscaleMCPError as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path_obj.absolute()),
                "recipient": recipient,
            }

    async def file_receive(
        self, save_path: str | None = None, accept_all: bool = False
    ) -> dict[str, Any]:
        """Receive files via Taildrop.

        Args:
            save_path: Optional directory to save received files
            accept_all: Accept all pending files automatically

        Returns:
            Reception result information
        """
        command = ["file", "get"]
        if save_path:
            command.extend(["--destination", save_path])
        if accept_all:
            command.append("--accept-all")

        try:
            result = await self._run_command(command)
            return {
                "success": True,
                "output": result.stdout.strip(),
                "save_path": save_path,
            }
        except TailscaleMCPError as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def funnel_status(self) -> dict[str, Any]:
        """Get Funnel status.

        Returns:
            Funnel status information
        """
        try:
            result = await self._run_command(["funnel", "status", "--json"])
            if result.stdout.strip():
                return json.loads(result.stdout)
            return {"active": False, "funnels": []}
        except json.JSONDecodeError:
            # If JSON parsing fails, try text parsing
            result = await self._run_command(["funnel", "status"])
            return {
                "active": "active" in result.stdout.lower(),
                "output": result.stdout.strip(),
            }

    async def funnel_enable(
        self, port: int, allow_tcp: bool = True, allow_tls: bool = True
    ) -> dict[str, Any]:
        """Enable Funnel for a port.

        Args:
            port: Port number to expose
            allow_tcp: Allow TCP connections
            allow_tls: Allow TLS connections

        Returns:
            Funnel enable result with public URL
        """
        command = ["funnel", str(port)]
        if not allow_tcp:
            command.append("--tcp=false")
        if not allow_tls:
            command.append("--tls=false")

        try:
            result = await self._run_command(command)
            # Parse output to extract public URL
            output = result.stdout.strip()
            url = None
            for line in output.split("\n"):
                if "https://" in line or "http://" in line:
                    url = line.strip()
                    break

            return {
                "success": True,
                "port": port,
                "public_url": url,
                "output": output,
            }
        except TailscaleMCPError as e:
            return {
                "success": False,
                "error": str(e),
                "port": port,
            }

    async def funnel_disable(self, port: int | None = None) -> dict[str, Any]:
        """Disable Funnel.

        Args:
            port: Optional specific port to disable (disables all if None)

        Returns:
            Funnel disable result
        """
        command = ["funnel", "--off", str(port)] if port else ["funnel", "--off"]

        try:
            result = await self._run_command(command)
            return {
                "success": True,
                "port": port,
                "output": result.stdout.strip(),
            }
        except TailscaleMCPError as e:
            return {
                "success": False,
                "error": str(e),
                "port": port,
            }

    async def version(self) -> dict[str, Any]:
        """Get Tailscale version.

        Returns:
            Version information
        """
        try:
            result = await self._run_command(["version"])
            return {
                "version": result.stdout.strip(),
                "binary": self.tailscale_binary,
            }
        except TailscaleMCPError as e:
            return {
                "error": str(e),
                "binary": self.tailscale_binary,
            }
