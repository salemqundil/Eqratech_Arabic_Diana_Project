"""
Integration test for cloud GPU training setup
Tests configuration loading, launcher, and GPU utilities
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def test_config_files():
    """Test that all configuration files are valid"""
    print("Testing configuration files...")
    
    configs = [
        "config/training_config.json",
        "config/cloud_gpu_config.json"
    ]
    
    for config_path in configs:
        if not os.path.exists(config_path):
            print(f"  ✗ FAIL: {config_path} not found")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"  ✓ {config_path} is valid")
        except json.JSONDecodeError as e:
            print(f"  ✗ FAIL: {config_path} has invalid JSON: {e}")
            return False
    
    return True


def test_cloud_launcher():
    """Test cloud training launcher"""
    print("\nTesting cloud training launcher...")
    
    # Test help command
    try:
        result = subprocess.run(
            [sys.executable, "cloud_training_launcher.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("  ✓ Cloud launcher help command works")
        else:
            print(f"  ✗ FAIL: Cloud launcher help failed with code {result.returncode}")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: Cloud launcher error: {e}")
        return False
    
    # Test monitor command
    try:
        result = subprocess.run(
            [sys.executable, "cloud_training_launcher.py", "--monitor"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("  ✓ Cloud launcher monitor works")
        else:
            print(f"  ✗ FAIL: Cloud launcher monitor failed")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: Cloud launcher monitor error: {e}")
        return False
    
    return True


def test_gpu_utils():
    """Test GPU utilities"""
    print("\nTesting GPU utilities...")
    
    # Test recommendations
    try:
        result = subprocess.run(
            [sys.executable, "cloud_gpu_utils.py", "--action", "recommend"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and "GPU Recommendations" in result.stdout:
            print("  ✓ GPU recommendations work")
        else:
            print(f"  ✗ FAIL: GPU recommendations failed")
            return False
    except Exception as e:
        print(f"  ✗ FAIL: GPU utils error: {e}")
        return False
    
    return True


def test_cloud_launcher_api():
    """Test cloud launcher Python API"""
    print("\nTesting cloud launcher Python API...")
    
    try:
        from cloud_training_launcher import CloudGPUTrainer
        
        # Test initialization
        launcher = CloudGPUTrainer()
        print("  ✓ CloudGPUTrainer can be instantiated")
        
        # Test GPU detection
        gpu_info = launcher.detect_gpu()
        print(f"  ✓ GPU detection works: {gpu_info.get('available', False)}")
        
        # Test cost estimation
        cost = launcher.estimate_training_cost(1.0)
        print(f"  ✓ Cost estimation works: ${cost['estimated_total_cost']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: Cloud launcher API error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gpu_utils_api():
    """Test GPU utilities Python API"""
    print("\nTesting GPU utilities Python API...")
    
    try:
        from cloud_gpu_utils import GPUMonitor, CloudOptimizer, CostTracker
        
        # Test GPU monitor
        monitor = GPUMonitor()
        metrics = monitor.get_gpu_metrics()
        print(f"  ✓ GPU monitoring works")
        
        # Test optimizer
        optimizer = CloudOptimizer()
        optimal = optimizer.get_optimal_batch_size(16.0)
        print(f"  ✓ Batch size optimization works: batch_size={optimal['batch_size']}")
        
        # Test cost tracker
        tracker = CostTracker(provider="local", cost_per_hour=0.0)
        tracker.start()
        current = tracker.get_current_cost()
        print(f"  ✓ Cost tracking works: ${current:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: GPU utils API error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_examples():
    """Test that provider example scripts exist"""
    print("\nTesting provider example scripts...")
    
    examples = [
        "cloud_examples/aws_training.sh",
        "cloud_examples/lambda_training.sh",
        "cloud_examples/runpod_training.sh"
    ]
    
    all_exist = True
    for example in examples:
        if os.path.exists(example):
            print(f"  ✓ {example} exists")
        else:
            print(f"  ✗ FAIL: {example} not found")
            all_exist = False
    
    return all_exist


def test_docker_files():
    """Test that Docker files exist"""
    print("\nTesting Docker configuration...")
    
    docker_files = [
        "docker/Dockerfile.gpu",
        "docker/docker-compose.gpu.yml",
        "docker/docker_helper.sh"
    ]
    
    all_exist = True
    for docker_file in docker_files:
        if os.path.exists(docker_file):
            print(f"  ✓ {docker_file} exists")
        else:
            print(f"  ✗ FAIL: {docker_file} not found")
            all_exist = False
    
    return all_exist


def test_documentation():
    """Test that documentation exists"""
    print("\nTesting documentation...")
    
    docs = [
        "CLOUD_GPU_TRAINING.md",
        "README.md"
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            # Check that cloud GPU info is in README
            if doc == "README.md":
                with open(doc, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "Cloud GPU Training" in content or "cloud_training_launcher" in content:
                        print(f"  ✓ {doc} contains cloud GPU information")
                    else:
                        print(f"  ⚠ WARNING: {doc} may not have cloud GPU info")
            else:
                print(f"  ✓ {doc} exists")
        else:
            print(f"  ✗ FAIL: {doc} not found")
            all_exist = False
    
    return all_exist


def test_quick_start_scripts():
    """Test that quick start scripts exist"""
    print("\nTesting quick start scripts...")
    
    scripts = [
        "quick_start_cloud_training.sh",
        "quick_start_cloud_training.ps1"
    ]
    
    all_exist = True
    for script in scripts:
        if os.path.exists(script):
            print(f"  ✓ {script} exists")
        else:
            print(f"  ✗ FAIL: {script} not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("=" * 70)
    print("Cloud GPU Training Setup - Integration Tests")
    print("=" * 70)
    
    tests = [
        ("Configuration Files", test_config_files),
        ("Cloud Launcher CLI", test_cloud_launcher),
        ("GPU Utilities CLI", test_gpu_utils),
        ("Cloud Launcher API", test_cloud_launcher_api),
        ("GPU Utilities API", test_gpu_utils_api),
        ("Provider Examples", test_provider_examples),
        ("Docker Files", test_docker_files),
        ("Documentation", test_documentation),
        ("Quick Start Scripts", test_quick_start_scripts),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! Cloud GPU training setup is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
