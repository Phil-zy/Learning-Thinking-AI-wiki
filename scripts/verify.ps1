[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SkillRoot = Join-Path $ProjectRoot '.agents/skills/ai-learning-llm-wiki'

Push-Location $ProjectRoot
try {
    $python = $null
    if (Get-Command python3 -ErrorAction SilentlyContinue) { $python = 'python3' }
    elseif (Get-Command py -ErrorAction SilentlyContinue) { $python = 'py' }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $python = 'python' }
    else { throw 'Python 3 is required.' }

    $prefix = @()
    if ($python -eq 'py') { $prefix = @('-3') }

    & $python @prefix "$SkillRoot/scripts/check_workflow.py" $ProjectRoot --phase repository
    if ($LASTEXITCODE -ne 0) { throw 'Repository workflow check failed.' }

    & $python @prefix "$SkillRoot/scripts/check_evidence.py" $ProjectRoot
    if ($LASTEXITCODE -ne 0) { throw 'Evidence check failed.' }

    & $python @prefix -m unittest discover -s "$SkillRoot/tests" -p 'test_*.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Skill tests failed.' }

    $forbidden = @(
        'automation-[0-9]{10,}',
        'Bearer\s+[A-Za-z0-9._-]{20,}',
        'github_pat_[A-Za-z0-9_]{20,}',
        'gh[pousr]_[A-Za-z0-9]{30,}',
        'sk-[A-Za-z0-9]{20,}',
        '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
    )

    $scanFiles = Get-ChildItem -LiteralPath $ProjectRoot -Recurse -File | Where-Object {
        $_.FullName -notmatch '[\\/]\.git[\\/]' -and
        $_.FullName -notmatch '[\\/]\.local[\\/]' -and
        $_.FullName -notmatch '[\\/]dist[\\/]' -and
        $_.FullName -notmatch '[\\/]__pycache__[\\/]' -and
        $_.FullName -ne $PSCommandPath -and
        $_.Name -ne 'ima-ingest.local.json'
    }
    foreach ($file in $scanFiles) {
        $content = Get-Content -Raw -Encoding UTF8 -ErrorAction SilentlyContinue $file.FullName
        foreach ($pattern in $forbidden) {
            if ($content -match $pattern) {
                throw "Possible private or secret value found in $($file.FullName)"
            }
        }
    }

    if (Test-Path -LiteralPath (Join-Path $ProjectRoot '.git')) {
        git diff --check
        if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed.' }
    } else {
        Write-Host 'Git repository not initialized; skipped git diff --check.'
    }

    Write-Host 'All verification checks passed.'
} finally {
    Pop-Location
}
