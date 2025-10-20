#!/bin/bash
# Quick Start: Cloud GPU Training

set -e

echo "============================================"
echo "Arabic BERT - Cloud GPU Training Quick Start"
echo "============================================"

# Check Python
if ! command -v python &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.8+"
    exit 1
fi

echo "Python version: $(python --version)"

# Install dependencies
echo ""
echo "1. Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Verify setup
echo ""
echo "2. Verifying setup..."
python test_setup.py || true

# Check GPU availability
echo ""
echo "3. Checking GPU availability..."
python -c "
import torch
if torch.cuda.is_available():
    print(f'✓ GPU available: {torch.cuda.get_device_name(0)}')
    print(f'  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
else:
    print('⚠ No GPU detected (will use CPU)')
"

# Show menu
echo ""
echo "============================================"
echo "Select Training Option:"
echo "============================================"
echo "1. Local training (use available GPU/CPU)"
echo "2. AWS EC2 (requires AWS credentials)"
echo "3. Lambda Labs (requires API key)"
echo "4. RunPod (requires API key)"
echo "5. Docker (local with GPU)"
echo "6. Just show recommendations"
echo ""
read -p "Enter choice (1-6): " CHOICE

case $CHOICE in
  1)
    echo ""
    echo "Starting local training..."
    python cloud_training_launcher.py --provider local
    ;;
    
  2)
    echo ""
    echo "AWS EC2 Training Setup"
    if [ -z "$AWS_ACCESS_KEY_ID" ]; then
      echo "Error: AWS credentials not configured"
      echo "Run: aws configure"
      exit 1
    fi
    ./cloud_examples/aws_training.sh
    ;;
    
  3)
    echo ""
    echo "Lambda Labs Training Setup"
    if [ -z "$LAMBDA_API_KEY" ]; then
      echo "Error: LAMBDA_API_KEY not set"
      echo "Get your key from: https://cloud.lambdalabs.com/api-keys"
      exit 1
    fi
    ./cloud_examples/lambda_training.sh
    ;;
    
  4)
    echo ""
    echo "RunPod Training Setup"
    if [ -z "$RUNPOD_API_KEY" ]; then
      echo "Error: RUNPOD_API_KEY not set"
      echo "Get your key from: https://www.runpod.io/console/user/settings"
      exit 1
    fi
    ./cloud_examples/runpod_training.sh
    ;;
    
  5)
    echo ""
    echo "Docker GPU Training"
    chmod +x docker/docker_helper.sh
    ./docker/docker_helper.sh
    ;;
    
  6)
    echo ""
    python cloud_gpu_utils.py --action recommend
    ;;
    
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "============================================"
echo "Training completed! Check output/ and logs/ directories"
echo "============================================"
