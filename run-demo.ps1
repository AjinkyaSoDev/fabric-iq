#requires -Version 5.1
<#
    Runs the full Fabric IQ synthetic data demo locally:
      1. Generate bronze
      2. Build silver + gold
      3. Run pytest smoke tests
#>
param(
    [int]$Days = 14
)

$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path .\.venv)) {
        Write-Host "Creating virtual environment..." -ForegroundColor Cyan
        python -m venv .venv
    }
    & .\.venv\Scripts\Activate.ps1

    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet

    Write-Host "`n[1/3] Generating bronze synthetic data ($Days days)..." -ForegroundColor Green
    python -m synth.run_generate --days $Days

    Write-Host "`n[2/3] Building silver + gold layers..." -ForegroundColor Green
    python lakehouse\build.py

    Write-Host "`n[3/3] Running quality tests..." -ForegroundColor Green
    pytest tests -q

    Write-Host "`nDone. Gold layer at: $(Resolve-Path .\lakehouse\gold)" -ForegroundColor Green
}
finally {
    Pop-Location
}
