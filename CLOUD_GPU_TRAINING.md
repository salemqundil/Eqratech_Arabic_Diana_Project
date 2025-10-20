# Cloud GPU Training for Arabic BERT

This guide explains how to train the Arabic BERT model using cloud GPU resources from various providers.

## Supported Cloud Providers

- **AWS** - EC2 instances with NVIDIA GPUs
- **Google Cloud Platform (GCP)** - Compute Engine with GPU accelerators
- **Microsoft Azure** - Virtual Machines with GPU support
- **Lambda Labs** - Dedicated GPU cloud instances
- **RunPod** - Container-based GPU instances

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Cloud GPU Settings

Edit `config/cloud_gpu_config.json` to configure your cloud provider:

```json
{
  "cloud_training": {
    "enabled": true,
    "provider": "lambda_labs",
    "gpu_type": "auto",
    "num_gpus": 1
  }
}
```

### 3. Launch Cloud Training

```bash
# Using the cloud training launcher
python cloud_training_launcher.py --provider lambda_labs

# Or specify custom configuration
python cloud_training_launcher.py \
  --cloud-config config/cloud_gpu_config.json \
  --training-config config/training_config.json
```

## Provider-Specific Setup

### AWS EC2

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

2. **Update cloud config:**
   ```json
   {
     "provider": "aws",
     "providers": {
       "aws": {
         "instance_type": "p3.2xlarge",
         "region": "us-east-1",
         "spot_instance": true
       }
     }
   }
   ```

3. **Launch training:**
   ```bash
   python cloud_training_launcher.py --provider aws
   ```

**Recommended AWS Instances:**
- `p3.2xlarge` - 1x V100 (16GB) - $3.06/hour
- `p3.8xlarge` - 4x V100 (16GB) - $12.24/hour
- `p4d.24xlarge` - 8x A100 (40GB) - $32.77/hour

### Google Cloud Platform (GCP)

1. **Authenticate with GCP:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Update cloud config:**
   ```json
   {
     "provider": "gcp",
     "providers": {
       "gcp": {
         "machine_type": "n1-standard-8",
         "accelerator_type": "nvidia-tesla-v100",
         "accelerator_count": 1,
         "zone": "us-central1-a"
       }
     }
   }
   ```

3. **Launch training:**
   ```bash
   python cloud_training_launcher.py --provider gcp
   ```

**Recommended GCP Configurations:**
- V100 GPU - $2.48/hour
- A100 GPU - $3.67/hour
- TPU v3-8 - $8.00/hour (for larger models)

### Microsoft Azure

1. **Login to Azure:**
   ```bash
   az login
   ```

2. **Update cloud config:**
   ```json
   {
     "provider": "azure",
     "providers": {
       "azure": {
         "vm_size": "Standard_NC6s_v3",
         "location": "eastus",
         "spot_instance": true
       }
     }
   }
   ```

3. **Launch training:**
   ```bash
   python cloud_training_launcher.py --provider azure
   ```

**Recommended Azure VMs:**
- `Standard_NC6s_v3` - 1x V100 (16GB) - $3.06/hour
- `Standard_NC24s_v3` - 4x V100 (16GB) - $12.24/hour
- `Standard_ND96asr_v4` - 8x A100 (40GB) - $27.20/hour

### Lambda Labs

1. **Get API key from Lambda Labs:**
   ```bash
   export LAMBDA_API_KEY="your-api-key"
   ```

2. **Update cloud config:**
   ```json
   {
     "provider": "lambda_labs",
     "providers": {
       "lambda_labs": {
         "instance_type": "gpu_1x_a100",
         "region": "us-west-1"
       }
     }
   }
   ```

3. **Launch training:**
   ```bash
   python cloud_training_launcher.py --provider lambda_labs
   ```

**Lambda Labs GPU Options:**
- 1x RTX 6000 Ada (48GB) - $0.50/hour
- 1x A100 (40GB) - $1.10/hour
- 8x A100 (40GB) - $8.80/hour

### RunPod

1. **Get API key from RunPod:**
   ```bash
   export RUNPOD_API_KEY="your-api-key"
   ```

2. **Update cloud config:**
   ```json
   {
     "provider": "runpod",
     "providers": {
       "runpod": {
         "gpu_type": "NVIDIA RTX A6000",
         "gpu_count": 1
       }
     }
   }
   ```

3. **Launch training:**
   ```bash
   python cloud_training_launcher.py --provider runpod
   ```

**RunPod GPU Options:**
- RTX A6000 (48GB) - $0.79/hour
- A100 (80GB) - $1.89/hour
- H100 (80GB) - $4.69/hour

## GPU Monitoring

Monitor GPU usage during training:

```bash
# Real-time monitoring
python cloud_gpu_utils.py --action monitor --interval 60

# Get optimization recommendations
python cloud_gpu_utils.py --action optimize

# View GPU recommendations
python cloud_gpu_utils.py --action recommend
```

## Optimization Tips

### Batch Size Optimization

The launcher automatically optimizes batch size based on GPU memory:

| GPU Memory | Batch Size | Gradient Accumulation |
|------------|------------|----------------------|
| < 8 GB     | 4          | 8                    |
| 8-16 GB    | 8          | 4                    |
| 16-24 GB   | 16         | 2                    |
| 24-40 GB   | 24         | 1                    |
| > 40 GB    | 32         | 1                    |

### Mixed Precision Training

Automatically enabled for supported GPUs:
- **FP16** - Volta+ GPUs (V100, T4, etc.)
- **BF16** - Ampere+ GPUs (A100, RTX 3090, etc.)

### Distributed Training

For multi-GPU training, update config:

```json
{
  "cloud_training": {
    "num_gpus": 4,
    "distributed_training": true
  },
  "distributed": {
    "backend": "nccl"
  }
}
```

Launch with:
```bash
python cloud_training_launcher.py --provider aws
```

## Cost Estimation

The launcher provides cost estimates before training:

```
[COST] Estimated training cost:
  Provider: lambda_labs
  Duration: 1.50 hours
  Cost per hour: $1.10
  Total estimate: $1.65
```

Track actual costs:
```python
from cloud_gpu_utils import CostTracker

tracker = CostTracker(provider="lambda_labs", cost_per_hour=1.10)
tracker.start()
# ... training ...
tracker.stop()
```

## Docker Deployment

Build and run training in Docker:

```bash
# Build Docker image
docker build -t arabic-bert-training -f docker/Dockerfile.gpu .

# Run training
docker run --gpus all \
  -v $(pwd)/config:/workspace/config \
  -v $(pwd)/output:/workspace/output \
  arabic-bert-training \
  python cloud_training_launcher.py --provider local
```

## Troubleshooting

### Out of Memory Errors

1. Reduce batch size in config
2. Enable gradient checkpointing
3. Reduce max sequence length
4. Increase gradient accumulation steps

### Slow Training

1. Check GPU utilization: `python cloud_gpu_utils.py --action monitor`
2. Increase batch size if GPU has free memory
3. Enable mixed precision training
4. Use data loader workers: set `dataloader_num_workers: 4`

### Connection Issues

1. Check cloud provider API credentials
2. Verify instance availability in selected region
3. Check firewall/security group settings

## Best Practices

1. **Use Spot/Preemptible Instances** - Save up to 70% on costs
2. **Start Small** - Test with 1 GPU before scaling up
3. **Monitor Costs** - Use built-in cost tracking
4. **Save Checkpoints Frequently** - Prevent data loss on preemption
5. **Use Appropriate GPU** - Don't overpay for unused capacity

## Example Training Sessions

### Small Test Run (< $1)
```bash
# Lambda Labs 1x RTX A6000, ~30 minutes
python cloud_training_launcher.py --provider lambda_labs
# Cost: ~$0.40
```

### Production Training (< $5)
```bash
# Lambda Labs 1x A100, ~2 hours
python cloud_training_launcher.py --provider lambda_labs
# Cost: ~$2.20
```

### Large-Scale Training (< $20)
```bash
# AWS 4x V100, ~2 hours
python cloud_training_launcher.py --provider aws
# Cost: ~$12.00
```

## Additional Resources

- [PyTorch Distributed Training](https://pytorch.org/tutorials/beginner/dist_overview.html)
- [Hugging Face Training Guide](https://huggingface.co/docs/transformers/training)
- [GPU Instance Comparison](https://cloud-gpus.com/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GPU monitoring output
3. Check provider-specific documentation
4. Open an issue on GitHub
