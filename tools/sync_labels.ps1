$ErrorActionPreference = 'Stop'

# Requires: authenticated gh (gh auth login)
$repo = "salemqundil/Eqratech_Arabic_Diana_Project"
$labelsFile = Join-Path (Get-Location) '.github/labels.yml'
if (-not (Test-Path $labelsFile)) { throw "labels.yml not found: $labelsFile" }

# Create/update labels from YAML
& (Get-Command gh).Source label import --repo $repo $labelsFile
Write-Host "Labels synced from $labelsFile to $repo" -ForegroundColor Green
