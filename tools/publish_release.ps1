$ErrorActionPreference = 'Stop'

# Portable gh path detection
$gh = (Get-ChildItem -Recurse (Join-Path (Get-Location) 'tools/gh') -Filter gh.exe | Select-Object -First 1).FullName
if (-not $gh) { throw 'GitHub CLI (gh.exe) not found under tools/gh' }

param(
  [string]$Tag = "bert-arabic-phoneme-$(Get-Date -Format yyyyMMdd)",
  [string]$Title = $Tag,
  [string]$Notes = "Automated release"
)

$repo = "salemqundil/Eqratech_Arabic_Diana_Project"
$artDir = Join-Path (Get-Location) 'artifacts'
if (-not (Test-Path $artDir)) { throw "Artifacts directory not found: $artDir" }

$assets = Get-ChildItem $artDir -Filter *.zip | Select-Object -ExpandProperty FullName
if (-not $assets -or $assets.Count -eq 0) { throw "No zip assets found under $artDir" }

& $gh release create $Tag --repo $repo --title $Title --notes $Notes --draft --target main @assets
Write-Host "Draft release '$Tag' created with assets:" -ForegroundColor Green
$assets | ForEach-Object { Write-Host " - $_" }
