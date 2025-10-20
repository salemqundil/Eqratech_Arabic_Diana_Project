"""GPU Monitoring and Optimization Utilities for Cloud Training"""

import time
import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class GPUMonitor:
    """Monitor GPU usage and performance metrics"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "logs/gpu_monitoring.json"
        self.metrics_history = []
        
    def get_gpu_metrics(self) -> Dict:
        """Get current GPU metrics"""
        try:
            import torch
            if not torch.cuda.is_available():
                return {"error": "No GPU available"}
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "gpus": []
            }
            
            for i in range(torch.cuda.device_count()):
                gpu_metrics = {
                    "gpu_id": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_allocated_gb": torch.cuda.memory_allocated(i) / 1e9,
                    "memory_reserved_gb": torch.cuda.memory_reserved(i) / 1e9,
                    "memory_total_gb": torch.cuda.get_device_properties(i).total_memory / 1e9,
                    "utilization_percent": (torch.cuda.memory_allocated(i) / 
                                          torch.cuda.get_device_properties(i).total_memory * 100)
                }
                metrics["gpus"].append(gpu_metrics)
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def log_metrics(self):
        """Log current GPU metrics to file"""
        metrics = self.get_gpu_metrics()
        self.metrics_history.append(metrics)
        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.metrics_history, f, indent=2, ensure_ascii=False)
    
    def print_metrics(self):
        """Print current GPU metrics to console"""
        metrics = self.get_gpu_metrics()
        
        if "error" in metrics:
            print(f"[GPU MONITOR] {metrics['error']}")
            return
        
        print("\n" + "=" * 70)
        print("GPU Monitoring Report")
        print("=" * 70)
        print(f"Timestamp: {metrics['timestamp']}")
        
        for gpu in metrics["gpus"]:
            print(f"\nGPU {gpu['gpu_id']}: {gpu['name']}")
            print(f"  Memory Allocated: {gpu['memory_allocated_gb']:.2f} GB")
            print(f"  Memory Reserved:  {gpu['memory_reserved_gb']:.2f} GB")
            print(f"  Memory Total:     {gpu['memory_total_gb']:.2f} GB")
            print(f"  Utilization:      {gpu['utilization_percent']:.1f}%")
        print("=" * 70)
    
    def continuous_monitoring(self, interval_seconds: int = 60, duration_minutes: Optional[int] = None):
        """Continuously monitor GPU and log metrics"""
        print(f"[GPU MONITOR] Starting continuous monitoring (interval: {interval_seconds}s)")
        
        start_time = time.time()
        try:
            while True:
                self.log_metrics()
                self.print_metrics()
                
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        print(f"\n[GPU MONITOR] Monitoring completed ({duration_minutes} minutes)")
                        break
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n[GPU MONITOR] Monitoring interrupted by user")


class CloudOptimizer:
    """Optimize training configuration for cloud GPUs"""
    
    @staticmethod
    def get_optimal_batch_size(gpu_memory_gb: float, model_size: str = "base") -> Dict:
        """Recommend optimal batch size based on GPU memory"""
        
        # Base recommendations for BERT-base model
        recommendations = {
            "small": {  # < 8 GB (e.g., GTX 1070, RTX 2060)
                "batch_size": 4,
                "gradient_accumulation": 8,
                "max_seq_length": 256
            },
            "medium": {  # 8-16 GB (e.g., RTX 2080Ti, RTX 3070)
                "batch_size": 8,
                "gradient_accumulation": 4,
                "max_seq_length": 512
            },
            "large": {  # 16-24 GB (e.g., V100, RTX 3090, RTX 4090)
                "batch_size": 16,
                "gradient_accumulation": 2,
                "max_seq_length": 512
            },
            "xlarge": {  # 24-40 GB (e.g., A5000, RTX 6000 Ada)
                "batch_size": 24,
                "gradient_accumulation": 1,
                "max_seq_length": 512
            },
            "xxlarge": {  # > 40 GB (e.g., A100, H100)
                "batch_size": 32,
                "gradient_accumulation": 1,
                "max_seq_length": 512
            }
        }
        
        if gpu_memory_gb < 8:
            category = "small"
        elif gpu_memory_gb < 16:
            category = "medium"
        elif gpu_memory_gb < 24:
            category = "large"
        elif gpu_memory_gb < 40:
            category = "xlarge"
        else:
            category = "xxlarge"
        
        return {
            "gpu_memory_gb": gpu_memory_gb,
            "category": category,
            **recommendations[category]
        }
    
    @staticmethod
    def estimate_training_time(
        num_samples: int,
        batch_size: int,
        num_epochs: int,
        gradient_accumulation_steps: int = 1,
        time_per_step_seconds: float = 0.5
    ) -> Dict:
        """Estimate training time"""
        
        effective_batch_size = batch_size * gradient_accumulation_steps
        steps_per_epoch = num_samples / effective_batch_size
        total_steps = steps_per_epoch * num_epochs
        
        total_time_seconds = total_steps * time_per_step_seconds
        total_time_hours = total_time_seconds / 3600
        
        return {
            "num_samples": num_samples,
            "batch_size": batch_size,
            "gradient_accumulation_steps": gradient_accumulation_steps,
            "effective_batch_size": effective_batch_size,
            "steps_per_epoch": int(steps_per_epoch),
            "total_steps": int(total_steps),
            "estimated_time_seconds": total_time_seconds,
            "estimated_time_hours": total_time_hours,
            "estimated_time_formatted": f"{int(total_time_hours)}h {int((total_time_hours % 1) * 60)}m"
        }


class CostTracker:
    """Track and estimate cloud training costs"""
    
    def __init__(self, provider: str = "local", cost_per_hour: float = 0.0):
        self.provider = provider
        self.cost_per_hour = cost_per_hour
        self.start_time = None
        self.end_time = None
        
    def start(self):
        """Start cost tracking"""
        self.start_time = time.time()
        print(f"[COST TRACKER] Started tracking for {self.provider} at ${self.cost_per_hour}/hour")
    
    def stop(self) -> Dict:
        """Stop cost tracking and return summary"""
        self.end_time = time.time()
        
        if not self.start_time:
            return {"error": "Tracking not started"}
        
        duration_hours = (self.end_time - self.start_time) / 3600
        total_cost = duration_hours * self.cost_per_hour
        
        summary = {
            "provider": self.provider,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
            "duration_hours": duration_hours,
            "cost_per_hour": self.cost_per_hour,
            "total_cost": total_cost,
            "currency": "USD"
        }
        
        print("\n" + "=" * 70)
        print("Cost Tracking Summary")
        print("=" * 70)
        print(f"Provider: {summary['provider']}")
        print(f"Duration: {summary['duration_hours']:.2f} hours")
        print(f"Cost per hour: ${summary['cost_per_hour']:.2f}")
        print(f"Total cost: ${summary['total_cost']:.2f}")
        print("=" * 70)
        
        return summary
    
    def get_current_cost(self) -> float:
        """Get current accumulated cost"""
        if not self.start_time:
            return 0.0
        
        current_time = time.time()
        duration_hours = (current_time - self.start_time) / 3600
        return duration_hours * self.cost_per_hour


def print_gpu_recommendations():
    """Print GPU recommendations for different use cases"""
    print("\n" + "=" * 70)
    print("GPU Recommendations for Arabic BERT Training")
    print("=" * 70)
    
    recommendations = [
        {
            "use_case": "Development & Testing",
            "gpu": "RTX 3060 (12GB) or RTX 3070 (8GB)",
            "cost": "$0.40-0.60/hour (cloud)",
            "batch_size": "8-12",
            "training_time": "~2-3 hours"
        },
        {
            "use_case": "Small-Scale Training",
            "gpu": "RTX 3090 (24GB) or V100 (16GB)",
            "cost": "$1.00-2.50/hour (cloud)",
            "batch_size": "16-24",
            "training_time": "~1-2 hours"
        },
        {
            "use_case": "Production Training",
            "gpu": "A100 (40GB) or A100 (80GB)",
            "cost": "$1.00-4.00/hour (cloud)",
            "batch_size": "32-48",
            "training_time": "~30-60 minutes"
        },
        {
            "use_case": "Multi-GPU Training",
            "gpu": "4x A100 (40GB)",
            "cost": "$4.00-16.00/hour (cloud)",
            "batch_size": "64-128",
            "training_time": "~15-30 minutes"
        }
    ]
    
    for rec in recommendations:
        print(f"\n{rec['use_case']}:")
        print(f"  Recommended GPU: {rec['gpu']}")
        print(f"  Cost: {rec['cost']}")
        print(f"  Batch Size: {rec['batch_size']}")
        print(f"  Est. Training Time: {rec['training_time']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GPU Monitoring and Optimization Utilities")
    parser.add_argument(
        "--action",
        choices=["monitor", "optimize", "recommend"],
        default="monitor",
        help="Action to perform"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Monitoring duration in minutes"
    )
    
    args = parser.parse_args()
    
    if args.action == "monitor":
        monitor = GPUMonitor()
        monitor.continuous_monitoring(args.interval, args.duration)
    elif args.action == "optimize":
        monitor = GPUMonitor()
        metrics = monitor.get_gpu_metrics()
        if not metrics.get("error") and metrics.get("gpus"):
            gpu_memory = metrics["gpus"][0]["memory_total_gb"]
            optimizer = CloudOptimizer()
            optimal = optimizer.get_optimal_batch_size(gpu_memory)
            print("\nOptimal Training Configuration:")
            print(json.dumps(optimal, indent=2))
    elif args.action == "recommend":
        print_gpu_recommendations()
