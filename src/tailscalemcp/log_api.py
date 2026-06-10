"""
REST API helpers for the webapp log viewer.
Reads the rotating JSONL log file and exposes search/tail/export/status.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_LOG_PATH = Path(os.getenv("LOG_FILE", "logs/tailscale-mcp.log"))


def _iter_logs(lines: int = 0) -> list[dict[str, Any]]:
    """Read the last N lines from the current log file.

    When lines=0 returns all lines.  Reads the active file and any
    rotated backups (tailscale-mcp.log.1, .2, …) to satisfy the count.
    """
    results: list[dict[str, Any]] = []
    files: list[Path] = []
    if _LOG_PATH.exists():
        files.append(_LOG_PATH)
    for i in range(1, 6):
        p = _LOG_PATH.with_suffix(f".log.{i}")
        if p.exists():
            files.append(p)

    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        except OSError:
            pass

    if lines > 0:
        results = results[-lines:]

    return results


def _parse_level(level: str | int) -> int:
    """Map string level to numeric for filtering."""
    if isinstance(level, int):
        return level
    m = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "WARN": 30, "INFO": 20, "DEBUG": 10}
    return m.get(level.upper(), 0)


def filter_logs(
    lines: int = 200,
    min_level: str | None = None,
    logger_name: str | None = None,
    search: str | None = None,
    tail: bool = True,
    offset: int = 0,
) -> dict[str, Any]:
    """Read log file(s) and return filtered, sorted results."""
    raw = _iter_logs(lines=0 if not tail else lines + offset)

    # level filter
    if min_level:
        numeric = _parse_level(min_level)
        raw = [
            e for e in raw if isinstance(e.get("level"), str) and _parse_level(e["level"]) >= numeric
        ]

    if logger_name:
        raw = [e for e in raw if (e.get("logger") or "").startswith(logger_name)]

    if search:
        q = search.lower()
        raw = [
            e
            for e in raw
            if q in (e.get("event") or "").lower()
            or q in (e.get("logger") or "").lower()
            or any(q in str(v).lower() for v in e.values())
        ]

    total = len(raw)

    if tail:
        if offset > 0 and offset < total:
            raw = raw[-offset:]
        raw = raw[-lines:]

    return {
        "total": total,
        "returned": len(raw),
        "lines": raw,
        "log_file": str(_LOG_PATH.resolve()),
        "file_size_bytes": _LOG_PATH.stat().st_size if _LOG_PATH.exists() else 0,
    }


def get_status() -> dict[str, Any]:
    """Log file rotation and size status."""
    files: list[dict[str, Any]] = []
    total_bytes = 0
    total_lines = 0
    for i in range(6):
        p = _LOG_PATH.with_suffix(f".log.{i}") if i > 0 else _LOG_PATH
        if p.exists():
            s = p.stat()
            files.append({"name": p.name, "size_bytes": s.st_size})
            total_bytes += s.st_size

    raw = _iter_logs()
    total_lines = len(raw)

    return {
        "log_file": str(_LOG_PATH.resolve()),
        "files": files,
        "total_bytes": total_bytes,
        "total_lines": total_lines,
        "rotation": {
            "max_bytes": 10 * 1024 * 1024,
            "backup_count": 5,
            "encoding": "utf-8",
        },
    }


def export_logs(
    format: str = "jsonl",
    min_level: str | None = None,
    logger_name: str | None = None,
    search: str | None = None,
) -> str:
    """Export filtered logs as a string."""
    result = filter_logs(lines=10000, min_level=min_level, logger_name=logger_name, search=search, tail=False)
    entries = result["lines"]

    if format == "jsonl":
        return "\n".join(json.dumps(e) for e in entries)

    # Plain text format
    out: list[str] = []
    for e in entries:
        ts = e.get("timestamp", "")
        lvl = e.get("level", "")
        evt = e.get("event", "")
        log = e.get("logger", "")
        out.append(f"[{ts}] [{lvl}] [{log}] {evt}")
    return "\n".join(out)
