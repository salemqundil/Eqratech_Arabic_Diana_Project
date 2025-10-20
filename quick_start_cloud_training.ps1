# Quick Start: Cloud GPU Training (PowerShell)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Arabic BERT - Cloud GPU Training Quick Start" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "1. Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -q
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Verify setup
Write-Host ""
Write-Host "2. Verifying setup..." -ForegroundColor Yellow
python test_setup.py

# Check GPU availability
Write-Host ""
Write-Host "3. Checking GPU availability..." -ForegroundColor Yellow
python -c @"
import torch
if torch.cuda.is_available():
    print(f'✓ GPU available: {torch.cuda.get_device_name(0)}')
    print(f'  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
else:
    print('⚠ No GPU detected (will use CPU)')
"@

# Show menu
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Select Training Option:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "1. Local training (use available GPU/CPU)"
Write-Host "2. Lambda Labs (requires API key)"
Write-Host "3. RunPod (requires API key)"
Write-Host "4. Docker (local with GPU)"
Write-Host "5. Just show recommendations"
Write-Host ""
$choice = Read-Host "Enter choice (1-5)"

switch ($choice) {
    1 {
        Write-Host ""
        Write-Host "Starting local training..." -ForegroundColor Yellow
        python cloud_training_launcher.py --provider local
    }
    
    2 {
        Write-Host ""
        Write-Host "Lambda Labs Training Setup" -ForegroundColor Yellow
        if (-not $env:LAMBDA_API_KEY) {
            Write-Host "Error: LAMBDA_API_KEY not set" -ForegroundColor Red
            Write-Host "Get your key from: https://cloud.lambdalabs.com/api-keys"
            Write-Host "Then run: `$env:LAMBDA_API_KEY='your-key'"
            exit 1
        }
        Write-Host "Follow the instructions in CLOUD_GPU_TRAINING.md for Lambda Labs setup"
        Write-Host "Or manually run: python cloud_training_launcher.py --provider lambda_labs"
    }
    
    3 {
        Write-Host ""
        Write-Host "RunPod Training Setup" -ForegroundColor Yellow
        if (-not $env:RUNPOD_API_KEY) {
            Write-Host "Error: RUNPOD_API_KEY not set" -ForegroundColor Red
            Write-Host "Get your key from: https://www.runpod.io/console/user/settings"
            Write-Host "Then run: `$env:RUNPOD_API_KEY='your-key'"
            exit 1
        }
        Write-Host "Follow the instructions in CLOUD_GPU_TRAINING.md for RunPod setup"
        Write-Host "Or manually run: python cloud_training_launcher.py --provider runpod"
    }
    
    4 {
        Write-Host ""
        Write-Host "Docker GPU Training" -ForegroundColor Yellow
        Write-Host "Building Docker image..."
        docker build -t arabic-bert-training:latest -f docker/Dockerfile.gpu .
        Write-Host "Running training in Docker..."
        docker run --rm --gpus all `
          -v "${PWD}/config:/workspace/config" `
          -v "${PWD}/output:/workspace/output" `
          -v "${PWD}/logs:/workspace/logs" `
          --shm-size=8g `
          arabic-bert-training:latest `
          python cloud_training_launcher.py --provider local
    }
    
    5 {
        Write-Host ""
        python cloud_gpu_utils.py --action recommend
    }
    
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Check output/ and logs/ directories for results" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
