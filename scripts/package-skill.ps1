[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SkillRoot = Join-Path $ProjectRoot '.agents/skills/ai-learning-llm-wiki'
$DistRoot = Join-Path $ProjectRoot 'dist'
$OutputZip = Join-Path $DistRoot 'ai-learning-llm-wiki.zip'

if (-not (Test-Path -LiteralPath (Join-Path $SkillRoot 'SKILL.md'))) {
    throw 'Skill entrypoint not found.'
}

if (-not (Test-Path -LiteralPath $DistRoot)) {
    New-Item -ItemType Directory -Path $DistRoot | Out-Null
}

if (Test-Path -LiteralPath $OutputZip) {
    Remove-Item -LiteralPath $OutputZip
}

$stagingRoot = Join-Path $DistRoot '.skill-package'
$packagedSkillRoot = Join-Path $stagingRoot 'ai-learning-llm-wiki'
if (Test-Path -LiteralPath $stagingRoot) {
    Remove-Item -LiteralPath $stagingRoot -Recurse
}
New-Item -ItemType Directory -Path $packagedSkillRoot | Out-Null

Get-ChildItem -LiteralPath $SkillRoot -Force | Where-Object {
    $_.Name -ne '__pycache__'
} | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $packagedSkillRoot -Recurse
}

Get-ChildItem -LiteralPath $packagedSkillRoot -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse
Get-ChildItem -LiteralPath $packagedSkillRoot -Recurse -File -Filter '*.pyc' | Remove-Item

Compress-Archive -LiteralPath $packagedSkillRoot -DestinationPath $OutputZip -CompressionLevel Optimal
Remove-Item -LiteralPath $stagingRoot -Recurse

Write-Host "Created $OutputZip"
