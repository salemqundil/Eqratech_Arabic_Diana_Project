param(
  [string]$Python = "py"
)

Write-Host "[1/3] Creating Python 3.11 venv .venv (if missing)" -ForegroundColor Cyan
& $Python -3.11 -m venv .venv

Write-Host "[2/3] Activating venv and installing minimal deps" -ForegroundColor Cyan
. .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install torch transformers

Write-Host "[3/3] Running training smoke" -ForegroundColor Cyan
python run_training_smoke.py

Write-Host "Done." -ForegroundColor Green
