#!/bin/bash
# BERT Training Setup Script for Linux/macOS
# This script automates the setup process for BERT model training

echo "======================================================================"
echo "  BERT Training Environment Setup for Linux/macOS"
echo "======================================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed or not in PATH"
    echo "Please install Python 3.8+ from your package manager or https://www.python.org/"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "[OK] Python is installed"
$PYTHON_CMD --version

echo ""
echo "Running automated setup script..."
echo ""

# Run the Python setup script with install flag
$PYTHON_CMD setup_bert_training.py --install

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Setup failed. Please check the errors above."
    exit 1
fi

echo ""
echo "======================================================================"
echo "  Setup Complete!"
echo "======================================================================"
echo ""
echo "You can now train the BERT model by running:"
echo "  $PYTHON_CMD run_training.py --config config/training_config.json"
echo ""
