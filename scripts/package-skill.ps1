[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DistRoot = Join-Path $ProjectRoot 'dist'
$SkillNames = @('ai-learning-llm-wiki', 'ai-thinking-writing')

if (-not (Test-Path -LiteralPath $DistRoot)) {
    New-Item -ItemType Directory -Path $DistRoot | Out-Null
}

foreach ($skillName in $SkillNames) {
    $skillRoot = Join-Path $ProjectRoot ".agents/skills/$skillName"
    $entrypoint = Join-Path $skillRoot 'SKILL.md'
    $outputZip = Join-Path $DistRoot "$skillName.zip"
    $stagingRoot = Join-Path $DistRoot ".skill-package-$skillName"
    $packagedSkillRoot = Join-Path $stagingRoot $skillName

    if (-not (Test-Path -LiteralPath $entrypoint)) {
        throw "Skill entrypoint not found: $entrypoint"
    }

    if (Test-Path -LiteralPath $outputZip) {
        Remove-Item -LiteralPath $outputZip
    }
    if (Test-Path -LiteralPath $stagingRoot) {
        Remove-Item -LiteralPath $stagingRoot -Recurse
    }

    New-Item -ItemType Directory -Path $packagedSkillRoot | Out-Null

    Get-ChildItem -LiteralPath $skillRoot -Force | Where-Object {
        $_.Name -ne '__pycache__'
    } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $packagedSkillRoot -Recurse
    }

    Get-ChildItem -LiteralPath $packagedSkillRoot -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse
    Get-ChildItem -LiteralPath $packagedSkillRoot -Recurse -File -Filter '*.pyc' | Remove-Item

    Compress-Archive -LiteralPath $packagedSkillRoot -DestinationPath $outputZip -CompressionLevel Optimal
    Remove-Item -LiteralPath $stagingRoot -Recurse

    Write-Host "Created $outputZip"
}
