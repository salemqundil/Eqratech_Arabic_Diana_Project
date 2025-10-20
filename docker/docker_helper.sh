#!/bin/bash
# Docker GPU Training Helper Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "====================================="
echo "Docker GPU Training Helper"
echo "====================================="

# Check for NVIDIA Docker runtime
if ! docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
  echo "Error: NVIDIA Docker runtime not available"
  echo ""
  echo "Install NVIDIA Container Toolkit:"
  echo "  https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
  exit 1
fi

# Display menu
echo ""
echo "Select operation:"
echo "1. Build Docker image"
echo "2. Run training (single GPU)"
echo "3. Run training (multi-GPU)"
echo "4. Start TensorBoard"
echo "5. Monitor GPU usage"
echo "6. Shell into container"
echo "7. Clean up containers and images"
echo ""
read -p "Enter choice (1-7): " CHOICE

case $CHOICE in
  1)
    echo "Building Docker image..."
    cd "$PROJECT_ROOT"
    docker build -t arabic-bert-training:latest -f docker/Dockerfile.gpu .
    echo "Build complete!"
    ;;
    
  2)
    echo "Running training on single GPU..."
    docker run --rm --gpus all \
      -v "$PROJECT_ROOT/config:/workspace/config" \
      -v "$PROJECT_ROOT/output:/workspace/output" \
      -v "$PROJECT_ROOT/logs:/workspace/logs" \
      -v "$PROJECT_ROOT/data:/workspace/data" \
      --shm-size=8g \
      arabic-bert-training:latest \
      python cloud_training_launcher.py --provider local
    ;;
    
  3)
    echo "Enter number of GPUs to use:"
    read NUM_GPUS
    echo "Running training on $NUM_GPUS GPUs..."
    docker run --rm --gpus "device=0,1,2,3" \
      -e CUDA_VISIBLE_DEVICES="0,1,2,3" \
      -v "$PROJECT_ROOT/config:/workspace/config" \
      -v "$PROJECT_ROOT/output:/workspace/output" \
      -v "$PROJECT_ROOT/logs:/workspace/logs" \
      -v "$PROJECT_ROOT/data:/workspace/data" \
      --shm-size=8g \
      arabic-bert-training:latest \
      python cloud_training_launcher.py --provider local
    ;;
    
  4)
    echo "Starting TensorBoard..."
    docker run -d --rm \
      -p 6006:6006 \
      -v "$PROJECT_ROOT/logs:/logs" \
      --name arabic-bert-tensorboard \
      tensorflow/tensorflow:latest \
      tensorboard --logdir=/logs --host=0.0.0.0
    echo "TensorBoard started at http://localhost:6006"
    ;;
    
  5)
    echo "Monitoring GPU usage (press Ctrl+C to stop)..."
    docker run --rm --gpus all \
      arabic-bert-training:latest \
      python cloud_gpu_utils.py --action monitor --interval 5
    ;;
    
  6)
    echo "Opening shell in container..."
    docker run -it --rm --gpus all \
      -v "$PROJECT_ROOT:/workspace" \
      arabic-bert-training:latest \
      /bin/bash
    ;;
    
  7)
    echo "Cleaning up Docker containers and images..."
    docker stop arabic-bert-tensorboard 2>/dev/null || true
    docker rm arabic-bert-gpu-training 2>/dev/null || true
    echo "Remove Docker images? (y/n)"
    read CONFIRM
    if [ "$CONFIRM" == "y" ]; then
      docker rmi arabic-bert-training:latest 2>/dev/null || true
      echo "Cleanup complete!"
    fi
    ;;
    
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "Done!"
