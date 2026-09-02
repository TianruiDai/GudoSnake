#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Test-WslInstalled {
    try {
        $null = wsl -l -v 2>$null
        return $true
    } catch {
        return $false
    }
}

Write-Host "Gudo Snake - Android APK builder" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option A - Install Docker Desktop, then run:" -ForegroundColor White
    Write-Host "  bash build-android.sh" -ForegroundColor Green
    Write-Host ""
    Write-Host "Option B - Install WSL2 (Ubuntu), then in WSL run:" -ForegroundColor White
    Write-Host "  wsl --install" -ForegroundColor Green
    Write-Host "  # restart PC, open Ubuntu, then:" -ForegroundColor Gray
    Write-Host "  cd /mnt/c/Users/Matri/pytorch_env/pygame/gudosnake" -ForegroundColor Green
    Write-Host "  bash wsl-setup.sh" -ForegroundColor Green
    Write-Host "  buildozer -v android debug" -ForegroundColor Green
    Write-Host ""
    Write-Host "See ANDROID_BUILD.md for full WSL + release signing steps." -ForegroundColor Cyan
    exit 1
}

Write-Host "Docker detected. Starting build via bash..." -ForegroundColor Green
bash "$Root/build-android.sh"
