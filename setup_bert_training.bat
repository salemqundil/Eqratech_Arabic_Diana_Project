@echo off
REM BERT Training Setup Script for Windows
REM This script automates the setup process for BERT model training

echo ======================================================================
echo   BERT Training Environment Setup for Windows
echo ======================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version

echo.
echo Running automated setup script...
echo.

REM Run the Python setup script with install flag
python setup_bert_training.py --install

if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo   Setup Complete!
echo ======================================================================
echo.
echo You can now train the BERT model by running:
echo   python run_training.py --config config/training_config.json
echo.
pause
