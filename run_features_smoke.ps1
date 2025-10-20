param(
  [string]$Python = "py",
  [string]$OntoPath = "config/phoneme_ontology.yaml",
  [string]$Text = "مُحَمَّدٌ رَسُولُ اللَّهِ"
)

Write-Host "[1/4] Creating Python 3.11 venv .venv (if missing)" -ForegroundColor Cyan
& $Python -3.11 -m venv .venv

Write-Host "[2/4] Activating venv and upgrading pip" -ForegroundColor Cyan
. .\.venv\Scripts\Activate.ps1
python -m pip install -U pip

Write-Host "[3/4] Installing minimal requirements for features pipeline" -ForegroundColor Cyan
pip install -r requirements-features.txt

Write-Host "[4/4] Running features pipeline smoke test" -ForegroundColor Cyan
$code = @"
from features_pipeline import run_pipeline
from pathlib import Path

Path('text.txt').write_text(r'''$Text''', encoding='utf-8')
df, mi, a = run_pipeline('text.txt', onto_path=r'''$OntoPath''', out_prefix='out')
print('OK rows', len(df), 'alpha_nan', str(a!=a))
"@

$tmp = Join-Path $PSScriptRoot "run_features_smoke_tmp.py"
$code | Out-File -Encoding utf8 $tmp
python $tmp
Remove-Item $tmp -ErrorAction SilentlyContinue

Write-Host "Done. Generated: out_features.csv, out_mi_fisher.csv, out_summary.json" -ForegroundColor Green
