#!/usr/bin/env python3
"""
BERT Training Setup Script

This script automates the setup process for BERT model training on Arabic phoneme data.
It handles dependency installation, environment configuration, and initial validation.
"""

import sys
import os
import subprocess
import json
from pathlib import Path


class BERTTrainingSetup:
    """Setup manager for BERT training environment."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_dir = self.root_dir / 'config'
        self.config_file = self.config_dir / 'training_config.json'
        self.requirements_file = self.root_dir / 'requirements.txt'
        
        self.required_packages = [
            'transformers',
            'torch',
            'datasets',
            'pandas',
            'numpy',
            'scikit-learn',
            'tqdm',
            'accelerate'
        ]
        
        self.optional_packages = {
            'tensorboard': 'For training visualization'
        }
    
    def print_header(self, text):
        """Print formatted header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
    
    def print_step(self, step_num, total_steps, text):
        """Print formatted step."""
        print(f"\n[{step_num}/{total_steps}] {text}")
    
    def print_success(self, text):
        """Print success message."""
        print(f"✓ {text}")
    
    def print_warning(self, text):
        """Print warning message."""
        print(f"⚠ {text}")
    
    def print_error(self, text):
        """Print error message."""
        print(f"✗ {text}")
    
    def print_info(self, text):
        """Print info message."""
        print(f"ℹ {text}")
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error(f"Python 3.8+ is required. Current: {version.major}.{version.minor}")
            return False
        self.print_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_package_installed(self, package_name):
        """Check if a Python package is installed."""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False
    
    def install_dependencies(self, force=False):
        """Install required dependencies."""
        missing_packages = []
        
        # Check which packages are missing
        for package in self.required_packages:
            if not self.check_package_installed(package):
                missing_packages.append(package)
        
        if not missing_packages and not force:
            self.print_success("All required packages are already installed")
            return True
        
        # Install from requirements.txt
        if self.requirements_file.exists():
            self.print_info("Installing dependencies from requirements.txt...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '-r', 
                    str(self.requirements_file)
                ])
                self.print_success("Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install dependencies: {e}")
                return False
        else:
            # Install packages individually
            self.print_info(f"Installing {len(missing_packages)} missing packages...")
            for package in missing_packages:
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', package
                    ])
                    self.print_success(f"Installed {package}")
                except subprocess.CalledProcessError as e:
                    self.print_error(f"Failed to install {package}: {e}")
                    return False
            return True
    
    def verify_config(self):
        """Verify that configuration file exists and is valid."""
        if not self.config_file.exists():
            self.print_error(f"Configuration file not found: {self.config_file}")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check required keys
            required_keys = ['model_name', 'training', 'tokenizer', 'data']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                self.print_error(f"Missing required config keys: {', '.join(missing_keys)}")
                return False
            
            self.print_success("Configuration file is valid")
            self.print_info(f"  Model: {config['model_name']}")
            self.print_info(f"  Output: {config.get('output_dir', './output')}")
            self.print_info(f"  Epochs: {config['training']['num_train_epochs']}")
            self.print_info(f"  Batch size: {config['training']['per_device_train_batch_size']}")
            
            return True
        except json.JSONDecodeError as e:
            self.print_error(f"Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            self.print_error(f"Error reading config file: {e}")
            return False
    
    def verify_training_script(self):
        """Verify that the training script exists."""
        training_script = self.root_dir / 'run_training.py'
        if not training_script.exists():
            self.print_error("Training script not found: run_training.py")
            return False
        
        self.print_success("Training script found: run_training.py")
        return True
    
    def verify_tokenizer(self):
        """Verify that the tokenizer module exists and works."""
        tokenizer_file = self.root_dir / 'utf8_tokenizer.py'
        if not tokenizer_file.exists():
            self.print_error("Tokenizer module not found: utf8_tokenizer.py")
            return False
        
        try:
            from utf8_tokenizer import UTF8PhonemeTokenizer
            
            # Create a test tokenizer
            tokenizer = UTF8PhonemeTokenizer()
            tokenizer.build_vocab_from_phonemes()
            
            if tokenizer.vocab_size == 0:
                self.print_warning("Tokenizer has empty vocabulary")
                return False
            
            self.print_success(f"Tokenizer working (vocab size: {tokenizer.vocab_size})")
            return True
        except Exception as e:
            self.print_error(f"Tokenizer verification failed: {e}")
            return False
    
    def check_data_availability(self):
        """Check if training data is available."""
        # Look for phoneme data files
        possible_data_files = [
            'الفونيمات.csv',
            'Phonemes.csv',
            'full_multilayer_grammar.csv',
            'full_multilayer_grammar1.csv',
            'full_multilayer_grammar.xlsx'
        ]
        
        found_files = []
        for filename in possible_data_files:
            filepath = self.root_dir / filename
            if filepath.exists():
                found_files.append(filename)
        
        if found_files:
            self.print_success(f"Found {len(found_files)} data file(s)")
            for filename in found_files:
                self.print_info(f"  - {filename}")
            return True
        else:
            self.print_warning("No phoneme data files found")
            self.print_info("Training will use sample data")
            return True  # Not a critical error, training can use sample data
    
    def create_directories(self):
        """Create necessary directories for training."""
        directories = [
            'output',
            'logs',
            'data',
            'tokenizers'
        ]
        
        created = []
        for dirname in directories:
            dirpath = self.root_dir / dirname
            if not dirpath.exists():
                dirpath.mkdir(parents=True, exist_ok=True)
                created.append(dirname)
        
        if created:
            self.print_success(f"Created directories: {', '.join(created)}")
        else:
            self.print_success("All required directories already exist")
        
        return True
    
    def check_gpu_availability(self):
        """Check if GPU is available for training."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)
                self.print_success(f"GPU available: {gpu_name} ({gpu_count} device(s))")
                return True
            else:
                self.print_warning("No GPU detected - training will use CPU (slower)")
                return True
        except ImportError:
            self.print_warning("PyTorch not yet installed - GPU check skipped")
            return True
    
    def run_validation_test(self):
        """Run the test_setup.py validation script."""
        test_script = self.root_dir / 'test_setup.py'
        if not test_script.exists():
            self.print_warning("Test script not found: test_setup.py")
            return True  # Not critical
        
        try:
            self.print_info("Running validation tests...")
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True
            )
            
            # Print the output
            print(result.stdout)
            
            if result.returncode == 0:
                self.print_success("All validation tests passed")
                return True
            else:
                self.print_warning("Some validation tests failed")
                return True  # Not critical for setup
        except Exception as e:
            self.print_warning(f"Could not run validation tests: {e}")
            return True
    
    def print_next_steps(self):
        """Print instructions for next steps."""
        self.print_header("Setup Complete!")
        print("\n📝 Next Steps:\n")
        print("1. Review the configuration:")
        print("   config/training_config.json\n")
        print("2. (Optional) Test the setup:")
        print("   python test_setup.py\n")
        print("3. Start training:")
        print("   python run_training.py --config config/training_config.json\n")
        print("4. Monitor training logs:")
        print("   tensorboard --logdir ./logs\n")
        print("📚 Documentation:")
        print("   - See BERT_TRAINING_README.md for detailed information")
        print("   - Training output will be saved in: ./output/")
        print("   - Logs will be saved in: ./logs/\n")
    
    def run_setup(self, install_deps=True, force_install=False):
        """Run the complete setup process."""
        self.print_header("BERT Training Environment Setup")
        
        total_steps = 9
        current_step = 0
        
        # Step 1: Check Python version
        current_step += 1
        self.print_step(current_step, total_steps, "Checking Python version")
        if not self.check_python_version():
            return False
        
        # Step 2: Install dependencies
        if install_deps:
            current_step += 1
            self.print_step(current_step, total_steps, "Installing dependencies")
            if not self.install_dependencies(force=force_install):
                return False
        else:
            self.print_info("Skipping dependency installation (use --install to enable)")
        
        # Step 3: Verify configuration
        current_step += 1
        self.print_step(current_step, total_steps, "Verifying configuration")
        if not self.verify_config():
            return False
        
        # Step 4: Verify training script
        current_step += 1
        self.print_step(current_step, total_steps, "Verifying training script")
        if not self.verify_training_script():
            return False
        
        # Step 5: Verify tokenizer
        current_step += 1
        self.print_step(current_step, total_steps, "Verifying tokenizer")
        if not self.verify_tokenizer():
            return False
        
        # Step 6: Check data availability
        current_step += 1
        self.print_step(current_step, total_steps, "Checking data availability")
        self.check_data_availability()
        
        # Step 7: Create directories
        current_step += 1
        self.print_step(current_step, total_steps, "Creating directories")
        if not self.create_directories():
            return False
        
        # Step 8: Check GPU
        current_step += 1
        self.print_step(current_step, total_steps, "Checking GPU availability")
        self.check_gpu_availability()
        
        # Step 9: Run validation tests
        current_step += 1
        self.print_step(current_step, total_steps, "Running validation tests")
        self.run_validation_test()
        
        # Print next steps
        self.print_next_steps()
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Setup BERT training environment for Arabic phoneme processing'
    )
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install required dependencies'
    )
    parser.add_argument(
        '--force-install',
        action='store_true',
        help='Force reinstall all dependencies'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip validation tests'
    )
    
    args = parser.parse_args()
    
    # Create setup manager
    setup = BERTTrainingSetup()
    
    # Run setup
    try:
        success = setup.run_setup(
            install_deps=args.install or args.force_install,
            force_install=args.force_install
        )
        
        if success:
            sys.exit(0)
        else:
            print("\n❌ Setup failed. Please fix the errors above and try again.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
