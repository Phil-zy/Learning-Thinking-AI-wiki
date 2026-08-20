[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

foreach ($relative in @('raw', 'staging', 'reviews', 'wiki')) {
    $path = Join-Path $ProjectRoot $relative
    if (-not (Test-Path -LiteralPath $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    Push-Location $ProjectRoot
    try {
        if (Test-Path -LiteralPath (Join-Path $ProjectRoot '.git')) {
            git config core.hooksPath .githooks
            Write-Host 'Configured Git hooks path: .githooks'
        } else {
            Write-Host 'Git repository not initialized; skipped hook configuration.'
        }
    } finally {
        Pop-Location
    }
}

Write-Host 'Core workspace initialization complete. Optional integrations have separate setup instructions.'
