$ErrorActionPreference = 'Stop'

# Portable gh path detection
$gh = (Get-ChildItem -Recurse (Join-Path (Get-Location) 'tools/gh') -Filter gh.exe | Select-Object -First 1).FullName
if (-not $gh) { $gh = (Get-Command gh -ErrorAction SilentlyContinue).Source }
if (-not $gh) { throw 'GitHub CLI (gh) not found. Please run gh auth login first.' }

param(
  [string]$Repo = 'salemqundil/Eqratech_Arabic_Diana_Project',
  [string]$Branch = 'main',
  [int]$RequiredApprovals = 1,
  [string[]]$RequiredChecks = @('Python CI (syntax + tokenizer smoke)')
)

# Build branch protection payload
$payload = @{
  required_status_checks = @{
    strict = $true
    contexts = $RequiredChecks
  }
  enforce_admins = $true
  required_pull_request_reviews = @{
    required_approving_review_count = $RequiredApprovals
    dismiss_stale_reviews = $true
  }
  restrictions = $null
  required_linear_history = $true
  allow_force_pushes = $false
  allow_deletions = $false
} | ConvertTo-Json -Depth 5

& $gh api \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$Repo/branches/$Branch/protection" \
  -f required_status_checks.strict=true \
  -f enforce_admins=true \
  -f required_pull_request_reviews.required_approving_review_count=$RequiredApprovals \
  -f required_pull_request_reviews.dismiss_stale_reviews=true \
  -f required_linear_history=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -F required_status_checks.contexts[]=$RequiredChecks

Write-Host "Branch protection applied to $Repo:$Branch" -ForegroundColor Green
