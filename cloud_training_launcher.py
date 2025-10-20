"""Cloud GPU Training Launcher for Arabic BERT
Supports: AWS, GCP, Azure, Lambda Labs, RunPod
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional
import time


class CloudGPUTrainer:
    """Manages cloud GPU training setup and execution"""
    
    def __init__(self, cloud_config_path: str = "config/cloud_gpu_config.json",
                 training_config_path: str = "config/training_config.json"):
        self.cloud_config = self._load_config(cloud_config_path)
        self.training_config = self._load_config(training_config_path)
        self.provider = self.cloud_config["cloud_training"]["provider"]
        
    def _load_config(self, path: str) -> Dict:
        """Load JSON configuration file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def detect_gpu(self) -> Dict:
        """Detect available GPU resources"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info = {
                    "available": True,
                    "count": torch.cuda.device_count(),
                    "devices": []
                }
                for i in range(torch.cuda.device_count()):
                    gpu_info["devices"].append({
                        "id": i,
                        "name": torch.cuda.get_device_name(i),
                        "memory_total": torch.cuda.get_device_properties(i).total_memory / 1e9,
                        "compute_capability": torch.cuda.get_device_capability(i)
                    })
                return gpu_info
            else:
                return {"available": False, "count": 0, "devices": []}
        except ImportError:
            return {"available": False, "count": 0, "devices": [], "error": "PyTorch not installed"}
    
    def setup_distributed_training(self):
        """Configure distributed training environment"""
        if not self.cloud_config["cloud_training"]["distributed_training"]:
            return
        
        # Set environment variables for distributed training
        if "RANK" not in os.environ:
            os.environ["RANK"] = "0"
        if "LOCAL_RANK" not in os.environ:
            os.environ["LOCAL_RANK"] = "0"
        if "WORLD_SIZE" not in os.environ:
            num_gpus = self.cloud_config["cloud_training"]["num_gpus"]
            os.environ["WORLD_SIZE"] = str(num_gpus)
        
        backend = self.cloud_config["distributed"]["backend"]
        print(f"[DISTRIBUTED] Backend: {backend}")
        print(f"[DISTRIBUTED] World size: {os.environ['WORLD_SIZE']}")
        print(f"[DISTRIBUTED] Rank: {os.environ['RANK']}")
    
    def optimize_training_config(self) -> Dict:
        """Apply cloud GPU optimizations to training config"""
        optimized = self.training_config.copy()
        opt_config = self.cloud_config["optimization"]
        
        # Adjust batch size based on GPU memory
        gpu_info = self.detect_gpu()
        if gpu_info["available"] and gpu_info["devices"]:
            gpu_memory_gb = gpu_info["devices"][0]["memory_total"]
            if gpu_memory_gb >= 40:  # A100 or similar
                optimized["training"]["per_device_train_batch_size"] = 32
                optimized["training"]["gradient_accumulation_steps"] = 1
            elif gpu_memory_gb >= 24:  # RTX 3090, A5000, etc.
                optimized["training"]["per_device_train_batch_size"] = 16
                optimized["training"]["gradient_accumulation_steps"] = 2
            elif gpu_memory_gb >= 16:  # V100, RTX 4090
                optimized["training"]["per_device_train_batch_size"] = 12
                optimized["training"]["gradient_accumulation_steps"] = 2
            else:  # Smaller GPUs
                optimized["training"]["per_device_train_batch_size"] = 8
                optimized["training"]["gradient_accumulation_steps"] = 4
        
        # Enable mixed precision for supported GPUs
        if opt_config["mixed_precision"] == "auto":
            if gpu_info["available"] and gpu_info["devices"]:
                compute_cap = gpu_info["devices"][0]["compute_capability"]
                # Enable FP16 for compute capability >= 7.0 (Volta+)
                if compute_cap[0] >= 7:
                    optimized["training"]["fp16"] = True
                    optimized["training"]["bf16"] = False
                # Enable BF16 for Ampere+ (compute capability >= 8.0)
                if compute_cap[0] >= 8:
                    optimized["training"]["bf16"] = True
                    optimized["training"]["fp16"] = False
        
        return optimized
    
    def estimate_training_cost(self, duration_hours: float) -> Dict:
        """Estimate training cost for cloud provider"""
        costs = self.cloud_config["cost_estimation"]["cost_per_hour"]
        provider = self.provider
        
        cost_key_map = {
            "aws": "aws_p3_2xlarge",
            "gcp": "gcp_v100",
            "azure": "azure_nc6s_v3",
            "lambda_labs": "lambda_a100",
            "runpod": "runpod_a6000"
        }
        
        cost_key = cost_key_map.get(provider, "aws_p3_2xlarge")
        cost_per_hour = costs.get(cost_key, 3.0)
        
        total_cost = duration_hours * cost_per_hour
        
        return {
            "provider": provider,
            "duration_hours": duration_hours,
            "cost_per_hour": cost_per_hour,
            "estimated_total_cost": total_cost,
            "currency": "USD"
        }
    
    def launch_training(self, args: argparse.Namespace):
        """Launch training with cloud GPU configuration"""
        print("=" * 70)
        print("Cloud GPU Training Launcher - Arabic BERT")
        print("=" * 70)
        
        # Detect GPU
        gpu_info = self.detect_gpu()
        print(f"\n[GPU] Detection:")
        print(f"  Available: {gpu_info['available']}")
        print(f"  Count: {gpu_info['count']}")
        if gpu_info["available"]:
            for device in gpu_info["devices"]:
                print(f"  - {device['name']} ({device['memory_total']:.1f} GB)")
        
        # Setup distributed training if needed
        if self.cloud_config["cloud_training"]["distributed_training"]:
            self.setup_distributed_training()
        
        # Optimize configuration
        optimized_config = self.optimize_training_config()
        
        # Save optimized config temporarily
        temp_config_path = "/tmp/optimized_training_config.json"
        with open(temp_config_path, "w", encoding="utf-8") as f:
            json.dump(optimized_config, f, indent=2, ensure_ascii=False)
        
        print(f"\n[CONFIG] Optimized training configuration:")
        print(f"  Batch size: {optimized_config['training']['per_device_train_batch_size']}")
        print(f"  Gradient accumulation: {optimized_config['training']['gradient_accumulation_steps']}")
        print(f"  Mixed precision: {optimized_config['training'].get('fp16', False) or optimized_config['training'].get('bf16', False)}")
        
        # Estimate cost
        estimated_hours = optimized_config["training"]["num_train_epochs"] * 0.5  # rough estimate
        if self.cloud_config["curriculum_training"]["enabled"]:
            estimated_hours *= len(self.cloud_config["curriculum_training"]["stages"])
        
        cost_estimate = self.estimate_training_cost(estimated_hours)
        print(f"\n[COST] Estimated training cost:")
        print(f"  Provider: {cost_estimate['provider']}")
        print(f"  Duration: {cost_estimate['duration_hours']:.2f} hours")
        print(f"  Cost per hour: ${cost_estimate['cost_per_hour']:.2f}")
        print(f"  Total estimate: ${cost_estimate['estimated_total_cost']:.2f}")
        
        # Launch training
        print("\n[TRAINING] Starting training process...")
        training_cmd = [
            sys.executable,
            "run_training.py",
            "--config", temp_config_path
        ]
        
        if args.skip_deps_check:
            training_cmd.append("--skip-deps-check")
        
        if args.text:
            training_cmd.extend(["--text", args.text])
        
        print(f"[TRAINING] Command: {' '.join(training_cmd)}")
        
        # Track start time for cost calculation
        start_time = time.time()
        
        try:
            result = subprocess.run(training_cmd, check=True)
            elapsed_hours = (time.time() - start_time) / 3600
            actual_cost = self.estimate_training_cost(elapsed_hours)
            
            print("\n" + "=" * 70)
            print("Training Completed Successfully!")
            print("=" * 70)
            print(f"Elapsed time: {elapsed_hours:.2f} hours")
            print(f"Actual cost: ${actual_cost['estimated_total_cost']:.2f}")
            
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Training failed with exit code {e.returncode}")
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            elapsed_hours = (time.time() - start_time) / 3600
            print(f"\n[INTERRUPT] Training interrupted after {elapsed_hours:.2f} hours")
            sys.exit(1)
    
    def monitor_gpu_usage(self):
        """Monitor GPU usage during training"""
        try:
            import torch
            if not torch.cuda.is_available():
                print("[MONITOR] No GPU available for monitoring")
                return
            
            print("\n[MONITOR] GPU Statistics:")
            for i in range(torch.cuda.device_count()):
                print(f"\n  GPU {i}: {torch.cuda.get_device_name(i)}")
                print(f"    Memory Allocated: {torch.cuda.memory_allocated(i) / 1e9:.2f} GB")
                print(f"    Memory Reserved: {torch.cuda.memory_reserved(i) / 1e9:.2f} GB")
                print(f"    Memory Total: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")
        except Exception as e:
            print(f"[MONITOR] Error monitoring GPU: {e}")


def main():
    parser = argparse.ArgumentParser(description="Cloud GPU Training Launcher for Arabic BERT")
    parser.add_argument(
        "--cloud-config",
        type=str,
        default="config/cloud_gpu_config.json",
        help="Path to cloud GPU configuration file"
    )
    parser.add_argument(
        "--training-config",
        type=str,
        default="config/training_config.json",
        help="Path to training configuration file"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["local", "aws", "gcp", "azure", "lambda_labs", "runpod"],
        help="Override cloud provider from config"
    )
    parser.add_argument(
        "--skip-deps-check",
        action="store_true",
        help="Skip dependency check in training script"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Path to text file for training data"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Show GPU monitoring information"
    )
    
    args = parser.parse_args()
    
    try:
        launcher = CloudGPUTrainer(args.cloud_config, args.training_config)
        
        # Override provider if specified
        if args.provider:
            launcher.cloud_config["cloud_training"]["provider"] = args.provider
            launcher.provider = args.provider
        
        if args.monitor:
            launcher.monitor_gpu_usage()
        else:
            launcher.launch_training(args)
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
