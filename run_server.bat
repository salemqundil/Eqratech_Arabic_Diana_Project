@echo off
set HOST=127.0.0.1
set PORT=8000
echo Starting server on http://%HOST%:%PORT%
python -m uvicorn web_app.main:app --host %HOST% --port %PORT%
echo (Press Ctrl+C to stop)
