#!/bin/bash
# RunPod GPU Training Script

set -e

echo "====================================="
echo "RunPod GPU Training"
echo "====================================="

# Check for API key
if [ -z "$RUNPOD_API_KEY" ]; then
  echo "Error: RUNPOD_API_KEY not set"
  echo "Get your API key from: https://www.runpod.io/console/user/settings"
  echo "Then run: export RUNPOD_API_KEY='your-key'"
  exit 1
fi

# Configuration
GPU_TYPE=${GPU_TYPE:-"NVIDIA RTX A6000"}
GPU_COUNT=${GPU_COUNT:-1}

echo "Configuration:"
echo "  GPU Type: $GPU_TYPE"
echo "  GPU Count: $GPU_COUNT"

echo ""
echo "RunPod Training Options:"
echo "1. Use RunPod Web Interface (Recommended)"
echo "2. Use RunPod CLI"
echo ""
echo "Select option (1 or 2):"
read OPTION

if [ "$OPTION" == "1" ]; then
  echo ""
  echo "Manual steps:"
  echo "1. Go to https://www.runpod.io/console/pods"
  echo "2. Click 'Deploy'"
  echo "3. Select GPU: $GPU_TYPE (x$GPU_COUNT)"
  echo "4. Select Template: 'PyTorch' or 'RunPod Pytorch'"
  echo "5. Add Volume (optional): 50GB for data"
  echo "6. Deploy and note the Pod ID and SSH command"
  echo ""
  echo "Once deployed, enter SSH connection details:"
  echo "SSH command (e.g., ssh root@ssh.runpod.io -p 12345 -i ~/.ssh/id_ed25519):"
  read SSH_CMD
  
  # Parse SSH command to get host and port
  echo ""
  echo "Uploading project files via SSH..."
  
  # Note: User will need to manually copy files or use the provided SSH command
  echo "Upload files with: $SSH_CMD"
  echo "Then run in the pod:"
  echo "  cd /workspace"
  echo "  git clone YOUR_REPO_URL"
  echo "  cd Eqratech_Arabic_Diana_Project"
  echo "  pip install -r requirements.txt"
  echo "  python cloud_training_launcher.py --provider runpod"
  
elif [ "$OPTION" == "2" ]; then
  echo ""
  echo "Using RunPod CLI (requires runpodctl installed)..."
  
  # Check if runpodctl is installed
  if ! command -v runpodctl &> /dev/null; then
    echo "Installing runpodctl..."
    wget https://github.com/runpod/runpodctl/releases/latest/download/runpodctl-linux-amd64 -O runpodctl
    chmod +x runpodctl
    sudo mv runpodctl /usr/local/bin/
  fi
  
  # Create pod
  echo "Creating RunPod pod..."
  POD_ID=$(runpodctl create pod \
    --name "arabic-bert-training" \
    --gpuType "$GPU_TYPE" \
    --gpuCount $GPU_COUNT \
    --containerImage "runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel" \
    --volumeSize 50 \
    --ports "8888/http" \
    | grep -oP 'Pod ID: \K\w+')
  
  echo "Pod created: $POD_ID"
  
  # Wait for pod to be ready
  echo "Waiting for pod to be ready..."
  sleep 30
  
  # Get connection details
  runpodctl get pod $POD_ID
  
  echo ""
  echo "Connect to pod and run training:"
  echo "  runpodctl connect $POD_ID"
  echo "  cd /workspace"
  echo "  # Upload your code or git clone"
  echo "  python cloud_training_launcher.py --provider runpod"
fi

echo ""
echo "Done! Remember to stop your pod when finished to save costs."
echo "Stop pod: runpodctl stop pod POD_ID"
echo "Or use RunPod web interface: https://www.runpod.io/console/pods"
