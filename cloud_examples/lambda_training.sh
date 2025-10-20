#!/bin/bash
# Lambda Labs GPU Training Script

set -e

echo "====================================="
echo "Lambda Labs GPU Training"
echo "====================================="

# Check for API key
if [ -z "$LAMBDA_API_KEY" ]; then
  echo "Error: LAMBDA_API_KEY not set"
  echo "Get your API key from: https://cloud.lambdalabs.com/api-keys"
  echo "Then run: export LAMBDA_API_KEY='your-key'"
  exit 1
fi

# Configuration
INSTANCE_TYPE=${INSTANCE_TYPE:-"gpu_1x_a100"}
SSH_KEY_NAME=${SSH_KEY_NAME:-"arabic-bert-key"}

echo "Configuration:"
echo "  Instance Type: $INSTANCE_TYPE"
echo "  SSH Key: $SSH_KEY_NAME"

# Launch instance using Lambda CLI or API
echo ""
echo "Launching Lambda Labs instance..."
echo "Manual steps (Lambda Labs web interface):"
echo "1. Go to https://cloud.lambdalabs.com/instances"
echo "2. Click 'Launch Instance'"
echo "3. Select: $INSTANCE_TYPE"
echo "4. Select SSH key: $SSH_KEY_NAME"
echo "5. Launch and note the instance IP"

echo ""
echo "Enter the instance IP address:"
read INSTANCE_IP

# Wait for SSH
echo ""
echo "Waiting for SSH to be ready..."
sleep 10

# Copy project files
echo ""
echo "Copying project files..."
scp -r -o StrictHostKeyChecking=no \
  ../../* ubuntu@$INSTANCE_IP:/home/ubuntu/arabic-bert/

# Run training
echo ""
echo "Starting training on Lambda Labs..."
ssh -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << 'EOF'
  cd /home/ubuntu/arabic-bert
  
  # Install dependencies
  pip install -r requirements.txt
  
  # Verify GPU
  python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
  
  # Run training with monitoring
  python cloud_training_launcher.py --provider lambda_labs
  
  # Create results archive
  tar -czf results.tar.gz output/ logs/
EOF

# Download results
echo ""
echo "Downloading results..."
scp ubuntu@$INSTANCE_IP:/home/ubuntu/arabic-bert/results.tar.gz ./

echo ""
echo "Training complete! Results saved to results.tar.gz"
echo "Remember to terminate your Lambda Labs instance from the web interface!"
