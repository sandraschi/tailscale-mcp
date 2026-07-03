"""PyInstaller entry point."""
import _datetime  # noqa: F401
import _strptime  # noqa: F401
import logging
import os
import sys
import traceback

sys.path.insert(0, "src")

# PyInstaller console=False sets sys.stderr=None, which crashes uvicorn's
# AccessFormatter on isatty(). Replace with devnull to survive.
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

try:
    import uvicorn

    from tailscalemcp.server import app
except Exception:
    logging.basicConfig(level=logging.ERROR, format="%(message)s", stream=sys.stderr)
    logging.error("FATAL: server import failed — missing module or dependency")
    logging.error(traceback.format_exc())
    sys.exit(1)

port = int(os.environ.get("PORT", os.environ.get("MCP_PORT", "10821")))
uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

