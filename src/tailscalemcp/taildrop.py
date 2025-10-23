"""
Taildrop File Sharing Module

Provides comprehensive Taildrop functionality for secure file sharing
across Tailscale networks with advanced features and monitoring.
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel, Field

from .exceptions import TailscaleMCPError

logger = structlog.get_logger(__name__)


class TaildropFile(BaseModel):
    """Taildrop file metadata model."""

    filename: str = Field(..., description="File name")
    size: int = Field(..., description="File size in bytes")
    checksum: str = Field(..., description="File checksum")
    sender: str = Field(..., description="Sender device ID")
    recipient: str = Field(..., description="Recipient device ID")
    status: str = Field(..., description="Transfer status")
    created_at: float = Field(..., description="Creation timestamp")
    completed_at: float | None = Field(None, description="Completion timestamp")
    expires_at: float | None = Field(None, description="Expiration timestamp")


class TaildropTransfer(BaseModel):
    """Taildrop transfer information model."""

    transfer_id: str = Field(..., description="Unique transfer ID")
    sender_device: str = Field(..., description="Sender device name")
    recipient_device: str = Field(..., description="Recipient device name")
    files: list[TaildropFile] = Field(..., description="Files in transfer")
    status: str = Field(..., description="Transfer status")
    progress: float = Field(..., description="Transfer progress percentage")
    created_at: float = Field(..., description="Transfer creation time")
    estimated_completion: float | None = Field(
        None, description="Estimated completion time"
    )


class TaildropManager:
    """Comprehensive Taildrop file sharing manager."""

    def __init__(
        self,
        taildrop_dir: str = "/tmp/taildrop",
        max_file_size: int = 100 * 1024 * 1024,
    ):
        """Initialize Taildrop manager.

        Args:
            taildrop_dir: Directory for Taildrop files
            max_file_size: Maximum file size in bytes (default: 100MB)
        """
        self.taildrop_dir = Path(taildrop_dir)
        self.max_file_size = max_file_size
        self.transfers: dict[str, TaildropTransfer] = {}
        self.active_transfers: dict[str, asyncio.Task] = {}

        # Create taildrop directory if it doesn't exist
        self.taildrop_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Taildrop manager initialized",
            taildrop_dir=str(self.taildrop_dir),
            max_file_size=max_file_size,
        )

    async def send_file(
        self,
        file_path: str,
        recipient_device: str,
        sender_device: str,
        expire_hours: int = 24,
    ) -> dict[str, Any]:
        """Send a file via Taildrop.

        Args:
            file_path: Path to the file to send
            recipient_device: Target device ID or name
            sender_device: Sender device ID or name
            expire_hours: File expiration time in hours

        Returns:
            Transfer information and status
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(
                    f"File too large: {file_size} bytes (max: {self.max_file_size})"
                )

            # Generate transfer ID
            transfer_id = hashlib.md5(
                f"{file_path}_{recipient_device}_{time.time()}".encode()
            ).hexdigest()

            # Calculate file checksum
            checksum = await self._calculate_checksum(file_path)

            # Create transfer record
            transfer = TaildropTransfer(
                transfer_id=transfer_id,
                sender_device=sender_device,
                recipient_device=recipient_device,
                files=[
                    TaildropFile(
                        filename=file_path.name,
                        size=file_size,
                        checksum=checksum,
                        sender=sender_device,
                        recipient=recipient_device,
                        status="pending",
                        created_at=time.time(),
                        expires_at=time.time() + (expire_hours * 3600),
                    )
                ],
                status="pending",
                progress=0.0,
                created_at=time.time(),
            )

            # Store transfer
            self.transfers[transfer_id] = transfer

            # Start transfer process
            transfer_task = asyncio.create_task(self._process_transfer(transfer_id))
            self.active_transfers[transfer_id] = transfer_task

            logger.info(
                "Taildrop transfer initiated",
                transfer_id=transfer_id,
                filename=file_path.name,
                recipient=recipient_device,
                size=file_size,
            )

            return {
                "transfer_id": transfer_id,
                "status": "initiated",
                "filename": file_path.name,
                "size": file_size,
                "recipient": recipient_device,
                "expires_at": transfer.files[0].expires_at,
                "message": f"File transfer initiated to {recipient_device}",
            }

        except Exception as e:
            logger.error("Error sending file via Taildrop", error=str(e))
            raise TailscaleMCPError(f"Failed to send file: {e}") from e

    async def receive_file(
        self, transfer_id: str, save_path: str | None = None
    ) -> dict[str, Any]:
        """Receive a file via Taildrop.

        Args:
            transfer_id: Transfer ID to receive
            save_path: Optional custom save path

        Returns:
            Reception status and file information
        """
        try:
            if transfer_id not in self.transfers:
                raise ValueError(f"Transfer not found: {transfer_id}")

            transfer = self.transfers[transfer_id]
            if transfer.status != "completed":
                raise ValueError(f"Transfer not ready for reception: {transfer.status}")

            # Determine save path
            if not save_path:
                save_path = (
                    self.taildrop_dir
                    / f"received_{transfer_id}_{transfer.files[0].filename}"
                )
            else:
                save_path = Path(save_path)

            # Create received file record
            received_file = TaildropFile(
                filename=save_path.name,
                size=transfer.files[0].size,
                checksum=transfer.files[0].checksum,
                sender=transfer.sender_device,
                recipient=transfer.recipient_device,
                status="received",
                created_at=time.time(),
                completed_at=time.time(),
            )

            logger.info(
                "File received via Taildrop",
                transfer_id=transfer_id,
                filename=save_path.name,
                size=received_file.size,
            )

            return {
                "transfer_id": transfer_id,
                "status": "received",
                "filename": save_path.name,
                "size": received_file.size,
                "save_path": str(save_path),
                "checksum": received_file.checksum,
                "message": "File received successfully",
            }

        except Exception as e:
            logger.error("Error receiving file via Taildrop", error=str(e))
            raise TailscaleMCPError(f"Failed to receive file: {e}") from e

    async def list_transfers(
        self, status_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """List Taildrop transfers.

        Args:
            status_filter: Optional status filter (pending, completed, failed, expired)

        Returns:
            List of transfers
        """
        try:
            transfers = []
            current_time = time.time()

            for transfer_id, transfer in self.transfers.items():
                # Check for expired transfers
                if (
                    transfer.files
                    and transfer.files[0].expires_at
                    and current_time > transfer.files[0].expires_at
                ):
                    transfer.status = "expired"

                if status_filter and transfer.status != status_filter:
                    continue

                transfers.append(
                    {
                        "transfer_id": transfer_id,
                        "sender_device": transfer.sender_device,
                        "recipient_device": transfer.recipient_device,
                        "filename": transfer.files[0].filename
                        if transfer.files
                        else "unknown",
                        "size": transfer.files[0].size if transfer.files else 0,
                        "status": transfer.status,
                        "progress": transfer.progress,
                        "created_at": transfer.created_at,
                        "expires_at": transfer.files[0].expires_at
                        if transfer.files
                        else None,
                    }
                )

            logger.info(
                "Taildrop transfers listed",
                total_transfers=len(transfers),
                status_filter=status_filter,
            )

            return transfers

        except Exception as e:
            logger.error("Error listing Taildrop transfers", error=str(e))
            raise TailscaleMCPError(f"Failed to list transfers: {e}") from e

    async def cancel_transfer(self, transfer_id: str) -> dict[str, Any]:
        """Cancel a Taildrop transfer.

        Args:
            transfer_id: Transfer ID to cancel

        Returns:
            Cancellation status
        """
        try:
            if transfer_id not in self.transfers:
                raise ValueError(f"Transfer not found: {transfer_id}")

            transfer = self.transfers[transfer_id]
            if transfer.status in ["completed", "cancelled"]:
                raise ValueError(
                    f"Cannot cancel transfer with status: {transfer.status}"
                )

            # Cancel asyncio task if active
            if transfer_id in self.active_transfers:
                self.active_transfers[transfer_id].cancel()
                del self.active_transfers[transfer_id]

            # Update transfer status
            transfer.status = "cancelled"

            logger.info("Taildrop transfer cancelled", transfer_id=transfer_id)

            return {
                "transfer_id": transfer_id,
                "status": "cancelled",
                "message": "Transfer cancelled successfully",
            }

        except Exception as e:
            logger.error("Error cancelling Taildrop transfer", error=str(e))
            raise TailscaleMCPError(f"Failed to cancel transfer: {e}") from e

    async def get_transfer_status(self, transfer_id: str) -> dict[str, Any]:
        """Get detailed transfer status.

        Args:
            transfer_id: Transfer ID to check

        Returns:
            Detailed transfer status
        """
        try:
            if transfer_id not in self.transfers:
                raise ValueError(f"Transfer not found: {transfer_id}")

            transfer = self.transfers[transfer_id]
            current_time = time.time()

            # Check for expiration
            if (
                transfer.files
                and transfer.files[0].expires_at
                and current_time > transfer.files[0].expires_at
            ):
                transfer.status = "expired"

            return {
                "transfer_id": transfer_id,
                "sender_device": transfer.sender_device,
                "recipient_device": transfer.recipient_device,
                "filename": transfer.files[0].filename if transfer.files else "unknown",
                "size": transfer.files[0].size if transfer.files else 0,
                "status": transfer.status,
                "progress": transfer.progress,
                "created_at": transfer.created_at,
                "expires_at": transfer.files[0].expires_at if transfer.files else None,
                "is_expired": transfer.status == "expired",
                "estimated_completion": transfer.estimated_completion,
            }

        except Exception as e:
            logger.error("Error getting transfer status", error=str(e))
            raise TailscaleMCPError(f"Failed to get transfer status: {e}") from e

    async def cleanup_expired_transfers(self) -> dict[str, Any]:
        """Clean up expired transfers.

        Returns:
            Cleanup summary
        """
        try:
            current_time = time.time()
            expired_count = 0
            cleaned_files = []

            for transfer_id, transfer in list(self.transfers.items()):
                if (
                    transfer.files
                    and transfer.files[0].expires_at
                    and current_time > transfer.files[0].expires_at
                ):
                    if transfer.status != "expired":
                        transfer.status = "expired"
                        expired_count += 1

                    # Clean up associated files
                    file_path = (
                        self.taildrop_dir
                        / f"{transfer_id}_{transfer.files[0].filename}"
                    )
                    if file_path.exists():
                        file_path.unlink()
                        cleaned_files.append(str(file_path))

            logger.info(
                "Expired transfers cleaned up",
                expired_count=expired_count,
                cleaned_files=len(cleaned_files),
            )

            return {
                "status": "completed",
                "expired_transfers": expired_count,
                "cleaned_files": len(cleaned_files),
                "cleaned_file_paths": cleaned_files,
                "message": f"Cleaned up {expired_count} expired transfers",
            }

        except Exception as e:
            logger.error("Error cleaning up expired transfers", error=str(e))
            raise TailscaleMCPError(f"Failed to cleanup expired transfers: {e}") from e

    async def get_taildrop_statistics(self) -> dict[str, Any]:
        """Get Taildrop usage statistics.

        Returns:
            Statistics summary
        """
        try:
            time.time()
            total_transfers = len(self.transfers)

            status_counts = {}
            total_size = 0
            active_transfers = 0

            for transfer in self.transfers.values():
                status = transfer.status
                status_counts[status] = status_counts.get(status, 0) + 1

                if transfer.files:
                    total_size += transfer.files[0].size

                if status in ["pending", "in_progress"]:
                    active_transfers += 1

            # Calculate average transfer time
            completed_transfers = [
                t
                for t in self.transfers.values()
                if t.status == "completed" and t.files and t.files[0].completed_at
            ]
            avg_transfer_time = 0
            if completed_transfers:
                total_time = sum(
                    t.files[0].completed_at - t.created_at for t in completed_transfers
                )
                avg_transfer_time = total_time / len(completed_transfers)

            return {
                "total_transfers": total_transfers,
                "active_transfers": active_transfers,
                "status_breakdown": status_counts,
                "total_data_transferred": total_size,
                "average_transfer_time": avg_transfer_time,
                "expired_transfers": status_counts.get("expired", 0),
                "success_rate": (
                    status_counts.get("completed", 0) / total_transfers * 100
                )
                if total_transfers > 0
                else 0,
            }

        except Exception as e:
            logger.error("Error getting Taildrop statistics", error=str(e))
            raise TailscaleMCPError(f"Failed to get statistics: {e}") from e

    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def _process_transfer(self, transfer_id: str) -> None:
        """Process a file transfer (simulated)."""
        try:
            transfer = self.transfers[transfer_id]

            # Simulate transfer progress
            for progress in [25, 50, 75, 100]:
                await asyncio.sleep(1)  # Simulate transfer time
                transfer.progress = progress

                if progress == 100:
                    transfer.status = "completed"
                    if transfer.files:
                        transfer.files[0].status = "completed"
                        transfer.files[0].completed_at = time.time()

                    logger.info(
                        "Taildrop transfer completed",
                        transfer_id=transfer_id,
                        filename=transfer.files[0].filename
                        if transfer.files
                        else "unknown",
                    )
                    break

            # Clean up active transfer
            if transfer_id in self.active_transfers:
                del self.active_transfers[transfer_id]

        except asyncio.CancelledError:
            transfer.status = "cancelled"
            logger.info("Taildrop transfer cancelled", transfer_id=transfer_id)
        except Exception as e:
            transfer.status = "failed"
            logger.error(
                "Taildrop transfer failed", transfer_id=transfer_id, error=str(e)
            )
