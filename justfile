set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Build ──────────────────────────────────────────────────────────────────────

# Build the PyInstaller backend .exe and copy to Tauri resources
build-sidecar:
    pwsh -NoProfile -File '{{justfile_directory()}}\native\build.ps1' -SidecarOnly

# Build the Tauri NSIS desktop installer (full pipeline: frontend → PyInstaller → Rust → NSIS)
build-native:
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    Set-Location '{{justfile_directory()}}\native'
    pwsh -NoProfile -File .\build.ps1

# Build Tauri native app (debug, skip PyInstaller)
build-native-debug:
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    Set-Location '{{justfile_directory()}}\native'
    npx @tauri-apps/cli build --debug

# Run CUA-NSIS smoke test (install → launch → verify → uninstall)
cua-nsis-test:
    uv run python scripts/cua-smoke.py

# ── Dev ────────────────────────────────────────────────────────────────────────

# Start webapp (backend + frontend)
serve:
    pwsh -NoProfile -File '{{justfile_directory()}}\start.ps1'

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome check --write .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check
