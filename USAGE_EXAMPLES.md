# Cloud GPU Training - Usage Examples

This document provides practical examples for using the cloud GPU training infrastructure.

## Table of Contents
1. [Quick Start Examples](#quick-start-examples)
2. [Provider-Specific Examples](#provider-specific-examples)
3. [Advanced Usage](#advanced-usage)
4. [Monitoring and Debugging](#monitoring-and-debugging)
5. [Cost Optimization](#cost-optimization)

## Quick Start Examples

### Example 1: Local Training (Fastest Setup)
```bash
# Install dependencies
pip install -r requirements.txt

# Run training with automatic GPU detection
python cloud_training_launcher.py --provider local

# Monitor GPU usage
python cloud_gpu_utils.py --action monitor --interval 30
```

### Example 2: Interactive Quick Start
```bash
# Linux/Mac
chmod +x quick_start_cloud_training.sh
./quick_start_cloud_training.sh

# Windows PowerShell
.\quick_start_cloud_training.ps1
```

### Example 3: Lambda Labs (Recommended for Cost)
```bash
# Set API key
export LAMBDA_API_KEY="your-api-key-here"

# Launch training
python cloud_training_launcher.py --provider lambda_labs

# Estimated cost: ~$1.65 for 1.5 hours on 1x A100
```

## Provider-Specific Examples

### AWS EC2

#### Manual Setup
```bash
# Configure AWS CLI
aws configure

# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type p3.2xlarge \
  --key-name your-key \
  --region us-east-1

# SSH into instance
ssh -i your-key.pem ubuntu@instance-ip

# On instance
git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
cd Eqratech_Arabic_Diana_Project
pip install -r requirements.txt
python cloud_training_launcher.py --provider aws
```

#### Automated Script
```bash
# Set environment
export INSTANCE_TYPE="p3.2xlarge"
export REGION="us-east-1"
export KEY_NAME="your-key"

# Run automated setup
./cloud_examples/aws_training.sh
```

### Google Cloud Platform

```bash
# Authenticate
gcloud auth login
gcloud config set project your-project-id

# Create instance with GPU
gcloud compute instances create arabic-bert-gpu \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-v100,count=1 \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release

# SSH and setup
gcloud compute ssh arabic-bert-gpu --zone=us-central1-a

# On instance
git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
cd Eqratech_Arabic_Diana_Project
pip install -r requirements.txt
python cloud_training_launcher.py --provider gcp
```

### Azure

```bash
# Login
az login

# Create resource group
az group create --name ArabicBERTRG --location eastus

# Create VM with GPU
az vm create \
  --resource-group ArabicBERTRG \
  --name arabic-bert-vm \
  --image microsoft-dsvm:ubuntu-hpc:1804:latest \
  --size Standard_NC6s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH into VM
ssh azureuser@vm-public-ip

# On VM
git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
cd Eqratech_Arabic_Diana_Project
pip install -r requirements.txt
python cloud_training_launcher.py --provider azure
```

### RunPod (Container-Based)

```bash
# Set API key
export RUNPOD_API_KEY="your-api-key"

# Using web interface (recommended):
# 1. Go to https://www.runpod.io/console/pods
# 2. Click "Deploy"
# 3. Select: PyTorch template, RTX A6000, 50GB storage
# 4. Deploy and connect via SSH

# On RunPod container
cd /workspace
git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
cd Eqratech_Arabic_Diana_Project
pip install -r requirements.txt
python cloud_training_launcher.py --provider runpod
```

## Advanced Usage

### Multi-GPU Training

```bash
# Update config for 4 GPUs
python -c "
import json
config = json.load(open('config/cloud_gpu_config.json'))
config['cloud_training']['num_gpus'] = 4
config['cloud_training']['distributed_training'] = True
json.dump(config, open('config/cloud_gpu_config.json', 'w'), indent=2)
"

# Launch distributed training
python cloud_training_launcher.py --provider local
```

### Custom Training Data

```bash
# Prepare your data
echo "ا ل ح م د ل ل ه" > my_data.txt
echo "م ر ح ب ا ب ك" >> my_data.txt
# ... add more lines

# Train with custom data
python cloud_training_launcher.py \
  --provider local \
  --text my_data.txt
```

### Docker with GPU

```bash
# Build image
docker build -t arabic-bert-training:latest -f docker/Dockerfile.gpu .

# Run training
docker run --rm --gpus all \
  -v $(pwd)/config:/workspace/config \
  -v $(pwd)/output:/workspace/output \
  -v $(pwd)/logs:/workspace/logs \
  -v $(pwd)/data:/workspace/data \
  --shm-size=8g \
  arabic-bert-training:latest \
  python cloud_training_launcher.py --provider local

# View TensorBoard
docker run -d --rm \
  -p 6006:6006 \
  -v $(pwd)/logs:/logs \
  tensorflow/tensorflow:latest \
  tensorboard --logdir=/logs --host=0.0.0.0

# Access at http://localhost:6006
```

### Docker Compose

```bash
# Start training and TensorBoard
docker-compose -f docker/docker-compose.gpu.yml up

# View logs
docker-compose -f docker/docker-compose.gpu.yml logs -f

# Stop
docker-compose -f docker/docker-compose.gpu.yml down
```

### Interactive Docker Helper

```bash
chmod +x docker/docker_helper.sh
./docker/docker_helper.sh

# Select from menu:
# 1. Build image
# 2. Run training
# 3. Start TensorBoard
# etc.
```

## Monitoring and Debugging

### Real-time GPU Monitoring

```bash
# Continuous monitoring (60 second intervals)
python cloud_gpu_utils.py --action monitor --interval 60

# Short monitoring session (5 minutes)
python cloud_gpu_utils.py --action monitor --interval 30 --duration 5

# One-time snapshot
python cloud_gpu_utils.py --action monitor --interval 1 --duration 0.1
```

### Check Configuration

```bash
# Validate all configs
python test_cloud_setup.py

# Check GPU optimization
python cloud_gpu_utils.py --action optimize

# View recommendations
python cloud_gpu_utils.py --action recommend
```

### TensorBoard Visualization

```bash
# Start TensorBoard
tensorboard --logdir ./logs --host 0.0.0.0 --port 6006

# Access in browser: http://localhost:6006
```

### Debug Training Issues

```bash
# Enable debug logging
export PYTHONVERBOSE=1

# Run with monitoring
python cloud_training_launcher.py --provider local --monitor

# Check GPU memory
nvidia-smi

# Monitor in real-time
watch -n 1 nvidia-smi
```

## Cost Optimization

### Use Spot/Preemptible Instances

```python
# Update config for spot instances
import json
config = json.load(open('config/cloud_gpu_config.json'))

# AWS spot
config['providers']['aws']['spot_instance'] = True
config['providers']['aws']['max_price'] = 1.5

# GCP preemptible
config['providers']['gcp']['preemptible'] = True

# Azure spot
config['providers']['azure']['spot_instance'] = True

json.dump(config, open('config/cloud_gpu_config.json', 'w'), indent=2)
```

### Optimize Batch Size

```bash
# Get recommendations for your GPU
python -c "
from cloud_gpu_utils import CloudOptimizer
import torch

if torch.cuda.is_available():
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
    opt = CloudOptimizer.get_optimal_batch_size(gpu_mem)
    print(f'Optimal batch size: {opt[\"batch_size\"]}')
    print(f'Gradient accumulation: {opt[\"gradient_accumulation\"]}')
"
```

### Track Costs

```python
# Track costs during training
from cloud_gpu_utils import CostTracker

tracker = CostTracker(provider="lambda_labs", cost_per_hour=1.10)
tracker.start()

# ... your training code ...

summary = tracker.stop()
print(f"Total cost: ${summary['total_cost']:.2f}")
```

### Estimate Before Running

```bash
# Get cost estimate
python -c "
from cloud_training_launcher import CloudGPUTrainer

launcher = CloudGPUTrainer()
cost = launcher.estimate_training_cost(2.0)  # 2 hours
print(f'Estimated cost: ${cost[\"estimated_total_cost\"]:.2f}')
"
```

## GitHub Actions (CI/CD)

### Trigger Manual Training

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "Cloud GPU Training CI/CD" workflow
4. Click "Run workflow"
5. Select options:
   - Provider: lambda_labs
   - GPU Type: auto
   - Num GPUs: 1
   - Training Epochs: 3
6. Click "Run workflow"

### Configure Secrets

In GitHub Settings → Secrets, add:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `LAMBDA_API_KEY`
- `RUNPOD_API_KEY`
- `GCP_SERVICE_ACCOUNT_KEY`

## Troubleshooting Examples

### Out of Memory Error

```bash
# Reduce batch size
python -c "
import json
config = json.load(open('config/training_config.json'))
config['training']['per_device_train_batch_size'] = 4
config['training']['gradient_accumulation_steps'] = 8
json.dump(config, open('config/training_config.json', 'w'), indent=2)
"

# Run again
python cloud_training_launcher.py --provider local
```

### Slow Training

```bash
# Enable mixed precision
python -c "
import json
config = json.load(open('config/cloud_gpu_config.json'))
config['optimization']['mixed_precision'] = 'fp16'
json.dump(config, open('config/cloud_gpu_config.json', 'w'), indent=2)
"

# Increase workers
python -c "
import json
config = json.load(open('config/cloud_gpu_config.json'))
config['optimization']['dataloader_num_workers'] = 8
json.dump(config, open('config/cloud_gpu_config.json', 'w'), indent=2)
"
```

## Best Practices

1. **Start with small experiments**: Test with 1 epoch on cheap GPU first
2. **Monitor costs**: Use cost tracking to avoid surprises
3. **Use spot instances**: Save 60-90% on cloud costs
4. **Optimize batch size**: Use GPU memory efficiently
5. **Enable checkpointing**: Save progress regularly
6. **Use TensorBoard**: Monitor training progress
7. **Clean up resources**: Terminate instances when done

## Support

If you encounter issues:
1. Run: `python test_cloud_setup.py`
2. Check: `CLOUD_GPU_TRAINING.md`
3. Review logs in `logs/` directory
4. Check provider documentation
