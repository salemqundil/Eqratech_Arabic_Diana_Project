Param(
    [string]$Host = '127.0.0.1',
    [int]$Port = 8000,
    [switch]$Reload
)
Write-Host "Starting server on http://$Host:$Port" -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error 'Python not found in PATH.'
    exit 1
}
python -c "import uvicorn,sys; uvicorn.run('web_app.main:app', host='$Host', port=$Port, reload=${Reload.IsPresent.ToString().ToLower()})"
