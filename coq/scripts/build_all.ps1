# FractalHub Coq Build Script
# Builds all theory files in correct dependency order

Write-Host "Building FractalHub Coq Theories..." -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

$CoqRoot = Split-Path $PSScriptRoot -Parent
$TheoriesPath = Join-Path $CoqRoot "theories"

# Build order: Core -> Phonology -> Syntax -> Codec -> Facades
$BuildOrder = @(
    @{Layer="Core"; Files=@(
        "Core/FractalHubSpec.v",
        "Core/FractalHubGates.v",
        "Core/FractalHubDerivation.v"
    )},
    @{Layer="Phonology"; Files=@(
        "Phonology/FractalHubPhonology.v"
    )},
    @{Layer="Syntax"; Files=@(
        "Syntax/FractalHubSyntaxDerivation.v"
    )},
    @{Layer="Codec"; Files=@(
        "Codec/FractalHubCodecRoundTrip.v"
    )},
    @{Layer="Facades"; Files=@(
        "FractalHubSpec.v",
        "FractalHubGates.v",
        "FractalHubDerivation.v",
        "FractalHubPhonology.v",
        "FractalHubSyntaxDerivation.v",
        "FractalHubCodecRoundTrip.v"
    )}
)

$TotalFiles = ($BuildOrder | ForEach-Object { $_.Files.Count } | Measure-Object -Sum).Sum
$CurrentFile = 0
$Failed = $false

foreach ($Layer in $BuildOrder) {
    Write-Host "`nBuilding $($Layer.Layer) layer..." -ForegroundColor Yellow
    
    foreach ($File in $Layer.Files) {
        $CurrentFile++
        $FilePath = Join-Path $TheoriesPath $File
        $FileName = Split-Path $File -Leaf
        
        Write-Host "  [$CurrentFile/$TotalFiles] $FileName... " -NoNewline
        
        try {
            $result = & coqc -q -R $TheoriesPath FractalHub $FilePath 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓" -ForegroundColor Green
            } else {
                Write-Host "✗" -ForegroundColor Red
                Write-Host "    Error: $result" -ForegroundColor Red
                $Failed = $true
                break
            }
        } catch {
            Write-Host "✗" -ForegroundColor Red
            Write-Host "    Exception: $_" -ForegroundColor Red
            $Failed = $true
            break
        }
    }
    
    if ($Failed) { break }
}

Write-Host "`n====================================`n" -ForegroundColor Cyan

if ($Failed) {
    Write-Host "Build FAILED!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "`nVerifying output files..." -ForegroundColor Cyan
    
    $VoFiles = Get-ChildItem -Path $TheoriesPath -Filter "*.vo" -Recurse | Select-Object Name, Directory
    Write-Host "Found $($VoFiles.Count) compiled files (.vo):" -ForegroundColor Green
    
    $VoFiles | ForEach-Object {
        $RelPath = $_.Directory.FullName.Replace($TheoriesPath, "theories")
        Write-Host "  • $RelPath\$($_.Name)" -ForegroundColor Gray
    }
    
    exit 0
}
