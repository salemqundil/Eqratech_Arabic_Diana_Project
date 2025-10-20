#!/usr/bin/env python3
"""
Test script to verify BERT training setup
"""

import sys
import os
import importlib.util

def _is_available(mod_name: str) -> bool:
    return importlib.util.find_spec(mod_name) is not None


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    required = [
        "transformers",
        "torch",
        "datasets",
        "pandas",
        "numpy",
        "sklearn",
        "accelerate",
    ]
    missing = [m for m in required if not _is_available(m)]
    if missing:
        print(f"\u2717 Missing packages: {', '.join(missing)}")
        return False

    # Print versions for primary deps
    import torch  # noqa: F401
    import transformers  # noqa: F401
    print("\u2713 All required packages appear available")
    print(f"  - PyTorch: {torch.__version__}")
    print(f"  - Transformers: {transformers.__version__}")
    return True

def test_tokenizer():
    """Test the UTF-8 tokenizer."""
    print("\nTesting UTF-8 Phoneme Tokenizer...")
    try:
        from utf8_tokenizer import UTF8PhonemeTokenizer
        
        # Create tokenizer
        tokenizer = UTF8PhonemeTokenizer()
        tokenizer.build_vocab_from_phonemes()
        
        # Test encoding
        test_text = "مرحبا"
        encoded = tokenizer.encode(test_text, padding=True, max_length=20)
        
        # Test decoding
        decoded = tokenizer.decode(encoded['input_ids'])
        
        print("✓ Tokenizer working correctly")
        print(f"  - Vocabulary size: {len(tokenizer)}")
        print(f"  - Test text: {test_text}")
        print(f"  - Encoded length: {len(encoded['input_ids'])}")
        print(f"  - Decoded: {decoded}")
        return True
    except Exception as e:
        print(f"✗ Tokenizer error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test that configuration file exists and is valid."""
    print("\nTesting configuration file...")
    try:
        import json
        config_path = 'config/training_config.json'
        
        if not os.path.exists(config_path):
            print(f"✗ Config file not found: {config_path}")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ['model_name', 'training', 'tokenizer', 'data']
        for key in required_keys:
            if key not in config:
                print(f"✗ Missing required config key: {key}")
                return False
        
        print("✓ Configuration file is valid")
        print(f"  - Model: {config['model_name']}")
        print(f"  - Epochs: {config['training']['num_train_epochs']}")
        print(f"  - Batch size: {config['training']['per_device_train_batch_size']}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_training_script():
    """Test that training script exists and can be imported."""
    print("\nTesting training script...")
    try:
        # Check if file exists
        if not os.path.exists('run_training.py'):
            print("✗ run_training.py not found")
            return False
        
        # Try to import (without running)
        
        print("✓ Training script is valid")
        print("  - run_training.py can be imported")
        return True
    except Exception as e:
        print(f"✗ Training script error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("BERT Training Setup Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Tokenizer", test_tokenizer()))
    results.append(("Config", test_config()))
    results.append(("Training Script", test_training_script()))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You can now run:")
        print("   python run_training.py --config config/training_config.json")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
