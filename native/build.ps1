$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoName = Split-Path -Leaf $Root
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"
New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null

Write-Host "=== ${RepoName} Tauri Release Build ===" -ForegroundColor Cyan

# Step 1: TypeScript lint gate + frontend build
$frontendDirs = @("web_sota", "webapp/frontend", "webapp")
foreach ($dir in $frontendDirs) {
    $frontend = Join-Path $Root $dir
    if (Test-Path "$frontend\package.json") {
        Write-Host "-> [1/4] Building frontend ($dir)..." -ForegroundColor Yellow
        Push-Location $frontend
        npm install --silent 2>$null

        Write-Host "  tsc --noEmit..." -ForegroundColor Gray
        $tscOut = npx tsc --noEmit 2>&1
        $tscExit = $LASTEXITCODE
        if ($tscExit -ne 0) {
            Write-Host "  TypeScript compilation FAILED - fix errors before building NSIS" -ForegroundColor Red
            Write-Host $tscOut
            throw "TypeScript compilation failed - fix all errors before building NSIS installer"
        }

        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
        Pop-Location
        break
    }
}

# Step 2: PyInstaller backend (onefile)
Write-Host "-> [2/4] PyInstaller backend..." -ForegroundColor Yellow
$specFile = "$Root\${RepoName}-backend.spec"
if (Test-Path $specFile) {
    Push-Location $Root
    # Patch fastmcp to not crash on missing metadata (dist-info stripped by spec)
    $fm = "$Root\.venv\Lib\site-packages\fastmcp\__init__.py"
    if (Test-Path $fm) {
        $c = Get-Content $fm -Raw
        $alreadyPatched = $c -match 'PackageNotFoundError'
        if (-not $alreadyPatched) {
            $c = $c -replace 'from importlib.metadata import version as _version', 'from importlib.metadata import version as _version, PackageNotFoundError'
            $c = $c -replace '__version__ = _version\("fastmcp"\)', 'try:
    __version__ = _version("fastmcp")
except PackageNotFoundError:
    __version__ = "0.0.0"'
            Set-Content $fm -Value $c -Encoding utf8
            Write-Host "  Patched fastmcp for frozen exe" -ForegroundColor Yellow
        } else {
            Write-Host "  fastmcp already patched, skipping" -ForegroundColor Gray
        }
    }
    # Patch pydantic networks module to handle missing email-validator metadata in frozen exe
    $pyd = "$Root\.venv\Lib\site-packages\pydantic\networks.py"
    if (Test-Path $pyd) {
        $c = Get-Content $pyd -Raw
        $alreadyPatchedPyd = $c -match '(?s)email.*validator.*except Exception'
        if (-not $alreadyPatchedPyd) {
            $c = $c -replace "    if not version\('email-validator'\)\.partition\('\.'\)\[0\] == '2':", "    try:
        if not version('email-validator').partition('.')[0] == '2':"
            $c = $c -replace "        raise ImportError\('email-validator version >= 2.0 required, run pip install -U email-validator'\)", "            raise ImportError('email-validator version >= 2.0 required, run pip install -U email-validator')
    except Exception:
        pass"
            Set-Content $pyd -Value $c -Encoding utf8
            Write-Host "  Patched pydantic for email-validator metadata fallback" -ForegroundColor Yellow
        } else {
            Write-Host "  pydantic email-validator already patched, skipping" -ForegroundColor Gray
        }
    }
    uv run pyinstaller "$specFile" --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
    Pop-Location
} else {
    Write-Host "  WARNING: spec file not found at $specFile - using existing backend exe if present" -ForegroundColor DarkYellow
}

# Step 3: Embed in Tauri resources (+ dev fallback)
Write-Host "-> [3/4] Embedding backend..." -ForegroundColor Yellow
$src = "$Root\dist\${RepoName}-backend.exe"
if (-not (Test-Path $src)) { throw "Backend exe not found at $src - PyInstaller step failed" }
Copy-Item $src "$ResourceDir\${RepoName}-backend.exe" -Force
Copy-Item $src "$DevDir\${RepoName}-backend-$Triple.exe" -Force
Write-Host "  Backend exe: $((Get-Item $src).Length / 1MB) MB" -ForegroundColor Green

# Bundle .env.example from repo root (NOT .env - .env has live API keys)
$envExampleSrc = "$Root\.env.example"
if (Test-Path $envExampleSrc) {
    Copy-Item $envExampleSrc "$ResourceDir\.env.example" -Force
    Write-Host "  Bundled .env.example ($((Get-Item $envExampleSrc).Length) bytes) - NOT .env" -ForegroundColor Green
} else {
    Write-Host "  WARNING: .env.example not found at repo root - create one for reference" -ForegroundColor DarkYellow
    Set-Content -Path "$ResourceDir\.env.example" -Value "# Copy this file to .env and fill in your credentials" -Encoding utf8
}

# Step 4: Single NSIS installer
Write-Host "-> [4/4] Tauri NSIS bundle..." -ForegroundColor Yellow
Push-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
npx @tauri-apps/cli build --bundles nsis
if ($LASTEXITCODE -ne 0) { throw "Tauri build failed with exit code $LASTEXITCODE" }
Pop-Location

# Stage to repo dist/
$distDir = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$nsisDir = "$PSScriptRoot\target\release\bundle\nsis"
if (Test-Path $nsisDir) { Copy-Item "$nsisDir\*-setup.exe" "$distDir\" -Force }
$strayExe = "$PSScriptRoot\target\release\tailscale-mcp-backend.exe"
if (Test-Path $strayExe) { Remove-Item $strayExe -Force; Write-Host "  Cleaned stray: $strayExe" -ForegroundColor DarkGray }

Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "Ship: $nsisDir\*.exe"
