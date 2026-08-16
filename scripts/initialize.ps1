[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

foreach ($relative in @('raw', 'staging', 'reviews', 'wiki', '.local')) {
    $path = Join-Path $ProjectRoot $relative
    if (-not (Test-Path -LiteralPath $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
    }
}

$localConfig = Join-Path $ProjectRoot 'config/ima-ingest.local.json'
$exampleConfig = Join-Path $ProjectRoot 'config/ima-ingest.example.json'
if (-not (Test-Path -LiteralPath $localConfig)) {
    Copy-Item -LiteralPath $exampleConfig -Destination $localConfig
    Write-Host 'Created config/ima-ingest.local.json. Fill in your own ima knowledge-base name.'
} else {
    Write-Host 'Local ima configuration already exists; left unchanged.'
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

Write-Host 'Initialization complete.'
